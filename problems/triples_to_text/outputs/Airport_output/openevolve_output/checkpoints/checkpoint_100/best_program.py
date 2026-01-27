from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    sentence = ""
    subject = ""
    for triple in triples:
        if not subject:
            subject = triple.subject
            sentence += f"{subject} "

        if triple.predicate == "cityServed":
            sentence += f"serves the city of {triple.object}. "
        elif triple.predicate == "elevationAboveTheSeaLevel":
            sentence += f"has an elevation of {triple.object} meters above sea level. "
        elif triple.predicate == "location":
            sentence += f"is located in {triple.object}. "
        elif triple.predicate == "operatingOrganisation":
            sentence += f"is operated by {triple.object}. "
        elif triple.predicate == "runwayLength":
            sentence += f"has a runway length of {triple.object} meters. "
        elif triple.predicate == "runwayName":
            sentence += f"has a runway named {triple.object}. "
        elif triple.predicate == "country":
            sentence += f"is in {triple.object}. "
        elif triple.predicate == "isPartOf":
            sentence += f"is part of {triple.object}. "
        elif triple.predicate == "1stRunwayLengthFeet":
            sentence += f"has a first runway length of {triple.object} feet. "
        elif triple.predicate == "1stRunwaySurfaceType":
            sentence += f"has a first runway surface type of {triple.object}. "
        elif triple.predicate == "3rdRunwayLengthFeet":
            sentence += f"has a third runway length of {triple.object} feet. "
        elif triple.predicate == "icaoLocationIdentifier":
            sentence += f"has an ICAO location identifier of {triple.object}. "
        elif triple.predicate == "locationIdentifier":
            sentence += f"has a location identifier of {triple.object}. "
        elif triple.predicate == "elevationAboveTheSeaLevelInFeet":
            sentence += f"has an elevation of {triple.object} feet above sea level. "
        elif triple.predicate == "iataLocationIdentifier":
            sentence += f"has an IATA location identifier of {triple.object}. "
        elif triple.predicate == "nativeName":
            sentence += f"is also known as {triple.object}. "
        elif triple.predicate == "leaderParty":
            sentence += f"is led by the {triple.object}. "
        elif triple.predicate == "capital":
            sentence += f"has {triple.object} as its capital. "
        elif triple.predicate == "language":
            sentence += f"speaks {triple.object}. "
        elif triple.predicate == "leader":
            sentence += f"is led by {triple.object}. "
        elif triple.predicate == "owner":
            sentence += f"is owned by {triple.object}. "
        elif triple.predicate == "1stRunwayLengthMetre":
            sentence += f"has a first runway length of {triple.object} metres. "
        elif triple.predicate == "4thRunwaySurfaceType":
            sentence += f"has a fourth runway surface type of {triple.object}. "
        elif triple.predicate == "5thRunwayNumber":
            sentence += f"has a fifth runway number of {triple.object}. "
        elif triple.predicate == "largestCity":
            sentence += f"has {triple.object} as its largest city. "
        elif triple.predicate == "4thRunwayLengthFeet":
            sentence += f"has a fourth runway length of {triple.object} feet. "
        elif triple.predicate == "1stRunwayNumber":
            sentence += f"has a first runway number of {triple.object}. "
        elif triple.predicate == "elevationAboveTheSeaLevelInMetres":
            sentence += f"has an elevation of {triple.object} metres above sea level. "
        elif triple.predicate == "administrativeArrondissement":
            sentence += f"is in the {triple.object}. "
        elif triple.predicate == "mayor":
            sentence += f"is led by mayor {triple.object}. "
        elif triple.predicate == "2ndRunwaySurfaceType":
            sentence += f"has a second runway surface type of {triple.object}. "
        elif triple.predicate == "3rdRunwaySurfaceType":
            sentence += f"has a third runway surface type of {triple.object}. "
        elif triple.predicate == "runwaySurfaceType":
            sentence += f"has a runway surface type of {triple.object}. "
        elif triple.predicate == "officialLanguage":
            sentence += f"has {triple.object} as an official language. "
        elif triple.predicate == "city":
            sentence += f"is located in {triple.object}. "
        elif triple.predicate == "jurisdiction":
            sentence += f"is under the jurisdiction of {triple.object}. "
        elif triple.predicate == "demonym":
            sentence += f"people are called {triple.object}. "
        elif triple.predicate == "aircraftHelicopter":
            sentence += f"uses {triple.object}. "
        elif triple.predicate == "transportAircraft":
            sentence += f"uses {triple.object}. "
        elif triple.predicate == "currency":
            sentence += f"uses {triple.object}. "
        elif triple.predicate == "headquarter":
            sentence += f"has its headquarter at {triple.object}. "
        elif triple.predicate == "class":
            sentence += f"belongs to the {triple.object} class. "
        elif triple.predicate == "division":
            sentence += f"belongs to the {triple.object} division. "
        elif triple.predicate == "order":
            sentence += f"belongs to the {triple.object} order. "
        elif triple.predicate == "regionServed":
            sentence += f"serves the {triple.object} region. "
        elif triple.predicate == "leaderTitle":
            sentence += f"has a leader title of {triple.object}. "
        elif triple.predicate == "hubAirport":
            sentence += f"has {triple.object} as its hub airport. "
        elif triple.predicate == "aircraftFighter":
            sentence += f"uses {triple.object}. "
        elif triple.predicate == "attackAircraft":
            sentence += f"uses {triple.object}. "
        elif triple.predicate == "battle":
            sentence += f"participated in {triple.object}. "
        elif triple.predicate == "5thRunwaySurfaceType":
            sentence += f"has a fifth runway surface type of {triple.object}. "
        elif triple.predicate == "countySeat":
            sentence += f"has {triple.object} as its county seat. "
        elif triple.predicate == "chief":
            sentence += f"is led by chief {triple.object}. "
        elif triple.predicate == "foundedBy":
            sentence += f"was founded by {triple.object}. "
        elif triple.predicate == "postalCode":
            sentence += f"has a postal code of {triple.object}. "
        elif triple.predicate == "areaCode":
            sentence += f"has an area code of {triple.object}. "
        elif triple.predicate == "foundingYear":
            sentence += f"was founded in {triple.object}. "
        elif triple.predicate == "ceremonialCounty":
            sentence += f"is in the ceremonial county of {triple.object}. "

    return sentence

# EVOLVE-BLOCK-END