import os
import json
import csv
from openai import OpenAI
from evaluator import ThemisEvaluation, fetch_completion, parse_themis_response
from tests.benchmark_reader.benchmark_reader import Benchmark, select_test_file
from dataclasses import dataclass
from initial_program import Triple
import concurrent.futures
import importlib.util
import evaluate as ev
import sys
import numpy as np
from tests.senlen import Senlen
from pathlib import Path

LLM_JUDGES = os.getenv(
    "LLM_JUDGES",
    "[{\"name\": \"themis\", \"base_url\": \"http://localhost:8010/v1\", \"api_key\": \"AiIsMyLife25\"}]",
)
judges_configs = json.loads(LLM_JUDGES)
judges_structured = {str(config["name"]): bool(config.get("structured", False)) for config in judges_configs}

try:
    judges_clients = {str(config['name']): OpenAI(base_url=config['base_url'], api_key=config['api_key']) for config in judges_configs}
except Exception:
    print("Error initializing judges clients. Themis evaluation will be skipped.")
    judges_clients: dict[str, OpenAI] = {}

def run_with_timeout(func, args=(), kwargs={}, timeout_seconds=5):
    """
    Run a function with a timeout using concurrent.futures

    Args:
        func: Function to run
        args: Arguments to pass to the function
        kwargs: Keyword arguments to pass to the function
        timeout_seconds: Timeout in seconds

    Returns:
        Result of the function or raises TimeoutError
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            result = future.result(timeout=timeout_seconds)
            return result
        except concurrent.futures.TimeoutError:
            raise TimeoutError(f"Function timed out after {timeout_seconds} seconds")

@dataclass
class TestTriple:
    subject: str
    predicate: str
    object: str

    def __str__(self):
        return f"({self.subject} | {self.predicate} | {self.object})"

@dataclass
class TestSentence:
    triples: list[TestTriple]
    example_texts: list[str]

WEBNLG_BASE_PATH = os.getenv(
    "WEBNLG_BASE_PATH",
    "./",
)
if not WEBNLG_BASE_PATH.endswith("/"):
    WEBNLG_BASE_PATH += "/"

WEBNLG_DOMAIN = os.getenv(
    "WEBNLG_DOMAIN",
    "Airport",
)

BEST_PROGRAM_PATH = os.getenv(
    "BEST_PROGRAM_PATH",
    "./current_program.py",
)


def build_judge_prompt(
    *,
    criterion: str,
    data_label: str,
    data_value: str,
    generated_text: str,
    structured: bool,
    rating_description: str,
) -> str:
    if structured:
        output_format = (
            'Respond with a single JSON object with keys "review" and "rating". '
            'The "rating" field must be numeric. Do not wrap the JSON in markdown fences or add any other text.'
        )
        data_header = "Data to evaluate"
    else:
        output_format = (
            f"{rating_description} "
            "You MUST keep to the strict boundaries of the evaluation criterion and focus solely on the issues and errors involved; otherwise, you will be penalized."
        )
        data_header = "Example"

    return (
        "###Instruction###\n"
        "Please act as an impartial and helpful evaluator for natural language generation (NLG), and the audience is an expert in the field.\n"
        "Your task is to evaluate the quality of text similarity strictly based on the given evaluation criterion.\n"
        "Begin the evaluation by providing your analysis concisely and accurately, and then follow the required output format.\n"
        f"{output_format}\n"
        "Make sure you read and understand these instructions, as well as the following evaluation criterion and example content, carefully.\n\n"
        f"###Evaluation Criterion###\n{criterion}\n\n"
        f"###{data_header}###\n{data_label}:\n{data_value}\n\n"
        f"The generated text:\n{generated_text}\n\n"
        "###Your Evaluation###"
    )


def format_triples_for_csv(triples: list[Triple]) -> str:
    # Format as: (sub,pred,obj);(sub2,pred2,obj2)
    parts = []
    for t in triples:
        subj = t.subject.replace(';', ',')
        pred = t.predicate.replace(';', ',')
        obj = t.object.replace(';', ',')
        parts.append(f"({subj},{pred},{obj})")
    return ";".join(parts)


def format_references_for_csv(references: list[str]) -> str:
    # Format as: "Ref text1";"Ref text2"
    parts = []
    for r in references:
        safe = r.replace('"', '""')
        parts.append(f'"{safe}"')
    return ";".join(parts)

test_dir = WEBNLG_BASE_PATH + "test"
test_file = select_test_file(test_dir, "rdf-to-text-generation-test-data-with-refs-en.xml")

test_benchmark = Benchmark()
test_benchmark.fill_benchmark(test_file)

entries = test_benchmark.entries
category_entries  = [e for e in entries if e.category == WEBNLG_DOMAIN]
category_test_sentences = [TestSentence([TestTriple(*triple) for triple in e.get_clean_triples_tuple_list()], e.get_lexs_list()) for e in category_entries]
print(f"Loaded {len(category_test_sentences)} test sentences for domain '{WEBNLG_DOMAIN}'.")

spec = importlib.util.spec_from_file_location("program", BEST_PROGRAM_PATH)
program = importlib.util.module_from_spec(spec)
spec.loader.exec_module(program)

bleu = ev.load("bleu")
meteor = ev.load("meteor")
senlen = Senlen()
bleurt = ev.load("bleurt", module_type="metric")

bleu_scores: list[float] = []
meteor_scores: list[float] = []
senlen_scores: list[float] = []
bleurt_scores: list[float] = []
themis_scores: dict[str, list[ThemisEvaluation]] = {}
gramatic_scores: list[ThemisEvaluation] = []
ommisions_scores: list[ThemisEvaluation] = []
additions_scores: list[ThemisEvaluation] = []
generated_rows: list[dict[str, str]] = []

themis_chat_messages_by_judge: dict[str, list[str]] = {judge_name: [] for judge_name in judges_clients}
gramatic_chat_messages: list[str] = []
ommisions_chat_messages: list[str] = []
additions_chat_messages: list[str] = []

iteration = 0

print("Starting evaluation loop...")
for test_sentence in category_test_sentences:
    #print(f"Current iteration: {iteration}/{len(category_test_sentences)}")
    #print(f"Test sentence triples: {[str(triple) for triple in test_sentence.triples]}")
    triples = [Triple(test_triple.subject, test_triple.predicate, test_triple.object) for test_triple in test_sentence.triples]

    # Run with timeout
    result = run_with_timeout(program.predict, args=(triples,), timeout_seconds=5)

    #print(f"Generated text: {result}")

    # Handle different result formats
    if isinstance(result, str):
        generated_text = result
    else:
        sys.exit(1)

    if generated_text.strip() == "":
        bleu_results = 0.0
        meteor_results = 0.0
        senlen_results = 0.0
        bleurt_score = 0.0
    else:
        # Calculate BLEU score with weights
        #print("Calulating BLEU score...")
        bleu_results = bleu.compute(predictions=[generated_text], references=[test_sentence.example_texts])
        bleu_score = float(bleu_results['bleu'])
        bleu_scores.append(bleu_score)

        # Calculate METEOR score
        #print("Calculating METEOR score...")
        meteor_results = meteor.compute(predictions=[generated_text], references=[test_sentence.example_texts])
        meteor_score = float(meteor_results['meteor'])
        meteor_scores.append(meteor_score)

        # Calculate SENLEN score
        #print("Calculating SENLEN score...")
        senlen_results = senlen.compute(predictions=[generated_text], references=[test_sentence.example_texts])
        senlen_score = float(senlen_results['senlen'])
        senlen_scores.append(senlen_score)

        # Calculate BLEURT score
        #print("Calculating BLEURT score...")
        bleurt_individual_scores = []
        for ref in test_sentence.example_texts:
            bleurt_results = bleurt.compute(predictions=[generated_text], references=[ref])
            bleurt_individual_scores.append(float(bleurt_results['scores'][0]))
        bleurt_score = float(np.mean(bleurt_individual_scores))
        bleurt_scores.append(bleurt_score)

        # Calculate Themis score
        if any(judges_clients.values()):
            source = "\n".join([f"{triple.subject}, {triple.predicate}, {triple.object}" for triple in triples])
            target = generated_text
            for judge_name in judges_clients:
                themis_chat_messages_by_judge[judge_name].append(
                    build_judge_prompt(
                        criterion="Accuaracy and number of sentences: The generated text must accurately reference the triples. There cannot be any extra information that was not present in the triples. If possible there must be just one complex sentence instead of multiple sentences.",
                        data_label="The triples in the form (subject, predicate, object)",
                        data_value=source,
                        generated_text=target,
                        structured=judges_structured.get(judge_name, False),
                        rating_description='Return a rating from 1 to 5. On structured runs, the rating must be stored in the JSON field named "rating".',
                    )
                )

            first_judge_name = next(iter(judges_clients.keys()))
            first_judge_structured = judges_structured.get(first_judge_name, False)

            gramatic_chat_messages.append(
                build_judge_prompt(
                    criterion="Grammatical correctness: You should assess the grammatical correctness of the resulting text. Do not take any other factors into account. Do not make assumptions or consider external knowledge not present in the provided context. Identify only errors relating to the grammaticality of the text. Do not consider aspects such as fluency, omissions or hallucinations.",
                    data_label="The generated text",
                    data_value=target,
                    generated_text=target,
                    structured=first_judge_structured,
                    rating_description='Return 1 if the text is grammatically correct and 0 if it is not. On structured runs, the rating must be stored in the JSON field named "rating".',
                )
            )

            ommisions_chat_messages.append(
                build_judge_prompt(
                    criterion="Omissions: You should assess the omissions in the resulting text; in other words, you should check whether any of the input triples were not verbalised. You can perform the task by iterating over the input triples and checking if it is present in the output. Do not take any other factors into account. Do not make assumptions or consider external knowledge not present in the provided context. Identify only errors relating to the fluency of the text. Do not consider aspects such as grammaticality, fluency or the addition of new facts (hallucinations).",
                    data_label="The triples in the form (subject, predicate, object)",
                    data_value=source,
                    generated_text=target,
                    structured=first_judge_structured,
                    rating_description='Return 0 if there are no omissions and 1 if there are. On structured runs, the rating must be stored in the JSON field named "rating".',
                )
            )

            additions_chat_messages.append(
                build_judge_prompt(
                    criterion="Additions: You should assess the addition of new facts in the resulting text which were not present in the input triples . You can perform the task by carefully reading the text and checking if the facts mentioned are present in the input triples. Do not take any other factors into account. Do not make assumptions or consider external knowledge not present in the provided context. Identify only errors relating to the fluency of the text. Do not consider aspects such as grammaticality, fluency or the omissions of input triples.",
                    data_label="The triples in the form (subject, predicate, object)",
                    data_value=source,
                    generated_text=target,
                    structured=first_judge_structured,
                    rating_description='Return 0 if there are no additions and 1 if there are. On structured runs, the rating must be stored in the JSON field named "rating".',
                )
            )

        generated_rows.append(
            {
                "input triples": format_triples_for_csv(triples),
                "reference text": format_references_for_csv(test_sentence.example_texts),
                "generated text": generated_text,
            }
        )

        iteration += 1

print("Done generating outputs")

# Batch score
for judge_name, judge_client in judges_clients.items():
    print(f"Running {judge_name} evaluation for {len(themis_chat_messages_by_judge.get(judge_name, []))} examples...")
    results = fetch_completion(
        themis_chat_messages_by_judge.get(judge_name, []),
        judge_client,
        structured=judges_structured.get(judge_name, False),
    )
    themis_scores[judge_name] = []
    for i, result_content in enumerate(results):
        review, rating = parse_themis_response(result_content)
        themis_scores[judge_name].append(ThemisEvaluation(review=review, rating=rating))

# Batch gramatic
if any(judges_clients.values()) and gramatic_chat_messages:
    judge_client = list(judges_clients.values())[0]  # Get the first available judge client
    first_judge_name = next(iter(judges_clients.keys()))
    print(f"Running Grammaticality evaluation for {len(gramatic_chat_messages)} examples...")
    results = fetch_completion(
        gramatic_chat_messages,
        judge_client,
        structured=judges_structured.get(first_judge_name, False),
    )
    for i, result_content in enumerate(results):
        review, rating = parse_themis_response(result_content)
        gramatic_scores.append(ThemisEvaluation(review=review, rating=rating))

# Batch ommisions
if any(judges_clients.values()) and ommisions_chat_messages:
    judge_client = list(judges_clients.values())[0]  # Get the first available judge client
    first_judge_name = next(iter(judges_clients.keys()))
    print(f"Running Omissions evaluation for {len(ommisions_chat_messages)} examples...")
    results = fetch_completion(
        ommisions_chat_messages,
        judge_client,
        structured=judges_structured.get(first_judge_name, False),
    )
    for i, result_content in enumerate(results):
        review, rating = parse_themis_response(result_content)
        ommisions_scores.append(ThemisEvaluation(review=review, rating=rating))

# Batch additions
if any(judges_clients.values()) and additions_chat_messages:
    judge_client = list(judges_clients.values())[0]  # Get the first available judge client
    first_judge_name = next(iter(judges_clients.keys()))
    print(f"Running Additions evaluation for {len(additions_chat_messages)} examples...")
    results = fetch_completion(
        additions_chat_messages,
        judge_client,
        structured=judges_structured.get(first_judge_name, False),
    )
    for i, result_content in enumerate(results):
        review, rating = parse_themis_response(result_content)
        additions_scores.append(ThemisEvaluation(review=review, rating=rating))

avg_bleu_score = float(np.mean(bleu_scores))
avg_meteor_score = float(np.mean(meteor_scores))
avg_senlen_score = float(np.mean(senlen_scores))
avg_bleurt_score = float(np.mean(bleurt_scores))

avg_themis_score = {
    judge_name: float(np.mean([evaluation.rating for evaluation in evaluations])) / 5.0
    if evaluations else 0.0
    for judge_name, evaluations in themis_scores.items()
}

avg_gramatic_score = float(np.mean([eval.rating for eval in gramatic_scores])) if gramatic_scores else 0.0
avg_ommisions_score = float(np.mean([eval.rating for eval in ommisions_scores])) if ommisions_scores else 0.0
avg_additions_score = float(np.mean([eval.rating for eval in additions_scores])) if additions_scores else 0.0

print(f"Final Evaluation Results for domain '{WEBNLG_DOMAIN}':")
print(f"Average BLEU Score: {avg_bleu_score}")
print(f"Average METEOR Score: {avg_meteor_score}")
print(f"Average SENLEN Score: {avg_senlen_score}")
print(f"Average BLEURT Score: {avg_bleurt_score}")
for judge_name, score in avg_themis_score.items():
    print(f"Average Judge Score ({judge_name}): {score}")
print(f"Average Grammaticality Score: {avg_gramatic_score}")
print(f"Average Omissions Score: {avg_ommisions_score}")
print(f"Average Additions Score: {avg_additions_score}")


output_path = "./scores.json"
generated_text_output_path = Path("./generated_text.csv")
results_payload = {
    "domain": WEBNLG_DOMAIN,
    "metrics": {
        "bleu": avg_bleu_score,
        "meteor": avg_meteor_score,
        "senlen": avg_senlen_score,
        "bleurt": avg_bleurt_score,
        **{judge_name: score for judge_name, score in avg_themis_score.items()},
        "gramatic": avg_gramatic_score,
        "ommisions": avg_ommisions_score,
        "additions": avg_additions_score,
    },
}

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results_payload, f, indent=2, ensure_ascii=False)
    f.write("\n")

with generated_text_output_path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["input triples", "reference text", "generated text"],
        extrasaction="ignore",
    )
    writer.writeheader()
    for row in generated_rows:
        writer.writerow(row)