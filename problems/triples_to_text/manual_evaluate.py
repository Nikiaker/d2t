import os

os.environ["CONFIG_PATH"] = "./outputs/Airport_output/config_remote.yaml"

from evaluator import evaluate


evalutaion_result = evaluate("./initial_program.py")
print(evalutaion_result)