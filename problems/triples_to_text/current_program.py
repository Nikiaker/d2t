from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    sentence = ""
    airport = None
    for triple in triples:
        if triple.predicate == "cityServed":
            airport = triple.subject
            sentence += f"{airport} serves the city of {triple.object}. "
        elif triple.predicate == "country":
            sentence += f"which is located in {triple.object}. "
        elif triple.predicate == "capital":
            sentence += f"where the capital is {triple.object}. "
        elif triple.predicate == "location":
            sentence += f"and is situated in {triple.object}. "
        elif triple.predicate == "elevationAboveTheSeaLevel":
            sentence += f"with an elevation of {triple.object} meters above sea level. "
        elif triple.predicate == "operatingOrganisation":
            sentence += f"and is operated by {triple.object}. "
    return sentence.strip()

# EVOLVE-BLOCK-END