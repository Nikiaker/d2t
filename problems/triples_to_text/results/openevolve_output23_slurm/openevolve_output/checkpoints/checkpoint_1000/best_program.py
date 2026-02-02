from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    """
    Generates a sentence from a list of triples related to airports.
    """
    airport = None
    location_info = []
    runway_info = []
    other_info = []

    for triple in triples:
        subject = triple.subject
        predicate = triple.predicate
        object_val = triple.object

        if predicate == "cityServed":
            location_info.append(f"{subject} serves the city of {object_val}")
        elif predicate == "country":
            location_info.append(f"{subject} is located in {object_val}")
        elif predicate == "elevationAboveTheSeaLevel":
            location_info.append(f"{subject} is {object_val} meters above sea level")
        elif predicate == "elevationAboveTheSeaLevelInFeet":
            location_info.append(f"{subject} is {object_val} feet above sea level")
        elif predicate == "runwayLength":
            runway_info.append(f"{subject} has a runway length of {object_val} meters")
        elif predicate == "iataLocationIdentifier":
            location_info.append(f"{subject} has IATA code {object_val}")
        elif predicate == "location":
            location_info.append(f"{subject} is located in {object_val}")
        elif predicate == "operatingOrganisation":
            other_info.append(f"{subject} is operated by {object_val}")
        elif predicate == "hubAirport":
            other_info.append(f"{subject} is a hub airport for {object_val}")
        elif predicate == "headquarter":
            other_info.append(f"The headquarters of {subject} is in {object_val}")
        elif predicate == "nativeName":
            airport = object_val
        elif predicate == "runwayName":
            runway_info.append(f"{subject} has a runway named {object_val}")
        elif predicate == "runwaySurfaceType":
            runway_info.append(f"The runway surface of {subject} is {object_val}")
        elif predicate == "isPartOf":
            location_info.append(f"{subject} is part of {object_val}")
        elif predicate == "1stRunwayLengthFeet":
            runway_info.append(f"The first runway of {subject} is {object_val} feet long")
        elif predicate == "1stRunwaySurfaceType":
            runway_info.append(f"The first runway of {subject} is made of {object_val}")
        elif predicate == "1stRunwayNumber":
            runway_info.append(f"The first runway of {subject} is number {object_val}")
        elif predicate == "2ndRunwaySurfaceType":
            runway_info.append(f"The second runway of {subject} is made of {object_val}")
        elif predicate == "3rdRunwaySurfaceType":
            runway_info.append(f"The third runway of {subject} is made of {object_val}")
        elif predicate == "4thRunwaySurfaceType":
            runway_info.append(f"The fourth runway of {subject} is made of {object_val}")
        elif predicate == "5thRunwaySurfaceType":
            runway_info.append(f"The fifth runway of {subject} is made of {object_val}")
        else:
            other_info.append(f"{subject} {predicate} {object_val}")

    if not triples:
        return ""

    sentence = ""
    subject = triples[0].subject
    sentence += f"{subject} "

    clauses = []
    for triple in triples:
        predicate = triple.predicate
        object_val = triple.object

        if predicate == "cityServed":
            clauses.append(f"serves the city of {object_val}")
        elif predicate == "country":
            clauses.append(f"is located in {object_val}")
        elif predicate == "elevationAboveTheSeaLevel":
            clauses.append(f"has an elevation of {object_val} meters above sea level")
        elif predicate == "elevationAboveTheSeaLevelInFeet":
            clauses.append(f"has an elevation of {object_val} feet above sea level")
        elif predicate == "runwayLength":
            clauses.append(f"has a runway length of {object_val} meters")
        elif predicate == "iataLocationIdentifier":
            clauses.append(f"has IATA code {object_val}")
        elif predicate == "location":
            clauses.append(f"is located in {object_val}")
        elif predicate == "operatingOrganisation":
            clauses.append(f"is operated by {object_val}")
        elif predicate == "hubAirport":
            clauses.append(f"is a hub airport for {object_val}")
        elif predicate == "headquarter":
            clauses.append(f"has its headquarters in {object_val}")
        elif predicate == "nativeName":
            clauses.append(f"is also known as {object_val}")
        elif predicate == "runwayName":
            clauses.append(f"features runway {object_val}")
        elif predicate == "runwaySurfaceType":
            clauses.append(f"has a runway surface type of {object_val}")
        elif predicate == "isPartOf":
            clauses.append(f"is part of {object_val}")
        elif predicate == "1stRunwayLengthFeet":
            clauses.append(f"has a first runway length of {object_val} feet")
        elif predicate == "1stRunwaySurfaceType":
            clauses.append(f"has a first runway surface type of {object_val}")
        elif predicate == "1stRunwayNumber":
            clauses.append(f"has a first runway numbered {object_val}")
        elif predicate == "2ndRunwaySurfaceType":
            clauses.append(f"has a second runway surface type of {object_val}")
        elif predicate == "3rdRunwaySurfaceType":
            clauses.append(f"has a third runway surface type of {object_val}")
        elif predicate == "4thRunwaySurfaceType":
            clauses.append(f"has a fourth runway surface type of {object_val}")
        elif predicate == "5thRunwaySurfaceType":
            clauses.append(f"has a fifth runway surface type of {object_val}")
        elif predicate == "leaderParty":
            clauses.append(f"is led by the {object_val}")
        elif predicate == "capital":
            clauses.append(f"has {object_val} as its capital")
        elif predicate == "language":
            clauses.append(f"speaks {object_val}")
        elif predicate == "leader":
            clauses.append(f"is led by {object_val}")
        elif predicate == "owner":
            clauses.append(f"is owned by {object_val}")
        elif predicate == "1stRunwayLengthMetre":
            clauses.append(f"has a first runway length of {object_val} meters")
        elif predicate == "largestCity":
            clauses.append(f"has {object_val} as its largest city")
        elif predicate == "4thRunwayLengthFeet":
            clauses.append(f"has a fourth runway length of {object_val} feet")
        elif predicate == "elevationAboveTheSeaLevelInMetres":
            clauses.append(f"has an elevation of {object_val} meters above sea level")
        elif predicate == "administrativeArrondissement":
            clauses.append(f"is in the {object_val}")
        elif predicate == "mayor":
            clauses.append(f"is governed by mayor {object_val}")
        elif predicate == "officialLanguage":
            clauses.append(f"has {object_val} as its official language")
        elif predicate == "city":
            clauses.append(f"is located in {object_val}")
        elif predicate == "jurisdiction":
            clauses.append(f"is under the jurisdiction of {object_val}")
        elif predicate == "demonym":
            clauses.append(f"people are known as {object_val}")
        elif predicate == "aircraftHelicopter":
            clauses.append(f"uses {object_val}")
        elif predicate == "transportAircraft":
            clauses.append(f"uses {object_val}")
        elif predicate == "currency":
            clauses.append(f"uses {object_val} as currency")
        elif predicate == "class":
            clauses.append(f"belongs to the class {object_val}")
        elif predicate == "division":
            clauses.append(f"belongs to the division {object_val}")
        elif predicate == "order":
            clauses.append(f"belongs to the order {object_val}")
        elif predicate == "regionServed":
            clauses.append(f"serves the region of {object_val}")
        elif predicate == "leaderTitle":
            clauses.append(f"is governed by {object_val}")
        elif predicate == "hubAirport":
            clauses.append(f"has {object_val} as its hub airport")
        elif predicate == "aircraftFighter":
            clauses.append(f"uses {object_val}")
        elif predicate == "attackAircraft":
            clauses.append(f"uses {object_val}")
        elif predicate == "battle":
            clauses.append(f"participated in {object_val}")
        elif predicate == "countySeat":
            clauses.append(f"has {object_val} as its county seat")
        elif predicate == "chief":
            clauses.append(f"is led by chief {object_val}")
        elif predicate == "foundedBy":
            clauses.append(f"was founded by {object_val}")
        elif predicate == "postalCode":
            clauses.append(f"has postal code {object_val}")
        elif predicate == "areaCode":
            clauses.append(f"has area code {object_val}")
        elif predicate == "foundingYear":
            clauses.append(f"was founded in {object_val}")
        elif predicate == "ceremonialCounty":
            clauses.append(f"is in the ceremonial county of {object_val}")

    sentence += ", ".join(clauses) + "."
    sentence = sentence[0].upper() + sentence[1:]
    return sentence

# EVOLVE-BLOCK-END