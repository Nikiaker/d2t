#!/bin/bash
#SBATCH -w hgx1
#SBATCH -p hgx
#SBATCH -c4
#SBATCH -n1

conda run -n openevolve-env python ~/d2t/.conda/test-response.py --port 2993

conda run -n openevolve-env python ~/d2t/.conda/test-response.py --port 2994

cd ~/d2t/problems/triples_to_text
export WEBNLG_BASE_PATH="/home/inf151915/d2t/problems/triples_to_text/tests/webnlg/release_v3.0/en/"
export WEBNLG_DOMAIN=Building
export CONFIG_PATH="./outputs/${WEBNLG_DOMAIN}_output/config_remote.yaml"
CHECKPOINT_ROOT="./outputs/${WEBNLG_DOMAIN}_output/openevolve_output/checkpoints"
LATEST_CHECKPOINT=""

if [ -d "${CHECKPOINT_ROOT}" ]; then
	LATEST_CHECKPOINT=$(find "${CHECKPOINT_ROOT}" -maxdepth 1 -mindepth 1 -type d -name "checkpoint_*" | sort -V | tail -n 1)
fi

CHECKPOINT_ARG=()
if [ -n "${LATEST_CHECKPOINT}" ]; then
	CHECKPOINT_ARG=(--checkpoint "${LATEST_CHECKPOINT}")
fi

conda run -n openevolve-env python ../../openevolve/openevolve-run.py initial_program.py evaluator.py --config ${CONFIG_PATH} "${CHECKPOINT_ARG[@]}" --output ./outputs/${WEBNLG_DOMAIN}_output/openevolve_output

cd ./outputs/${WEBNLG_DOMAIN}_output
conda run -n openevolve-env python ../../plot_results.py
export BEST_PROGRAM_PATH="./openevolve_output/best/best_program.py"
conda run -n openevolve-env python ../../final_test.py