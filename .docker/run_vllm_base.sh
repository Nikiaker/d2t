docker run --device nvidia.com/gpu=all \
	--name vllm_container \
	-v ~/.cache/huggingface:/root/.cache/huggingface \
	-p 8001:8000 \
	--ipc=host \
	vllm/vllm-openai:latest \
	google/gemma-3-270m-it \
	--enforce-eager