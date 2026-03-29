export HOSTED_VLLM_API_BASE="http://localhost:8000"
export HOSTED_VLLM_API_KEY="your-api-key"

litellm --config ~/d2t/.conda/proxy_config.yaml

python ~/d2t/tripler/batch_wrapper_server.py --upstream-base-url http://localhost:2993 --port 2992 --storage-dir ~/.batch_wrapper_data