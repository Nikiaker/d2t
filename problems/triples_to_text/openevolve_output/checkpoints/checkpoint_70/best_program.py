from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    predicate_descriptions = {
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
        "elevationAboveTheSeaLevelInFeet": "{subject} has an elevation of {object} feet above sea level.",
        "iataLocationIdentifier": "{subject} has an IATA location identifier of {object}.",
        "nativeName": "{subject} has a native name of {object}.",
        "leaderParty": "{subject} is led by the {object}.",
        "capital": "{subject} has a capital of {object}.",
        "language": "{subject} has an official language of {object}.",
        "leader": "{subject} is led by {object}.",
        "owner": "{subject} is owned by {object}.",
        "currency": "{subject} uses {object} as its currency.",
        "headquarter": "{subject} has its headquarters in {object}.",
        "class": "{subject} belongs to the class of {object}.",
        "division": "{subject} is part of the division of {object}.",
        "order": "{subject} is part of the order of {object}.",
        "regionServed": "{subject} serves the region of {object}.",
        "leaderTitle": "{subject} has a leader title of {object}.",
        "hubAirport": "{subject} has a hub airport at {object}.",
        "aircraftFighter": "{subject} operates {object} fighter aircraft.",
        "attackAircraft": "{subject} operates {object} attack aircraft.",
        "battle": "{subject} has been involved in the {object} battle.",
        # Add even more predicate descriptions as needed
    }

    sentences = []
    for triple in triples:
        predicate = triple.predicate
        if predicate in predicate_descriptions:
            sentence = predicate_descriptions[predicate].format(subject=triple.subject, object=triple.object)
        else:
            sentence = f"The {triple.predicate} of {triple.subject} is {triple.object}."
        sentences.append(sentence)
    return " and ".join(sentences)

# EVOLVE-BLOCK-END