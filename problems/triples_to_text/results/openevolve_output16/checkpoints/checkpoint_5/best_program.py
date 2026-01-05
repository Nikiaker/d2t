from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    subject = triples[0].subject
    sentence = f"The {triples[0].predicate} of {subject} is {triples[0].object}."

    for triple in triples[1:]:
        if triple.predicate == 'cityServed':
            subject = triple.object
        elif triple.predicate == 'location':
            sentence += f" Located in {triple.object}."
        elif triple.predicate == 'isPartOf':
            sentence += f" Part of {triple.object}."
        elif triple.predicate == 'runwayLength':
            sentence += f" With a runway length of {triple.object} meters."
        else:
            sentence += f" The {triple.predicate} is {triple.object}."

    return sentence

# EVOLVE-BLOCK-END