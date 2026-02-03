from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    """
    Generates a natural language sentence from a list of triples.
    """
    if not triples:
        return ""

    sentence = ""
    subject = triples[0].subject

    for i, triple in enumerate(triples):
        predicate = triple.predicate
        object_val = triple.object

        if predicate == "cityServed":
            sentence += f"{subject} serves the city of {object_val}."
        elif predicate == "elevationAboveTheSeaLevel":
            sentence += f"{subject} has an elevation of {object_val} above sea level."
        elif predicate == "location":
            sentence += f"{subject} is located in {object_val}."
        elif predicate == "operatingOrganisation":
            sentence += f"{subject} is operated by {object_val}."
        elif predicate == "runwayLength":
            sentence += f"{subject} has a runway length of {object_val}."
        elif predicate == "runwayName":
            sentence += f"{subject} has a runway named {object_val}."
        elif predicate == "country":
            sentence += f"{subject} is in {object_val}."
        elif predicate == "isPartOf":
            sentence += f"{subject} is part of {object_val}."
        elif predicate == "1stRunwayLengthFeet":
            sentence += f"The first runway of {subject} is {object_val} feet long."
        elif predicate == "1stRunwaySurfaceType":
            sentence += f"The first runway of {subject} is made of {object_val}."
        elif predicate == "3rdRunwayLengthFeet":
            sentence += f"The third runway of {subject} is {object_val} feet long."
        elif predicate == "icaoLocationIdentifier":
            sentence += f"The ICAO identifier for {subject} is {object_val}."
        elif predicate == "locationIdentifier":
            sentence += f"The location identifier for {subject} is {object_val}."
        elif predicate == "elevationAboveTheSeaLevelInFeet":
            sentence += f"{subject} has an elevation of {object_val} feet above sea level."
        elif predicate == "iataLocationIdentifier":
            sentence += f"The IATA identifier for {subject} is {object_val}."
        elif predicate == "nativeName":
            sentence += f"{subject} is also known as {object_val}."
        elif predicate == "leaderParty":
            sentence += f"{subject} is led by the {object_val}."
        elif predicate == "capital":
            sentence += f"{subject}'s capital is {object_val}."
        elif predicate == "language":
            sentence += f"{subject} speaks {object_val}."
        elif predicate == "leader":
            sentence += f"{subject} is led by {object_val}."
        elif predicate == "owner":
            sentence += f"{subject} is owned by {object_val}."
        elif predicate == "1stRunwayLengthMetre":
            sentence += f"The first runway of {subject} is {object_val} metres long."
        elif predicate == "4thRunwaySurfaceType":
            sentence += f"The fourth runway of {subject} is made of {object_val}."
        elif predicate == "5thRunwayNumber":
            sentence += f"The fifth runway of {subject} is numbered {object_val}."
        elif predicate == "largestCity":
            sentence += f"{subject}'s largest city is {object_val}."
        elif predicate == "4thRunwayLengthFeet":
            sentence += f"The fourth runway of {subject} is {object_val} feet long."
        elif predicate == "1stRunwayNumber":
            sentence += f"The first runway of {subject} is numbered {object_val}."
        elif predicate == "elevationAboveTheSeaLevelInMetres":
            sentence += f"{subject} has an elevation of {object_val} metres above sea level."
        elif predicate == "administrativeArrondissement":
            sentence += f"{subject} is located in the {object_val}."
        elif predicate == "mayor":
            sentence += f"The mayor of {subject} is {object_val}."
        elif predicate == "2ndRunwaySurfaceType":
            sentence += f"The second runway of {subject} is made of {object_val}."
        elif predicate == "3rdRunwaySurfaceType":
            sentence += f"The third runway of {subject} is made of {object_val}."
        elif predicate == "runwaySurfaceType":
            sentence += f"{subject}'s runway surface type is {object_val}."
        elif predicate == "officialLanguage":
            sentence += f"{subject}'s official language is {object_val}."
        elif predicate == "city":
            sentence += f"{subject} is located in {object_val}."
        elif predicate == "jurisdiction":
            sentence += f"{subject}'s jurisdiction is {object_val}."
        elif predicate == "demonym":
            sentence += f"People from {subject} are called {object_val}."
        elif predicate == "aircraftHelicopter":
            sentence += f"{subject} uses {object_val} helicopters."
        elif predicate == "transportAircraft":
            sentence += f"{subject} uses {object_val} transport aircraft."
        elif predicate == "currency":
            sentence += f"{subject}'s currency is {object_val}."
        elif predicate == "headquarter":
            sentence += f"{subject}'s headquarters are at {object_val}."
        elif predicate == "class":
            sentence += f"{subject} is classified as {object_val}."
        elif predicate == "division":
            sentence += f"{subject} belongs to the {object_val} division."
        elif predicate == "order":
            sentence += f"{subject} is part of the {object_val} order."
        elif predicate == "regionServed":
            sentence += f"{subject} serves the {object_val} region."
        elif predicate == "leaderTitle":
            sentence += f"{subject}'s leader title is {object_val}."
        elif predicate == "hubAirport":
            sentence += f"{subject}'s hub airport is {object_val}."
        elif predicate == "aircraftFighter":
            sentence += f"{subject} uses {object_val} fighter aircraft."
        elif predicate == "attackAircraft":
            sentence += f"{subject} uses {object_val} attack aircraft."
        elif predicate == "battle":
            sentence += f"{subject} participated in the {object_val} battle."
        elif predicate == "5thRunwaySurfaceType":
            sentence += f"The fifth runway of {subject} is made of {object_val}."
        elif predicate == "countySeat":
            sentence += f"{subject}'s county seat is {object_val}."
        elif predicate == "chief":
            sentence += f"{subject}'s chief is {object_val}."
        elif predicate == "foundedBy":
            sentence += f"{subject} was founded by {object_val}."
        elif predicate == "postalCode":
            sentence += f"{subject}'s postal code is {object_val}."
        elif predicate == "areaCode":
            sentence += f"{subject}'s area code is {object_val}."
        elif predicate == "foundingYear":
            sentence += f"{subject} was founded in {object_val}."
        elif predicate == "ceremonialCounty":
            sentence += f"{subject}'s ceremonial county is {object_val}."
        else:
            sentence += f" {subject} is related to {object_val}." #Default case

    return sentence

# EVOLVE-BLOCK-END