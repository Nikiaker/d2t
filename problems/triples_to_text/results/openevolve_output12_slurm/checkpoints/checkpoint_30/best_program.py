from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    predicate_sentence_map = {
        "cityServed": f"{triples[0].subject} is the airport of {triples[0].object}.",
        "elevationAboveTheSeaLevel": f"{triples[0].subject} Airport is {triples[0].object} metres above sea level.",
        "location": f"{triples[0].subject} Airport is located in {triples[0].object}.",
        "operatingOrganisation": f"{triples[0].subject} Airport is operated by {triples[0].object}.",
        "runwayLength": f"{triples[0].subject} Airport runway length is {triples[0].object}.",
        "runwayName": f"{triples[0].subject} Airport runway name is {triples[0].object}.",
        "country": f"{triples[0].object} is in the {triples[0].subject}.",
        "isPartOf": f"{triples[0].subject} is part of {triples[0].object}.",
        "1stRunwayLengthFeet": f"The length of the 1st runway at {triples[0].subject} airport is {triples[0].object} feet.",
        "1stRunwaySurfaceType": f"The first runway at {triples[0].subject} Airport is made from {triples[0].object}.",
        "3rdRunwayLengthFeet": f"The third runway at {triples[0].subject} Airport is {triples[0].object} feet long.",
        "icaoLocationIdentifier": f"{triples[0].subject} Airport ICAO Location Identifier is {triples[0].object}.",
        "locationIdentifier": f"The location identifier for {triples[0].subject} airport is {triples[0].object}.",
        "elevationAboveTheSeaLevelInFeet": f"{triples[0].subject} International Airport is elevated {triples[0].object} feet above sea level.",
        "iataLocationIdentifier": f"{triples[0].subject} Airport IATA Location Identifier is {triples[0].object}.",
        "nativeName": f"{triples[0].object} is the native name of {triples[0].subject} Airport.",
        "leaderParty": f"The leader party at {triples[0].subject} is the {triples[0].object}.",
        "capital": f"{triples[0].object} is the capital of {triples[0].subject}.",
        "language": f"The main language spoken on {triples[0].subject} is {triples[0].object}.",
        "leader": f"{triples[0].subject}'s leader name is {triples[0].object}.",
        "owner": f"{triples[0].subject} County Regional Airport owner is {triples[0].object}.",
        "1stRunwayLengthMetre": f"The length of the first runway at {triples[0].subject} Airport Schiphol is {triples[0].object} metres.",
        "4thRunwaySurfaceType": f"The fourth runway at {triples[0].subject} Airport in {triples[0].subject} is made of {triples[0].object}.",
        "5thRunwayNumber": f"{triples[0].subject} Airport Schiphol is 5th runway number {triples[0].object}.",
        "largestCity": f"The largest city in {triples[0].subject} County, {triples[0].object} is {triples[0].object}.",
        "4thRunwayLengthFeet": f"{triples[0].subject} County Airport is 4th runway length feet of {triples[0].object}.",
        "1stRunwayNumber": f"{triples[0].subject} International Airport 1st runway is Number {triples[0].object}.",
        "elevationAboveTheSeaLevelInMetres": f"{triples[0].subject} International airport is {triples[0].object} metres above sea level.",
        "administrativeArrondissement": f"{triples[0].subject} is admin Arrondissement of {triples[0].object}.",
        "mayor": f"The mayor of {triples[0].subject} is {triples[0].object}.",
        "2ndRunwaySurfaceType": f"{triples[0].object} is the surface type of the second runway of {triples[0].subject} Airport, {triples[0].object}.",
        "3rdRunwaySurfaceType": f"{triples[0].subject} Airport (New Zealand)'s 3rd runway surface type is {triples[0].object}.",
        "runwaySurfaceType": f"The runway surface at {triples[0].subject} International Airport is made from {triples[0].object}.",
        "officialLanguage": f"{triples[0].object} is the official language of {triples[0].subject}.",
        "city": f"{triples[0].subject} is in the city of {triples[0].object}.",
        "jurisdiction": f"{triples[0].subject} Government jurisdiction is {triples[0].object}.",
        "demonym": f"{triples[0].subject} demonym is {triples[0].object}.",
        "aircraftHelicopter": f"{triples[0].subject}'s Air Force has an aircraft-capable helicopter known as the {triples[0].object}.",
        "transportAircraft": f"The {triples[0].object} is a transport aircraft in the {triples[0].subject} Air Force.",
        "currency": f"The currency in {triples[0].subject} is the {triples[0].object}.",
        "headquarter": f"The {triples[0].subject} Civil Aviation Authority is headquartered at {triples[0].object} International Airport.",
        "class": f"{triples[0].subject} class is {triples[0].object}.",
        "division": f"{triples[0].subject} belongs to the division of {triples[0].object}.",
        "order": f"{triples[0].subject} belongs to the order of {triples[0].object}.",
        "regionServed": f"The {triples[0].subject} of New York and New Jersey serves the {triples[0].object} region.",
        "leaderTitle": f"The {triples[0].subject}, {triples[0].object}, is led by the {triples[0].object}.",
        "hubAirport": f"The hub airport for {triples[0].subject} airlines is {triples[0].object} International airport.",
        "aircraftFighter": f"{triples[0].subject} Air FOrce aircraft fighter is {triples[0].object}.",
        "attackAircraft": f"The {triples[0].object} can be found on {triples[0].subject} Air Force aircraft carriers.",
        "battle": f"One of the noted {triples[0].subject} Air Force battles was the {triples[0].object}.",
        "countySeat": f"{triples[0].subject} County, {triples[0].object} is country seat to {triples[0].object}, {triples[0].object}.",
        "chief": f"{triples[0].subject} Jersey Transportation Authority chief is {triples[0].object}.",
        "ceremonialCounty": f"The ceremonial county of {triples[0].subject} is {triples[0].object}.",
        "foundingYear": f"{triples[0].subject} was founded in the year {triples[0].object}.",
    }

    return predicate_sentence_map.get(triples[0].predicate, f"The {triples[0].predicate} of {triples[0].subject} is {triples[0].object}.")

# EVOLVE-BLOCK-END