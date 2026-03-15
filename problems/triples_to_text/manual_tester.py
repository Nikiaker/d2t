from best_program import Triple, predict

if __name__ == "__main__":
    # Example triples
    triples = [
        Triple(subject="Aarhus Airport", predicate="location", object="Tirstrup"),
        Triple(subject="Tirstrup", predicate="country", object="Denmark"),
        Triple(subject="Denmark", predicate="language", object="Faroese language"),
    ]

    # Generate text from triples
    generated_text = predict(triples)
    print("Generated Text:")
    print(generated_text)