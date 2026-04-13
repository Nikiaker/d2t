docker run --device nvidia.com/gpu=all \
	--name vllm_lmcache_container \
	-v ~/.cache/huggingface:/root/.cache/huggingface \
 	--env-file .env \
	-p 8001:8000 \
	--ipc=host \
	vllm_lmcache \
	--model cyankiwi/Qwen3.5-9B-AWQ-4bit \
	--gpu-memory-utilization 0.9 \
	--enforce-eager \
	--kv-transfer-config \
    '{"kv_connector":"LMCacheConnectorV1",
      "kv_role":"kv_both"
    }'


docker run --device nvidia.com/gpu=all \
        --name vllm_container \
        -v ~/.cache/huggingface:/root/.cache/huggingface \
        -p 8001:8000 \
        --ipc=host \
        vllm/vllm-openai:latest \
        google/gemma-3-270m-it \
        --enforce-eager