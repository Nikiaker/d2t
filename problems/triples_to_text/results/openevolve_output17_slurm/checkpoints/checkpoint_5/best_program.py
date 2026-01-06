from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    sentence_templates = {
        "cityServed": "{subject} serves the city of {object}.",
        "elevationAboveTheSeaLevel": "{subject} is {object} meters above sea level.",
        "location": "{subject} is located in {object}.",
        "operatingOrganisation": "{subject} is operated by {object}.",
        "runwayLength": "{subject} has a runway length of {object} meters.",
        "runwayName": "{subject} has the runway name {object}.",
        "country": "{subject} is in {object}.",
        "isPartOf": "{subject} is part of {object}.",
        "1stRunwayLengthFeet": "{subject} has a first runway length of {object} feet.",
        "1stRunwaySurfaceType": "{subject} has a first runway made of {object}.",
        # Add more predicates and sentence templates as needed
    }

    sentences = []
    for triple in triples:
        predicate = triple.predicate
        subject = triple.subject
        object = triple.object

        if predicate in sentence_templates:
            sentence = sentence_templates[predicate].format(subject=subject, object=object)
        else:
            sentence = f"The {predicate} of {subject} is {object}."

        sentences.append(sentence)

    return ". ".join(sentences) + "."

# EVOLVE-BLOCK-END