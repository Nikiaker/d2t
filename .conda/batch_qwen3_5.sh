# 35B needs 70GB + KV cache
vllm serve "Qwen/Qwen3.5-35B-A3B" --port 2993 --tensor-parallel-size 2 --reasoning-parser qwen3 --language-model-only

vllm serve "Qwen/Qwen3.5-122B-A10B-FP8" --reasoning-parser qwen3 --language-model-only --tensor-parallel-size 2