from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    return f"The {triples[0].predicate} of {triples[0].subject} is {triples[0].object}."

# EVOLVE-BLOCK-END