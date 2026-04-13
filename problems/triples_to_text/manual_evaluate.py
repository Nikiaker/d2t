import os

os.environ["CONFIG_PATH"] = "./config_remote.yaml"

from evaluator import evaluate


evalutaion_result = evaluate("./initial_program.py")
print(evalutaion_result)