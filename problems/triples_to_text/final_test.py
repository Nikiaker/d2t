import os
from openai import OpenAI
from problems.triples_to_text.evaluator import ThemisEvaluation, fetch_completion, parse_themis_response
from tests.benchmark_reader.benchmark_reader import Benchmark, select_test_file
from dataclasses import dataclass
from initial_program import Triple
import concurrent.futures
import importlib.util
import evaluate as ev
import sys
import numpy as np
from tests.senlen import Senlen
import yaml

CONFIG_PATH = os.getenv("CONFIG_PATH", "config_remote.yaml")

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

THEMIS_NAME = config['evaluator']['themis_name']
THEMIS_API_BASE = config['evaluator']['themis_api_base']
THEMIS_API_KEY = config['evaluator']['themis_api_key']

themis_client = OpenAI(base_url=THEMIS_API_BASE, api_key=THEMIS_API_KEY)

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

test_dir = WEBNLG_BASE_PATH + "test"
test_file = select_test_file(test_dir, "rdf-to-text-generation-test-data-with-refs-en.xml")

test_benchmark = Benchmark()
test_benchmark.fill_benchmark(test_file)

entries = test_benchmark.entries
category_entries  = [e for e in entries if e.category == WEBNLG_DOMAIN]
category_test_sentences = [TestSentence([TestTriple(*triple) for triple in e.get_clean_triples_tuple_list()], e.get_lexs_list()) for e in category_entries]

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
themis_scores: list[ThemisEvaluation] = []

themis_chat_messages: list[str] = []

for test_sentence in category_test_sentences:
    triples = [Triple(test_triple.subject, test_triple.predicate, test_triple.object) for test_triple in test_sentence.triples]

    # Run with timeout
    result = run_with_timeout(program.predict, args=(triples,), timeout_seconds=5)

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
        bleu_results = bleu.compute(predictions=[generated_text], references=[test_sentence.example_texts])
        bleu_score = float(bleu_results['bleu'])
        bleu_scores.append(bleu_score)

        # Calculate METEOR score
        meteor_results = meteor.compute(predictions=[generated_text], references=[test_sentence.example_texts])
        meteor_score = float(meteor_results['meteor'])
        meteor_scores.append(meteor_score)

        # Calculate SENLEN score
        senlen_results = senlen.compute(predictions=[generated_text], references=[test_sentence.example_texts])
        senlen_score = float(senlen_results['senlen'])
        senlen_scores.append(senlen_score)

        # Calculate BLEURT score
        bleurt_individual_scores = []
        for ref in test_sentence.example_texts:
            bleurt_results = bleurt.compute(predictions=[generated_text], references=[ref])
            bleurt_individual_scores.append(float(bleurt_results['scores'][0]))
        bleurt_score = float(np.mean(bleurt_individual_scores))
        bleurt_scores.append(bleurt_score)

        # Calculate Themis score
        if themis_client:
            source = "\n".join([f"{triple.subject}, {triple.predicate}, {triple.object}" for triple in triples])
            target = generated_text
            chat_message = f"###Instruction###\nPlease act as an impartial and helpful evaluator for natural language generation (NLG), and the audience is an expert in the field.\nYour task is to evaluate the quality of text similarity strictly based on the given evaluation criterion.\nBegin the evaluation by providing your analysis concisely and accurately, and then on the next line, start with \"Rating:\" followed by your rating on a Likert scale from 1 to 5 (higher means better).\nYou MUST keep to the strict boundaries of the evaluation criterion and focus solely on the issues and errors involved; otherwise, you will be penalized.\nMake sure you read and understand these instructions, as well as the following evaluation criterion and example content, carefully.\n\n###Evaluation Criterion###\nAccuaracy and number of sentences: The generated text must accurately reference the triples. There cannot be any extra information that was not present in the triples. If possible there must be just one complex sentence instead of multiple sentences.\n\n###Example###\nThe triples in the form (subject, predicate, object):\n{source}\n\nThe generated text:\n{target}\n\n###Your Evaluation###"

            themis_chat_messages.append(chat_message)

# Batch themis
if themis_client and themis_chat_messages:
    results = fetch_completion(themis_chat_messages)
    for i, result_content in enumerate(results):
        review, rating = parse_themis_response(result_content)
        themis_scores.append(ThemisEvaluation(review=review, rating=rating))

avg_bleu_score = float(np.mean(bleu_scores))
avg_meteor_score = float(np.mean(meteor_scores))
avg_senlen_score = float(np.mean(senlen_scores))
avg_bleurt_score = float(np.mean(bleurt_scores))
avg_themis_score = float(np.mean([eval.rating for eval in themis_scores])) if themis_scores else 0.0

print(f"Final Evaluation Results for domain '{WEBNLG_DOMAIN}':")
print(f"Average BLEU Score: {avg_bleu_score}")
print(f"Average METEOR Score: {avg_meteor_score}")
print(f"Average SENLEN Score: {avg_senlen_score}")
print(f"Average BLEURT Score: {avg_bleurt_score}")
print(f"Average Themis Score: {avg_themis_score}")

output_path = "./scores.txt"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(f"Final Evaluation Results for domain '{WEBNLG_DOMAIN}':\n")
    f.write(f"Average BLEU Score: {avg_bleu_score}\n")
    f.write(f"Average METEOR Score: {avg_meteor_score}\n")
    f.write(f"Average SENLEN Score: {avg_senlen_score}\n")
    f.write(f"Average BLEURT Score: {avg_bleurt_score}\n")
    f.write(f"Average Themis Score: {avg_themis_score}\n")