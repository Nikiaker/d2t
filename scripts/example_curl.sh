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