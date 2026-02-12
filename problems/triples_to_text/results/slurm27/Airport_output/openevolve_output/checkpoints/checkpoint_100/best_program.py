from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    subjects = {}
    for triple in triples:
        if triple.subject not in subjects:
            subjects[triple.subject] = []
        subjects[triple.subject].append((triple.predicate, triple.object))

    sentence = ""
    for subject, triples_list in subjects.items():
        sentence += f"{subject} "
        for i, (predicate, obj) in enumerate(triples_list):
            if predicate == "cityServed":
                sentence += f"serves the city of {obj} "
            elif predicate == "location":
                sentence += f"is located in {obj} "
            elif predicate == "elevationAboveTheSeaLevel":
                sentence += f"which is {obj} metres above sea level "
            elif predicate == "elevationAboveTheSeaLevelInFeet":
                sentence += f"which is {obj} feet above sea level "
            elif predicate == "runwayLength":
                sentence += f"and has a runway length of {obj} metres "
            elif predicate == "runwayName":
                sentence += f"with a runway named {obj} "
            elif predicate == "country":
                sentence += f"in {obj} "
            elif predicate == "isPartOf":
                sentence += f"which is part of {obj} "
            elif predicate == "language":
                sentence += f"where the language spoken is {obj} "
            elif predicate == "capital":
                sentence += f"where the capital is {obj} "
            elif predicate == "nativeName":
                sentence += f"also known as {obj} "
            elif predicate == "iataLocationIdentifier":
                sentence += f"with the IATA code {obj} "
            elif predicate == "icaoLocationIdentifier":
                sentence += f"and the ICAO code {obj} "
            elif predicate == "operatingOrganisation":
                sentence += f"operated by {obj} "
            elif predicate == "leader":
                sentence += f"led by {obj} "
            elif predicate == "owner":
                sentence += f"owned by {obj} "
            elif predicate == "1stRunwayLengthFeet":
                sentence += f"with the first runway length of {obj} feet "
            elif predicate == "1stRunwaySurfaceType":
                sentence += f"with the first runway surface type of {obj} "
            elif predicate == "3rdRunwayLengthFeet":
                sentence += f"with the third runway length of {obj} feet "
            elif predicate == "3rdRunwaySurfaceType":
                sentence += f"with the third runway surface type of {obj} "
            elif predicate == "4thRunwayLengthFeet":
                sentence += f"with the fourth runway length of {obj} feet "
            elif predicate == "4thRunwaySurfaceType":
                sentence += f"with the fourth runway surface type of {obj} "
            elif predicate == "5thRunwayNumber":
                sentence += f"with the fifth runway number of {obj} "
            elif predicate == "5thRunwaySurfaceType":
                sentence += f"with the fifth runway surface type of {obj} "
            elif predicate == "administrativeArrondissement":
                sentence += f"in the administrative arrondissement of {obj} "
            elif predicate == "areaCode":
                sentence += f"with the area code of {obj} "
            elif predicate == "ceremonialCounty":
                sentence += f"in the ceremonial county of {obj} "
            elif predicate == "chief":
                sentence += f"with the chief of {obj} "
            elif predicate == "countySeat":
                sentence += f"with the county seat of {obj} "
            elif predicate == "currency":
                sentence += f"with the currency of {obj} "
            elif predicate == "demonym":
                sentence += f"with the demonym of {obj} "
            elif predicate == "foundingYear":
                sentence += f"founded in the year {obj} "
            elif predicate == "headquarter":
                sentence += f"with the headquarter of {obj} "
            elif predicate == "hubAirport":
                sentence += f"with the hub airport of {obj} "
            elif predicate == "jurisdiction":
                sentence += f"with the jurisdiction of {obj} "
            elif predicate == "largestCity":
                sentence += f"with the largest city of {obj} "
            elif predicate == "leaderParty":
                sentence += f"with the leader party of {obj} "
            elif predicate == "leaderTitle":
                sentence += f"with the leader title of {obj} "
            elif predicate == "locationIdentifier":
                sentence += f"with the location identifier of {obj} "
            elif predicate == "mayor":
                sentence += f"with the mayor of {obj} "
            elif predicate == "officialLanguage":
                sentence += f"with the official language of {obj} "
            elif predicate == "postalCode":
                sentence += f"with the postal code of {obj} "
            elif predicate == "regionServed":
                sentence += f"with the region served of {obj} "
            elif predicate == "transportAircraft":
                sentence += f"with the transport aircraft of {obj} "
            if i < len(triples_list) - 1:
                sentence += ", "
        sentence += ". "

    # Remove the extra ". " at the end and add a period at the end of the sentence
    sentence = sentence.strip()[:-1] + "."

    return sentence

# EVOLVE-BLOCK-END