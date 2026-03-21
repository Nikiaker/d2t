# 35B needs 70GB + KV cache
vllm serve "Qwen/Qwen3.5-35B-A3B" --port 2993 --tensor-parallel-size 2 --reasoning-parser qwen3 --language-model-only