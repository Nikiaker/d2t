from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    sentences = []
    for triple in triples:
        if triple.predicate == "cityServed":
            sentences.append(f"{triple.subject} serves the city of {triple.object}.")
        elif triple.predicate == "elevationAboveTheSeaLevel":
            sentences.append(f"{triple.subject} has an elevation of {triple.object} meters above sea level.")
        elif triple.predicate == "location":
            sentences.append(f"{triple.subject} is located in {triple.object}.")
        elif triple.predicate == "operatingOrganisation":
            sentences.append(f"{triple.subject} is operated by {triple.object}.")
        elif triple.predicate == "runwayLength":
            sentences.append(f"{triple.subject} has a runway length of {triple.object} meters.")
        elif triple.predicate == "runwayName":
            sentences.append(f"{triple.subject} has a runway named {triple.object}.")
        else:
            sentences.append(f"The {triple.predicate} of {triple.subject} is {triple.object}.")
    return " ".join(sentences)

# EVOLVE-BLOCK-END