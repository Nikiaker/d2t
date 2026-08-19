import json
import os
import re
import time
import io
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI

from tests.benchmark_reader.benchmark_reader import Benchmark, select_test_file


ZS_GEN_PORT = int(os.getenv("ZS_GEN_PORT", "2992"))
ZS_API_KEY = os.getenv("ZS_API_KEY", "AiIsMyLife25")
ZS_GEN_MODEL = os.getenv("ZS_GEN_MODEL", "RedHatAI/gemma-4-31B-it-NVFP4")
ZS_MAX_TOKENS = int(os.getenv("ZS_MAX_TOKENS", "256"))
ZS_TEMPERATURE = float(os.getenv("ZS_TEMPERATURE", "0.0"))
ZS_TIMEOUT_SECONDS = int(os.getenv("ZS_TIMEOUT_SECONDS", "600"))
ZS_POLL_INTERVAL = float(os.getenv("ZS_POLL_INTERVAL", "2"))
ZS_OUTPUT_DIR = Path(os.getenv("ZS_OUTPUT_DIR", "./"))

WEBNLG_BASE_PATH = os.getenv("WEBNLG_BASE_PATH", "./")
if not WEBNLG_BASE_PATH.endswith("/"):
    WEBNLG_BASE_PATH += "/"

WEBNLG_DOMAIN = os.getenv("WEBNLG_DOMAIN", "Airport")

SYSTEM_PROMPT = (
    "You are an expert data-to-text generator. Verbalize the given RDF triples "
    "into a single fluent, grammatically correct English sentence that conveys "
    "every fact and adds no extra information."
)

USER_PROMPT_TEMPLATE = (
    "Convert these RDF triples (subject | predicate | object) into one "
    "natural-language sentence.\n\nTriples:\n{triples}\n\n"
    "Output only the sentence."
)

gen_client = OpenAI(
    base_url=f"http://localhost:{ZS_GEN_PORT}/v1",
    api_key=ZS_API_KEY,
)


def make_key(triples: list[tuple[str, str, str]]) -> str:
    return json.dumps(triples, sort_keys=True)


def build_prompt(triples: list[tuple[str, str, str]]) -> str:
    lines = "\n".join(f"{s} | {p} | {o}" for s, p, o in triples)
    return USER_PROMPT_TEMPLATE.format(triples=lines)


def main():
    test_dir = WEBNLG_BASE_PATH + "test"
    test_file = select_test_file(
        test_dir, "rdf-to-text-generation-test-data-with-refs-en.xml"
    )

    test_benchmark = Benchmark()
    test_benchmark.fill_benchmark(test_file)

    category_entries = [
        e for e in test_benchmark.entries if e.category == WEBNLG_DOMAIN
    ]
    print(
        f"Loaded {len(category_entries)} test entries for domain '{WEBNLG_DOMAIN}'."
    )

    if not category_entries:
        print("No entries found, exiting.")
        return

    triples_by_key: dict[str, list[tuple[str, str, str]]] = {}
    prompts: list[str] = []
    keys_ordered: list[str] = []

    for entry in category_entries:
        cleaned = entry.get_clean_triples_tuple_list()
        key = make_key(cleaned)
        if key in triples_by_key:
            continue
        triples_by_key[key] = cleaned
        prompts.append(build_prompt(cleaned))
        keys_ordered.append(key)

    print(f"Sending {len(prompts)} batch requests...")

    requests_payload: list[dict] = []
    for i, prompt in enumerate(prompts):
        requests_payload.append(
            {
                "custom_id": f"zs-gen-{i}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": ZS_GEN_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": ZS_MAX_TOKENS,
                    "temperature": ZS_TEMPERATURE,
                },
            }
        )

    jsonl_content = "\n".join(json.dumps(r) for r in requests_payload) + "\n"
    batch_input_file = io.BytesIO(jsonl_content.encode("utf-8"))
    batch_input_file.name = "zs_batch.jsonl"

    uploaded = gen_client.files.create(file=batch_input_file, purpose="batch")
    batch = gen_client.batches.create(
        input_file_id=uploaded.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )

    start = time.time()
    while True:
        batch = gen_client.batches.retrieve(batch.id)
        if batch.status == "completed":
            break
        if batch.status in {"failed", "expired", "cancelled"}:
            raise RuntimeError(f"Batch finished with status: {batch.status}")
        if (time.time() - start) > ZS_TIMEOUT_SECONDS:
            raise TimeoutError(
                f"Batch timed out after {ZS_TIMEOUT_SECONDS}s (status {batch.status})"
            )
        time.sleep(ZS_POLL_INTERVAL)

    if not batch.output_file_id:
        raise RuntimeError("Batch completed but no output_file_id returned")

    output_text = gen_client.files.content(batch.output_file_id).text

    responses_by_index: dict[int, str] = {}
    for line in output_text.splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        mid = re.search(r"zs-gen-(\d+)$", row.get("custom_id", ""))
        if not mid:
            continue
        index = int(mid.group(1))
        body = (row.get("response") or {}).get("body") or {}
        choices = body.get("choices") or []
        content = ""
        if choices:
            msg = choices[0].get("message") or {}
            content = msg.get("content") or ""
        responses_by_index[index] = content

    generated: dict[str, str] = {}
    for idx, key in enumerate(keys_ordered):
        generated[key] = responses_by_index.get(idx, "").strip()

    best_dir = ZS_OUTPUT_DIR / "openevolve_output" / "best"
    best_dir.mkdir(parents=True, exist_ok=True)

    json_path = best_dir / "generated_texts.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(generated, f, indent=2, ensure_ascii=False)
    print(f"Written {len(generated)} entries to {json_path}")

    shim_path = best_dir / "best_program.py"
    shim_source = (
        'import json\n'
        'import os\n\n'
        'from dataclasses import dataclass\n\n'
        '@dataclass\n'
        'class Triple:\n'
        '    subject: str\n'
        '    predicate: str\n'
        '    object: str\n\n'
        f'_DATA = json.loads(r"""'
        f'{json.dumps(generated, ensure_ascii=False)}""")\n\n'
        'def predict(triples: list[Triple]) -> str:\n'
        '    key = json.dumps([(t.subject, t.predicate, t.object) for t in triples], sort_keys=True)\n'
        '    return _DATA.get(key, "")\n'
    )
    with open(shim_path, "w", encoding="utf-8") as f:
        f.write(shim_source)
    print(f"Written shim to {shim_path}")


if __name__ == "__main__":
    main()
