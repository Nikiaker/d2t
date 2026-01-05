from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    sentence = ""
    for i, triple in enumerate(triples):
        if i == 0:
            sentence += f"The {triple.predicate} of {triple.subject} is {triple.object}. "
        else:
            if triple.predicate == "location":
                sentence += f"It is located in {triple.object}. "
            elif triple.predicate == "elevationAboveTheSeaLevel":
                sentence += f"It is situated at an elevation of {triple.object} meters above the sea level. "
            else:
                sentence += f"Additionally, the {triple.predicate} of {triple.subject} is {triple.object}. "
    return sentence.strip()

# EVOLVE-BLOCK-END