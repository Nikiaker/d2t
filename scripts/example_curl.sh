curl -X POST "http://localhost:8000/v1/chat/completions" \
	-H "Content-Type: application/json" \
	--data '{
		"model": "RedHatAI/Meta-Llama-3.1-8B-Instruct-FP8",
		"messages": [
			{
				"role": "user",
				"content": "What is the capital of France?"
			}
		]
	}'


curl -X POST "http://localhost:2993/v1/chat/completions" -H "Content-Type: application/json" -H "Authorization: Bearer AiIsMyLife25" --data '{ "model": "RedHatAI/Meta-Llama-3.1-70B-Instruct-FP8", "messages": [{ "role": "user", "content": "What is the capital of France?" }] }'