docker run --device nvidia.com/gpu=all \
	--name vllm_lmcache_container \
	-v ~/.cache/huggingface:/root/.cache/huggingface \
 	--env-file .env \
	-p 8000:8000 \
	--ipc=host \
	vllm_lmcache \
	--model RedHatAI/Meta-Llama-3.1-8B-Instruct-FP8 \
	--max-model-len 12000 \
	--enforce-eager \
	--kv-transfer-config \
    '{"kv_connector":"LMCacheConnectorV1",
      "kv_role":"kv_both"
    }'