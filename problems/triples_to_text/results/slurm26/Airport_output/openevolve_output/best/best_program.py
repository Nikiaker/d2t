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
        if triple.predicate == "cityServed":
            sentence += f"{triple.subject} serves the city of {triple.object}. "
        elif triple.predicate == "country":
            sentence += f"{triple.subject} is located in {triple.object}. "
        elif triple.predicate == "capital":
            if i > 0:
                sentence += " and "
            sentence += f"the capital of {triple.subject} is {triple.object}. "
        elif triple.predicate == "elevationAboveTheSeaLevel":
            sentence += f"{triple.subject} has an elevation of {triple.object} meters above sea level. "
        elif triple.predicate == "location":
            sentence += f"{triple.subject} is located in {triple.object}. "
        elif triple.predicate == "operatingOrganisation":
            sentence += f"{triple.subject} is operated by {triple.object}. "
        elif triple.predicate == "runwayLength":
            sentence += f"The runway length of {triple.subject} is {triple.object} meters. "
        elif triple.predicate == "runwayName":
            sentence += f"The runway name of {triple.subject} is {triple.object}. "
        elif triple.predicate == "isPartOf":
            sentence += f"{triple.subject} is part of {triple.object}. "
        elif triple.predicate == "1stRunwayLengthFeet":
            sentence += f"The first runway of {triple.subject} is {triple.object} feet long. "
        elif triple.predicate == "1stRunwaySurfaceType":
            sentence += f"The first runway surface type of {triple.subject} is {triple.object}. "
        elif triple.predicate == "3rdRunwayLengthFeet":
            sentence += f"The third runway of {triple.subject} is {triple.object} feet long. "
        elif triple.predicate == "icaoLocationIdentifier":
            sentence += f"The ICAO location identifier of {triple.subject} is {triple.object}. "
        elif triple.predicate == "locationIdentifier":
            sentence += f"The location identifier of {triple.subject} is {triple.object}. "
        elif triple.predicate == "elevationAboveTheSeaLevelInFeet":
            sentence += f"{triple.subject} has an elevation of {triple.object} feet above sea level. "
        elif triple.predicate == "iataLocationIdentifier":
            sentence += f"The IATA location identifier of {triple.subject} is {triple.object}. "
        elif triple.predicate == "nativeName":
            sentence += f"{triple.subject} is also known as {triple.object}. "
        elif triple.predicate == "leaderParty":
            sentence += f"{triple.subject} is led by the {triple.object}. "
        elif triple.predicate == "language":
            sentence += f"The official language of {triple.subject} is {triple.object}. "
        elif triple.predicate == "owner":
            sentence += f"{triple.subject} is owned by {triple.object}. "
        elif triple.predicate == "1stRunwayLengthMetre":
            sentence += f"The first runway of {triple.subject} is {triple.object} meters long. "
        elif triple.predicate == "4thRunwaySurfaceType":
            sentence += f"The fourth runway surface type of {triple.subject} is {triple.object}. "
        elif triple.predicate == "largestCity":
            sentence += f"The largest city in {triple.subject} is {triple.object}. "
        elif triple.predicate == "4thRunwayLengthFeet":
            sentence += f"The fourth runway of {triple.subject} is {triple.object} feet long. "
        elif triple.predicate == "elevationAboveTheSeaLevelInMetres":
            sentence += f"{triple.subject} has an elevation of {triple.object} meters above sea level. "
        elif triple.predicate == "administrativeArrondissement":
            sentence += f"{triple.subject} is in the {triple.object}. "
        elif triple.predicate == "officialLanguage":
            sentence += f"The official language of {triple.subject} is {triple.object}. "
        elif triple.predicate == "regionServed":
            sentence += f"{triple.subject} serves the region of {triple.object}. "
        else:
            sentence += f"{triple.subject} {triple.predicate} {triple.object}. "
    return sentence

# EVOLVE-BLOCK-END