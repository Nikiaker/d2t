#!/bin/bash
#SBATCH -p plgrid-gpu-a100
#SBATCH -A plgnarnlg-gpu-a100
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -c16
#SBATCH --mem=128G
#SBATCH --gres=gpu:4
#SBATCH --time=48:00:00
set -eo pipefail
DOMAIN="owid"
TRIPLE_DOMAIN="owid"
EXPERIMENT="${EXPERIMENT:-baseline}"

module load CUDA/12.8.0
module load Miniconda3
eval "$(conda shell.bash hook)"
conda activate finetune-env
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

export PYTHONPATH="$D2TPATH/tripler:$D2TPATH/openevolve/:$D2TPATH/problems/triples_to_text/tests/benchmark_reader/:$D2TPATH/problems/triples_to_text/:$PYTHONPATH"
source "$D2TPATH/tripler/finetune/experiments.sh"
configure_experiment "$EXPERIMENT"

BASE_ID="${BASE_ID:-google/gemma-4-31B-it}"
DATA_DIR="$D2TPATH/tripler/finetune/datasets/${DOMAIN}"
TRIPLES_FILE="${TRIPLES_FILE:-$D2TPATH/tripler/outputs/test11/${TRIPLE_DOMAIN}/joined.json}"
if [ "$EXPERIMENT" = "baseline" ]; then
    RUN_DIR="$D2TPATH/tripler/finetune/runs/${DOMAIN}"
    EXPERIMENT_SUFFIX=""
else
    RUN_DIR="$D2TPATH/tripler/finetune/runs/${DOMAIN}/${EXPERIMENT}"
    EXPERIMENT_SUFFIX="_${EXPERIMENT}"
fi
REPORT="$RUN_DIR/eval_report.json"
MERGED_DIR="${MERGED_DIR:-$SCRATCH/ft_models/${DOMAIN}_gemma4_31b${EXPERIMENT_SUFFIX}_merged}"
MERGED_CHECKPOINT_100_DIR="${MERGED_CHECKPOINT_100_DIR:-$SCRATCH/ft_models/${DOMAIN}_gemma4_31b${EXPERIMENT_SUFFIX}_checkpoint_100_merged}"
MERGED_CHECKPOINT_150_DIR="${MERGED_CHECKPOINT_150_DIR:-$SCRATCH/ft_models/${DOMAIN}_gemma4_31b${EXPERIMENT_SUFFIX}_checkpoint_150_merged}"
PORT="${PORT:-2999}"

python "$D2TPATH/tripler/finetune/eval.py" \
    --train "$DATA_DIR/train.jsonl" \
    --dev "$DATA_DIR/dev.jsonl" \
    --report "$REPORT" \
    --port "$PORT" \
    --api-key none \
    --max-tokens 2048 \
    --tp 4 \
    --vllm-env vllm-env \
    --model base "$BASE_ID" \
    --model ft "$MERGED_DIR" \
    --model checkpoint-100 "$MERGED_CHECKPOINT_100_DIR" \
    --model checkpoint-150 "$MERGED_CHECKPOINT_150_DIR" \
    --catalog "$TRIPLES_FILE"

echo "EVAL DONE report=$REPORT"
