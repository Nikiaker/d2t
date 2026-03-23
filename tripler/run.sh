python app.py extract --input input_data.json --output extracted_triples.json --model openai/gpt-oss-120b --base-url http://localhost:8001/v1 --api-key none

python app.py normalize --input extracted_triples.json --output normalized_triples.json --model openai/gpt-oss-120b --base-url http://localhost:8001/v1 --api-key none