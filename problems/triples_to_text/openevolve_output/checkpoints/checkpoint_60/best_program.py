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
        "elevationAboveTheSeaLevel": "{subject} has an elevation of {object} meters above sea level.",
        "location": "{subject} is located in {object}.",
        "operatingOrganisation": "{subject} is operated by {object}.",
        "runwayLength": "{subject} has a runway length of {object} meters.",
        "runwayName": "{subject} has a runway named {object}.",
        "country": "{subject} is located in the country of {object}.",
        "isPartOf": "{subject} is part of {object}.",
        "1stRunwayLengthFeet": "{subject} has a first runway length of {object} feet.",
        "1stRunwaySurfaceType": "{subject} has a first runway surface type of {object}.",
        "3rdRunwayLengthFeet": "{subject} has a third runway length of {object} feet.",
        "icaoLocationIdentifier": "{subject} has an ICAO location identifier of {object}.",
        "locationIdentifier": "{subject} has a location identifier of {object}.",
        # Add more templates for other predicates as needed
    }

    sentences = []
    for triple in triples:
        predicate = triple.predicate
        if predicate in sentence_templates:
            sentence = sentence_templates[predicate].format(subject=triple.subject, object=triple.object)
        else:
            sentence = f"The {triple.predicate} of {triple.subject} is {triple.object}."
        sentences.append(sentence)
    return " ".join(sentences)

# EVOLVE-BLOCK-END