from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triple: Triple) -> str:
    # Use a more descriptive template for the sentence
    # Consider the type of the object and use a more descriptive template
    if triple.object.isnumeric():
        return f"The {triple.subject} has a {triple.predicate} of {triple.object} meters."
    else:
        return f"The {triple.subject} is characterized by having a {triple.predicate} of {triple.object}."

# EVOLVE-BLOCK-END