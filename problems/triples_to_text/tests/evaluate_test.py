from nltk.translate.bleu_score import sentence_bleu
import evaluate

prediction_text = "Aarhus Airport is elevated 25 meters above the sea level."
reference_texts = [
    "Aarhus Airport is 25 metres above sea level.",
    "Aarhus airport is at an elevation of 25 metres above seal level.",
    "Aarhus Airport is 25.0 metres above the sea level."
]

bleu = evaluate.load("bleu")
results = bleu.compute(predictions=[prediction_text], references=[reference_texts])
print(results['bleu'])
print(type(results['bleu']))