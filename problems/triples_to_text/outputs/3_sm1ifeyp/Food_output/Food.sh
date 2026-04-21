#!/bin/bash
#SBATCH -w hgx1
#SBATCH -p hgx
#SBATCH -c16
#SBATCH --gres=gpu:3
#SBATCH -n1
SERVER_LOG1="/home/inf151915/vllm-server1.log"
SERVER_LOG2="/home/inf151915/vllm-server2.log"

export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

CUDA_VISIBLE_DEVICES=0 \
conda run -n vllm-env vllm serve \
	google/gemma-4-31B-it \
    --port 2996 \
    --max-model-len 32K \
    > "$SERVER_LOG1" 2>&1 &
SERVER_PID1=$!

conda run -n openevolve-env python ~/d2t/.conda/test-response.py --port 2996

conda run -n openevolve-env python ~/d2t/tripler/batch_wrapper_server.py \
    --upstream-base-url http://localhost:2996 \
    --port 2995 \
    --storage-dir ~/.batch_wrapper_data \
	2>&1 &

cd ~/d2t/problems/triples_to_text
export WEBNLG_BASE_PATH="/home/inf151915/d2t/problems/triples_to_text/tests/webnlg/release_v3.0/en/"
export WEBNLG_DOMAIN=Food
export CONFIG_PATH="./outputs/3_sm1ifeyp/${WEBNLG_DOMAIN}_output/config_remote.yaml"
CHECKPOINT_ROOT="./outputs/3_sm1ifeyp/${WEBNLG_DOMAIN}_output/openevolve_output/checkpoints"
LATEST_CHECKPOINT=""

if [ -d "${CHECKPOINT_ROOT}" ]; then
	LATEST_CHECKPOINT=$(find "${CHECKPOINT_ROOT}" -maxdepth 1 -mindepth 1 -type d -name "checkpoint_*" | sort -V | tail -n 1)
fi

CHECKPOINT_ARG=()
if [ -n "${LATEST_CHECKPOINT}" ]; then
	CHECKPOINT_ARG=(--checkpoint "${LATEST_CHECKPOINT}")
fi

conda run -n openevolve-env python ../../openevolve/openevolve-run.py initial_program.py evaluator.py --config ${CONFIG_PATH} "${CHECKPOINT_ARG[@]}" --output ./outputs/3_sm1ifeyp/${WEBNLG_DOMAIN}_output/openevolve_output

cd ./outputs/3_sm1ifeyp/${WEBNLG_DOMAIN}_output
conda run -n openevolve-env python ../../../plot_results.py
export BEST_PROGRAM_PATH="./openevolve_output/best/best_program.py"
conda run -n openevolve-env python ../../../final_test.py