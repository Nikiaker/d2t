from nltk.translate.bleu_score import sentence_bleu

prediction_text = "Aarhus Airport is elevated 25 meters above the sea level."
reference_texts = [
    "Aarhus Airport is 25 metres above sea level.",
    "Aarhus airport is at an elevation of 25 metres above seal level.",
    "Aarhus Airport is 25.0 metres above the sea level."
]

# Define your desired weights (example: higher weight for bi-grams)
weights = (0.25,)  # Weights for uni-gram, bi-gram, tri-gram, and 4-gram

# Reference and predicted texts (same as before)
reference = [ref.lower().split() for ref in reference_texts]
predictions = prediction_text.lower().split()

# Calculate BLEU score with weights
score = sentence_bleu(reference, predictions, weights=weights)
print(score)