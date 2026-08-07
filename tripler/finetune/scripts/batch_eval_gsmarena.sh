#!/bin/bash
#SBATCH -p plgrid-gpu-a100
#SBATCH -A plgnarnlg-gpu-a100
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -c16
#SBATCH --mem=96G
#SBATCH --gres=gpu:1
#SBATCH --time=06:00:00

set -euo pipefail

module load CUDA/12.8.0
module load Miniconda3
eval "$(conda shell.bash hook)"

export D2TPATH="${D2TPATH:-$HOME/d2t}"
export PYTHONPATH="$D2TPATH/tripler:$D2TPATH/problems/triples_to_text/:$PYTHONPATH"
export HF_TOKEN="${HF_TOKEN:?HF_TOKEN must be exported}"

DOMAIN="gsmarena"
TRIPLE_DOMAIN="mobile_phone_specification"
DATA_DIR="$D2TPATH/tripler/finetune/datasets/${DOMAIN}"
TRIPLES_FILE="${TRIPLES_FILE:-$D2TPATH/tripler/outputs/test9/${TRIPLE_DOMAIN}/extracted_triples_text_predicate_catalog_stable.json}"
REPORT="$D2TPATH/tripler/finetune/runs/${DOMAIN}/eval_report.json"
MERGED_DIR="${MERGED_DIR:-$SCRATCH/ft_models/${DOMAIN}_gemma4_31b_merged}"
BASE_ID="RedHatAI/gemma-4-31B-it"
PORT="${PORT:-2997}"

conda run -n finetune-env python "$D2TPATH/tripler/finetune/eval.py" \
    --dev "$DATA_DIR/dev.jsonl" \
    --report "$REPORT" \
    --port "$PORT" \
    --api-key none \
    --max-tokens 2048 \
    --model base "$BASE_ID" \
    --model ft "$MERGED_DIR" \
    --catalog "$TRIPLES_FILE"

echo "EVAL DONE report=$REPORT"