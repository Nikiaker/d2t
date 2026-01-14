from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    sentences = []
    predicates = {
        "cityServed": lambda triple: f"{triple.subject} serves the city of {triple.object}.",
        "elevationAboveTheSeaLevel": lambda triple: f"{triple.subject} is {triple.object} meters above sea level.",
        "location": lambda triple: f"{triple.subject} is located in {triple.object}.",
        "operatingOrganisation": lambda triple: f"{triple.subject} is operated by {triple.object}.",
        "runwayLength": lambda triple: f"The runway length of {triple.subject} is {triple.object} meters.",
        "runwayName": lambda triple: f"The runway name of {triple.subject} is {triple.object}.",
        "country": lambda triple: f"{triple.subject} is located in {triple.object}.",
        "isPartOf": lambda triple: f"{triple.subject} is part of {triple.object}.",
        "1stRunwayLengthFeet": lambda triple: f"The length of the first runway at {triple.subject} is {triple.object} feet.",
        "1stRunwaySurfaceType": lambda triple: f"The first runway at {triple.subject} is made of {triple.object}.",
        "3rdRunwayLengthFeet": lambda triple: f"The length of the third runway at {triple.subject} is {triple.object} feet.",
        "icaoLocationIdentifier": lambda triple: f"The ICAO location identifier of {triple.subject} is {triple.object}.",
        "locationIdentifier": lambda triple: f"The location identifier of {triple.subject} is {triple.object}.",
        "elevationAboveTheSeaLevelInFeet": lambda triple: f"{triple.subject} is {triple.object} feet above sea level.",
        "iataLocationIdentifier": lambda triple: f"The IATA location identifier of {triple.subject} is {triple.object}.",
        "nativeName": lambda triple: f"The native name of {triple.subject} is {triple.object}.",
        "leaderParty": lambda triple: f"The leader party of {triple.subject} is {triple.object}.",
        "capital": lambda triple: f"The capital of {triple.subject} is {triple.object}.",
        "language": lambda triple: f"The language of {triple.subject} is {triple.object}.",
        "leader": lambda triple: f"The leader of {triple.subject} is {triple.object}.",
        "owner": lambda triple: f"The owner of {triple.subject} is {triple.object}.",
        "4thRunwaySurfaceType": lambda triple: f"The fourth runway at {triple.subject} is made of {triple.object}.",
        "5thRunwayNumber": lambda triple: f"The fifth runway at {triple.subject} has the number {triple.object}.",
        "largestCity": lambda triple: f"The largest city in {triple.subject} is {triple.object}.",
        "4thRunwayLengthFeet": lambda triple: f"The length of the fourth runway at {triple.subject} is {triple.object} feet.",
        "1stRunwayNumber": lambda triple: f"The first runway at {triple.subject} has the number {triple.object}.",
        "elevationAboveTheSeaLevelInMetres": lambda triple: f"{triple.subject} is {triple.object} meters above sea level.",
        "administrativeArrondissement": lambda triple: f"The administrative arrondissement of {triple.subject} is {triple.object}.",
        "mayor": lambda triple: f"The mayor of {triple.subject} is {triple.object}.",
        "2ndRunwaySurfaceType": lambda triple: f"The second runway at {triple.subject} is made of {triple.object}.",
        "3rdRunwaySurfaceType": lambda triple: f"The third runway at {triple.subject} is made of {triple.object}.",
        "runwaySurfaceType": lambda triple: f"The runway surface type of {triple.subject} is {triple.object}.",
        "officialLanguage": lambda triple: f"The official language of {triple.subject} is {triple.object}.",
        "city": lambda triple: f"The city of {triple.subject} is {triple.object}.",
        "jurisdiction": lambda triple: f"The jurisdiction of {triple.subject} is {triple.object}.",
        "demonym": lambda triple: f"The demonym of {triple.subject} is {triple.object}.",
        "aircraftHelicopter": lambda triple: f"The aircraft helicopter of {triple.subject} is {triple.object}.",
        "transportAircraft": lambda triple: f"The transport aircraft of {triple.subject} is {triple.object}.",
        "currency": lambda triple: f"The currency of {triple.subject} is {triple.object}.",
        "headquarter": lambda triple: f"The headquarter of {triple.subject} is {triple.object}.",
        "class": lambda triple: f"The class of {triple.subject} is {triple.object}.",
        "division": lambda triple: f"The division of {triple.subject} is {triple.object}.",
        "order": lambda triple: f"The order of {triple.subject} is {triple.object}.",
        "regionServed": lambda triple: f"The region served by {triple.subject} is {triple.object}.",
        "leaderTitle": lambda triple: f"The leader title of {triple.subject} is {triple.object}.",
        "hubAirport": lambda triple: f"The hub airport of {triple.subject} is {triple.object}.",
        "aircraftFighter": lambda triple: f"The aircraft fighter of {triple.subject} is {triple.object}.",
        "attackAircraft": lambda triple: f"The attack aircraft of {triple.subject} is {triple.object}.",
        "battle": lambda triple: f"{triple.subject} fought in the {triple.object}.",
    }
    for triple in triples:
        if triple.predicate in predicates:
            sentences.append(predicates[triple.predicate](triple))
        else:
            # Attempt to generate a more meaningful sentence for unknown predicates
            if triple.predicate.endswith("Length"):
                sentences.append(f"The {triple.predicate.replace('Length', '')} at {triple.subject} measures {triple.object}.")
            elif triple.predicate.endswith("SurfaceType"):
                sentences.append(f"The {triple.predicate.replace('SurfaceType', '')} at {triple.subject} is made of {triple.object}.")
            elif triple.predicate.endswith("Identifier"):
                sentences.append(f"{triple.subject} has the {triple.predicate.replace('Identifier', 'identifier')} {triple.object}.")
            elif triple.predicate.endswith("Year"):
                sentences.append(f"{triple.subject} was established in the year {triple.object}.")
            elif triple.predicate.endswith("Code"):
                sentences.append(f"{triple.subject} has the {triple.predicate.replace('Code', 'code')} {triple.object}.")
            else:
                # Attempt to generate a more informative sentence for unknown predicates
                if triple.subject.lower().startswith("airport"):
                    sentences.append(f"{triple.subject} has a {triple.predicate} of {triple.object}.")
                else:
                    sentences.append(f"The {triple.predicate} of {triple.subject} is {triple.object}.")
    return ". ".join(sentences) + "."

# EVOLVE-BLOCK-END