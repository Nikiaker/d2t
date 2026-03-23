# Tripler

Python CLI to:

1. Generate semantic triples `(subject, predicate, object)` from JSON instances using an OpenAI-compatible LLM endpoint (local vLLM).
2. Extract unique predicates.
3. Compare each predicate pair with an LLM for semantic equivalence.
4. Group equivalent predicates.
5. Replace each group with its first predicate as canonical.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py \
  --input ../quintd/data/quintd-1/data/openweather/dev.json \
  --output ./triples_out.json \
  --model your-vllm-model-name \
  --base-url http://localhost:8000/v1 \
  --api-key local-key
```

## Batch Wrapper for vLLM (no `/v1/files` / `/v1/batches`)

If your vLLM server does not implement OpenAI Files/Batch endpoints, run the local wrapper:

```bash
python batch_wrapper_server.py \
  --upstream-base-url http://localhost:8001 \
  --host 0.0.0.0 \
  --port 8010 \
  --storage-dir .batch_wrapper_data
```

Then point `app.py` to the wrapper:

```bash
python app.py \
  --input input_data.json \
  --output output_data.json \
  --model vllm-model-1 \
  --base-url http://localhost:8010/v1 \
  --api-key none
```

The wrapper forwards each batch request line to upstream `POST /v1/chat/completions`, stores uploaded files locally, and exposes OpenAI-compatible:

- `POST /v1/files`
- `GET /v1/files/{file_id}`
- `GET /v1/files/{file_id}/content`
- `POST /v1/batches`
- `GET /v1/batches/{batch_id}`

## Notes

- The app expects one of these JSON shapes:
  - `{ "forecasts": [ { "list": [...] } ] }` (weather example)
  - `{ "list": [...] }`
  - `[ ... ]`
- For weather, each forecast element in each city list is treated as one instance and receives one extraction prompt.
- You can override prompts:
  - `--extract-prompt-file path/to/extract_prompt.txt`
  - `--equivalence-prompt-file path/to/equivalence_prompt.txt`

## Output

The output JSON contains:

- `triples_by_instance`: extracted triples per instance.
- `predicate_groups`: grouped equivalent predicates.
- `pairwise_predicate_comparisons`: LLM decisions for each predicate pair.
- `normalized_triples`: final triples after predicate standardization.
