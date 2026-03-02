curl -X POST "http://localhost:8001/v1/chat/completions" \
	-H "Content-Type: application/json" \
	--data '{
		"model": "RedHatAI/Llama-3.3-70B-Instruct-FP8-dynamic",
		"messages": [
			{
				"role": "user",
				"content": "What is the capital of France?"
			}
		]
	}'


curl -X POST "http://localhost:2993/v1/chat/completions" -H "Content-Type: application/json" -H "Authorization: Bearer AiIsMyLife25" --data '{ "model": "RedHatAI/Llama-3.3-70B-Instruct-FP8-dynamic", "messages": [{ "role": "user", "content": "What is the capital of France?" }] }'