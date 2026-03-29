python app.py extract --input inputs/input_data_weather_dev_full.json --output outputs/test3/extracted_triples.json --model openai/gpt-oss-120b --base-url http://localhost:8001/v1 --api-key none

python app.py normalize --input outputs/test3/extracted_triples.json --output outputs/test3/normalized_triples.json --model openai/gpt-oss-120b --base-url http://localhost:8001/v1 --api-key none