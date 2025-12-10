from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triple: Triple) -> str:
    if triple.predicate == "elevationAboveTheSeaLevelInMetres" or triple.predicate == "elevationAboveTheSeaLevel":
        return f"{triple.subject} airport is {triple.object} metres above sea level."
    elif triple.predicate == "runwayLength":
        return f"The runway length of {triple.subject} is {triple.object} metres."
    elif triple.predicate == "runwaySurfaceType":
        return f"The runway surface type at {triple.subject} is {triple.object}."
    elif triple.predicate == "country":
        return f"{triple.subject} is in {triple.object}."
    elif triple.predicate == "city":
        return f"{triple.subject} is the city of {triple.object}."
    elif triple.predicate == "location":
        return f"{triple.subject} is located in {triple.object}."
    elif triple.predicate == "runwayName":
        return f"{triple.subject} runway name is {triple.object}."
    elif triple.predicate == "1stRunwayLengthFeet":
        return f"The length of the 1st runway at {triple.subject} is {triple.object} feet."
    elif triple.predicate == "1stRunwaySurfaceType":
        return f"The first runway at {triple.subject} is made from {triple.object}."
    elif triple.predicate == "3rdRunwayLengthFeet":
        return f"The third runway at {triple.subject} is {triple.object} feet long."
    elif triple.predicate == "icaoLocationIdentifier":
        return f"{triple.subject} ICAO Location Identifier is {triple.object}."
    elif triple.predicate == "iataLocationIdentifier":
        return f"{triple.subject} IATA Location Identifier is {triple.object}."
    elif triple.predicate == "locationIdentifier":
        return f"The location identifier for {triple.subject} is {triple.object}."
    elif triple.predicate == "nativeName":
        return f"{triple.object} is the native name of {triple.subject}."
    elif triple.predicate == "leaderParty":
        return f"The leader party at {triple.subject} is {triple.object}."
    elif triple.predicate == "capital":
        return f"{triple.subject} is the capital of {triple.object}."
    elif triple.predicate == "leaderTitle":
        return f"{triple.subject} is led by the {triple.object}."
    elif triple.predicate == "hubAirport":
        return f"The hub airport for {triple.object} is {triple.subject}."
    elif triple.predicate == "largestCity":
        return f"The largest city in {triple.object} is {triple.subject}."
    else:
        return f"The {triple.predicate} of {triple.subject} is {triple.object}."

# EVOLVE-BLOCK-END