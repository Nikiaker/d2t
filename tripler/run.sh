python app.py extract --input inputs/input_data_weather_dev_full.json --output extracted_triples.json --model google/gemma-3-270m-it --base-url http://localhost:8002/v1 --api-key none

python app.py normalize --input extracted_triples.json --output normalized_triples.json --model google/gemma-3-270m-it --base-url http://localhost:8002/v1 --api-key none

python app_domain_predicates.py --input inputs/input_data_weather_dev_full.json --output extracted_triples.json --domain "weather forecast" --model google/gemma-3-270m-it --base-url http://localhost:8002/v1 --api-key none

sbatch ~/d2t/tripler/outputs/test5/batch_triples.sh
sbatch ~/d2t/tripler/outputs/test7/batch_triples.sh