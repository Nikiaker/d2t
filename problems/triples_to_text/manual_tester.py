from best_program import Triple, predict

if __name__ == "__main__":
    # Example triples
    triples = [
        Triple(subject="Heathrow Airport", predicate="location", object="London"),
        Triple(subject="Heathrow Airport", predicate="runwayLength", object="3902"),
        Triple(subject="Heathrow Airport", predicate="icaoLocationIdentifier", object="EGLL"),
    ]

    # Generate text from triples
    generated_text = predict(triples)
    print("Generated Text:")
    print(generated_text)