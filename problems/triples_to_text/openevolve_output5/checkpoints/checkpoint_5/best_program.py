from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triple: Triple) -> str:
    return f"The {triple.predicate} of {triple.subject} is {triple.object}."

# EVOLVE-BLOCK-END