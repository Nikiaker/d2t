from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    if not triples:
        return "No information available."

    subject_data = {}
    for triple in triples:
        if triple.subject not in subject_data:
            subject_data[triple.subject] = []
        subject_data[triple.subject].append((triple.predicate, triple.object))

    sentences = []
    for subject, data in subject_data.items():
        properties = []
        for predicate, object in data:
            if predicate == "discoverer":
                properties.append(f"was discovered by {object}")
            elif predicate == "epoch":
                properties.append(f"has an epoch of {object}")
            elif predicate == "apoapsis":
                properties.append(f"has an apoapsis of {object}")
            elif predicate == "orbitalPeriod":
                properties.append(f"has an orbital period of {object}")
            elif predicate == "periapsis":
                properties.append(f"has a periapsis of {object}")
            elif predicate == "averageSpeed":
                properties.append(f"has an average speed of {object}")
            elif predicate == "escapeVelocity":
                properties.append(f"has an escape velocity of {object}")
            elif predicate == "mass":
                properties.append(f"has a mass of {object}")
            elif predicate == "temperature":
                properties.append(f"has a temperature of {object}")
            elif predicate == "density":
                properties.append(f"has a density of {object}")
            elif predicate == "rotationPeriod":
                properties.append(f"has a rotation period of {object}")
            elif predicate == "maximumTemperature":
                properties.append(f"has a maximum temperature of {object}")
            elif predicate == "meanTemperature":
                properties.append(f"has a mean temperature of {object}")
            elif predicate == "minimumTemperature":
                properties.append(f"has a minimum temperature of {object}")
            elif predicate == "formerName":
                properties.append(f"was formerly known as {object}")
            elif predicate == "absoluteMagnitude":
                properties.append(f"has an absolute magnitude of {object}")
            elif predicate == "discovered":
                properties.append(f"was discovered on {object}")
            elif predicate == "surfaceArea":
                properties.append(f"has a surface area of {object}")
            elif predicate == "deathCause":
                properties.append(f"died of {object}")
            elif predicate == "deathPlace":
                properties.append(f"died in {object}")
            elif predicate == "nationality":
                properties.append(f"is a {object} national")
            elif predicate == "stateOfOrigin":
                properties.append(f"originates from {object}")
            elif predicate == "almaMater":
                properties.append(f"attended {object}")
            elif predicate == "birthPlace":
                properties.append(f"was born in {object}")
            elif predicate == "doctoralStudent":
                properties.append(f"was a doctoral student of {object}")
            elif predicate == "deathDate":
                properties.append(f"died on {object}")
            elif predicate == "birthDate":
                properties.append(f"was born on {object}")
            else:
                properties.append(f"has a {predicate} of {object}")

        sentence = f"{subject} {', '.join(properties[:-1]) + ' and ' + properties[-1] if len(properties) > 1 else properties[0]}."
        sentences.append(sentence)

    if len(sentences) == 1:
        return sentences[0]
    else:
        return " ".join(sentences)

# EVOLVE-BLOCK-END