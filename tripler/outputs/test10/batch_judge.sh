#!/bin/bash
#SBATCH -w hgx1
#SBATCH -p hgx
#SBATCH -c16
#SBATCH --gres=gpu:1
#SBATCH -n1
SERVER_LOG1="$HOME/vllm-server15.log"
SERVER_PID1=""
trap 'kill $SERVER_PID1 2>/dev/null' EXIT

export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

CUDA_VISIBLE_DEVICES=0 \
conda run -n vllm-env vllm serve \
	google/gemma-4-31B-it \
    --port 3015 \
    --max-model-len 30K \
    --reasoning-parser gemma4 \
    --default-chat-template-kwargs '{"enable_thinking": false}' \
    --max-num-batched-tokens 4096 \
    --gpu-memory-utilization 0.95 \
    > "$SERVER_LOG1" 2>&1 &
SERVER_PID1=$!

conda run -n openevolve-env python $D2TPATH/.conda/test-response.py --port 3015 --timeout 300
if [ $? -ne 0 ]; then
    echo "ERROR: vLLM server 1 (gemma) did not start within 5 minutes. Canceling." >&2
    exit 1
fi

conda run -n openevolve-env python $D2TPATH/tripler/batch_wrapper_server.py \
    --upstream-base-url http://localhost:3015 \
    --port 3014 \
    --storage-dir $HOME/.batch_wrapper_data10 \
	2>&1 &

cd $D2TPATH/tripler/

conda run -n openevolve-env python make_scoring_table.py \
  --test-dir outputs/test10

conda run -n openevolve-env python judge_scoring_batch.py \
  --model google/gemma-4-31B-it \
  --base-url http://localhost:3014/v1 \
  --api-key none \
  --test-dir outputs/test10 \
  --batch-timeout-seconds 86400 \
  --poll-interval-seconds 30