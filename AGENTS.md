# AGENTS.md

This repository is the code workspace for a **master thesis / research article** on
LLM-driven data-to-text generation. It is a research orchestration repo, not a
single application: it combines an evolutionary code-optimization framework
(OpenEvolve, vendored as a submodule), OpenEvolve "problems" that are the actual
experiments, and tooling for triples extraction and dataset handling. Most heavy
runs happen on SLURM GPU clusters.

## Layout

- `openevolve/` — **git submodule** (fork of OpenEvolve). The evolutionary coding
  agent. See `openevolve/CLAUDE.md` for its architecture, commands, and patterns;
  do not duplicate that guidance here.
- `problems/` — OpenEvolve problems (experiments). Each has `initial_program.py`,
  `evaluator.py`, `config*.yaml`, `start_evolution.sh`, `templates/`:
  - `triples_to_text/` — the main thesis experiment. Evolves `predict(triples)`
    to verbalize RDF triples; scored against the WebNLG corpus (BLEU/METEOR) plus
    an optional Themis LLM judge. Many variants live in `configs/<experiment>/`,
    each with its own `config_remote.yaml` + SLURM `batch_template.sh`.
  - `function_minimization/`, `circle_packing_with_artifacts/` — reference/
    reproduction problems (the latter targets AlphaEvolve's n=26 packing).
- `quintd/` — data-to-text dataset collection tool (vendored fork; Python 3.10,
  own `requirements.txt`). Source of JSON inputs used downstream.
- `tripler/` — CLI for extracting/normalizing semantic triples from JSON via a
  vLLM/OpenAI-compatible endpoint. `batch_wrapper_server.py` emulates OpenAI
  `/v1/files` + `/v1/batches` on top of vLLM chat completions.
- `jinja/` — vLLM chat templates (`gpt-oss.jinja`, `llama.jinja`).
- `scripts/` — mock LLM servers and small helpers.
- `.conda/` — SLURM batch scripts, the `openevolve-env` conda env
  (`environment.yml`, Python 3.13), vLLM health-check (`test-response.py`),
  litellm proxy config.
- `.nix/` — alternative Nix dev shell (`shell.nix`) that builds a `.venv` and
  wires up `PYTHONPATH`/`WEBNLG_BASE_PATH`/`CONFIG_PATH` for local work.
- `.docker/` — vLLM Docker build/run scripts.
- `notes/` — dated research notes.

## Data flow

For the text-generation line of work, components chain as:

```
quintd/  →  JSON instances  →  tripler/  →  normalized triples
                                      ↓
            problems/triples_to_text/initial_program.py::predict(triples)
                                      ↓
                            natural language text
                                      ↑
            scored against WebNLG corpus (BLEU/METEOR) + Themis LLM judge
```

- `quintd/` acquires ad-hoc JSON datasets (weather, products, hockey, OWID,
  Wikidata) used as input instances.
- `tripler/` extracts `(subject, predicate, object)` triples from those JSON
  instances via an LLM and normalizes predicates (groups synonyms to a
  canonical member).
- `problems/triples_to_text/` evolves `predict(triples)` to verbalize those
  triples. Its evaluator does **not** consume tripler's output directly; it
  loads the WebNLG corpus (`train/` + `dev/`) for reference-based scoring and
  uses WebNLG category filtering via `WEBNLG_DOMAIN`.
- `openevolve/` is the engine that mutates `predict()` inside the
  `# EVOLVE-BLOCK-*` region; its LLM calls hit vLLM endpoints started by the
  SLURM batch templates.

The other two problems are independent of this pipeline:
`function_minimization/` and `circle_packing_with_artifacts/` evolve standalone
algorithmic code with their own evaluators and need neither quintd nor tripler.

## Cluster hardware

Experiments run on **PLGrid Athena** (Academic Computer Centre Cyfronet AGH), an
HPE Cray EX4000 system with Infiniband HDR (4×200 Gb/s per node) and a Lustre
filesystem backed by NVMe flash.

**Per-node specs:** 48 nodes, each with 2× AMD EPYC 7742 64-core (128 cores
total), 1 TB RAM, and 8× NVIDIA A100-SXM4-40GB GPUs (40 GB VRAM each). Total
cluster: 6144 CPU cores, 384 A100 GPUs, ~7.7 PFlops theoretical.

**Partition and account:**
- SLURM partition: `plgrid-gpu-a100`
- Account: `plgnarnlg-gpu-a100`
- Walltime limit: 48 hours

**Proportional per-GPU resources:** 128 GB RAM and 16 CPU cores. Batch scripts
request `--cpus-per-task=16` and 64–128 GB of RAM accordingly. Jobs use 1–5 GPUs
from a single node, pinned to specific devices via `CUDA_VISIBLE_DEVICES`.
Multi-GPU jobs can leverage tensor parallelism across GPUs on the same node over
the Infiniband fabric.

## Running an experiment

From inside a problem directory:
```bash
cd problems/<name>
python ../../openevolve/openevolve-run.py initial_program.py evaluator.py --config config.yaml
```
Resume from the latest checkpoint by adding `--checkpoint <checkpoint_dir>` and
`--output <out_dir>`. See each problem's `start_evolution.sh` for the canonical
invocation.

For `triples_to_text` specifically:
- The real experiment uses `config_remote.yaml` and `evaluator_themis.py`, **not**
  `config.yaml` (the latter is only a tiny local smoke-test config).
- The evaluator reads its config from the `CONFIG_PATH` env var (defaults to
  `config_remote.yaml`) and the WebNLG corpus from `WEBNLG_BASE_PATH`.
- End-to-end runs are launched via SLURM: `sbatch configs/<exp>/batch_template.sh`.
  These templates contain `{port_0}`, `{port_1}`, `{domain}`, `{evolution_config}`
  placeholders that `prepare_evolution.py` substitutes.
- Scoring/plotting helpers: `final_test.py`, `collect_scores_to_csv.py`,
  `run_final_test_for_configs.py`, `plot_results.py`.

## Environment requirements (easy to miss)

- `PYTHONPATH` must include `openevolve/`,
  `problems/triples_to_text/tests/benchmark_reader/`, and
  `problems/triples_to_text/` — the evaluator imports `from initial_program
  import Triple` and the benchmark reader by name. The Nix shell and the SLURM
  templates set this; a plain shell does not.
- Required env vars for `triples_to_text`: `WEBNLG_BASE_PATH` (points at
  `tests/webnlg/release_v3.0/en/` with `train/` and `dev/`), `WEBNLG_DOMAIN`
  (e.g. `Airport`), `CONFIG_PATH`, `LLM_JUDGES` (JSON list of judge models),
  and `D2TPATH` (repo root) on the cluster.
- Two conda envs on the cluster: `vllm-env` (serves models) and
  `openevolve-env` (runs experiments). SLURM scripts `module load CUDA/12.8.0`
  and `Miniconda3` on PLGrid.
- vLLM serves models on OpenAI-compatible ports; vLLM lacks `/v1/files` and
  `/v1/batches`, so `tripler/batch_wrapper_server.py` must be started in front
  of it for batch flows.

## OpenEvolve toolchain (in `openevolve/`)

These commands are scoped to the `openevolve/` subdirectory:
```bash
pip install -e ".[dev]"     # or: make install
make test                   # unit tests (unittest; no LLM needed)
make test-integration       # needs optillm server on :8000
make lint                   # black formatting
```
Python >=3.10. Pre-commit runs `isort` (black profile) + `black`.

## Conventions / gotchas

- Code an OpenEvolve problem evolves must be wrapped in:
  ```python
  # EVOLVE-BLOCK-START
  # ...code to evolve...
  # EVOLVE-BLOCK-END
  ```
- The `triples_to_text` evaluator enforces per-call timeouts via `os.fork` +
  `pickle` so an infinite loop in evolved code returns `combined_score=0`
  instead of the framework's misleading `0.5` fallback. Do not "simplify" this
  to a thread-based timeout.
- `island_unique_models: true` in `config_remote.yaml` pins each island to one
  LLM; island indices in the `llm.models` list must match `num_islands`.
- Config files under `problems/triples_to_text/configs/*/config_remote.yaml`
  contain real-looking API keys and private endpoint URLs (e.g.
  `llm.hpc.psnc.pl`). Do not echo them into commits, issues, or PRs, and do not
  rotate/republish them casually — other batch scripts depend on them.
- Output dirs (`openevolve_output*`, `results/`, `outputs/`, `all_programs/`)
  are experiment artifacts and are mostly gitignored; do not rely on them being
  present on a fresh checkout.
- This is research code for a thesis/article: prefer reproducibility of an
  experiment config over "clean" refactors. Don't rename or renumber
  `configs/<experiment>/` directories — they are referenced by name in notes,
  results CSVs, and SLURM outputs.