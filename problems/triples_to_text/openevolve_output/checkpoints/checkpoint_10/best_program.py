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
        sentences.append(f"The {triple.predicate} of {triple.subject} is {triple.object}.")
    return " ".join(sentences)

# EVOLVE-BLOCK-END