from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    sentences = []
    predicate_mapping = {
        "cityServed": "{} serves the city of {}.",
        "elevationAboveTheSeaLevel": "{} is {} meters above sea level.",
        "operatingOrganisation": "{} is operated by {}.",
        "runwayName": "The runway name of {} is {}.",
        "location": "{} is located in {}.",
        "country": "{} is in {}.",
        "isPartOf": "{} is part of {}.",
        "1stRunwayLengthFeet": "The length of the 1st runway at {} is {} feet.",
        "1stRunwaySurfaceType": "The 1st runway at {} is made of {}.",
        "icaoLocationIdentifier": "The ICAO Location Identifier of {} is {}.",
        "iataLocationIdentifier": "The IATA Location Identifier of {} is {}.",
    }

    for triple in triples:
        if triple.predicate in predicate_mapping:
            sentences.append(predicate_mapping[triple.predicate].format(triple.subject, triple.object))
        else:
            sentences.append(f"The {triple.predicate} of {triple.subject} is {triple.object}.")
    return " ".join(sentences)

# EVOLVE-BLOCK-END