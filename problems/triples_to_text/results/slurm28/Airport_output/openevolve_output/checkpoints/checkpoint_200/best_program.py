from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    subject_map = {}
    for triple in triples:
        if triple.subject not in subject_map:
            subject_map[triple.subject] = []
        subject_map[triple.subject].append((triple.predicate, triple.object))

    sentence = ""
    for subject, triples in subject_map.items():
        if sentence:
            sentence += " which "
        sentence += f"{subject} "
        for i, (predicate, obj) in enumerate(triples):
            if predicate == "cityServed":
                sentence += f"serves the city of {obj}"
            elif predicate == "mayor":
                sentence += f"where the mayor is {obj}"
            elif predicate == "isPartOf":
                sentence += f"is part of {obj}"
            elif predicate == "operatingOrganisation":
                sentence += f"is operated by {obj}"
            elif predicate == "location":
                sentence += f"is located in {obj}"
            elif predicate == "elevationAboveTheSeaLevel":
                sentence += f"has an elevation of {obj} metres above sea level"
            elif predicate == "runwayLength":
                sentence += f"has a runway length of {obj} metres"
            elif predicate == "country":
                sentence += f"is located in {obj}"
            elif predicate == "capital":
                sentence += f"has {obj} as its capital"
            elif predicate == "language":
                sentence += f"speaks {obj}"
            elif predicate == "leader":
                sentence += f"has a leader of {obj}"
            elif predicate == "owner":
                sentence += f"is owned by {obj}"
            elif predicate == "1stRunwayLengthFeet":
                sentence += f"has a first runway length of {obj} feet"
            elif predicate == "1stRunwaySurfaceType":
                sentence += f"has a first runway surface type of {obj}"
            elif predicate == "3rdRunwayLengthFeet":
                sentence += f"has a third runway length of {obj} feet"
            elif predicate == "icaoLocationIdentifier":
                sentence += f"has an ICAO location identifier of {obj}"
            elif predicate == "locationIdentifier":
                sentence += f"has a location identifier of {obj}"
            elif predicate == "elevationAboveTheSeaLevelInFeet":
                sentence += f"has an elevation of {obj} feet above sea level"
            elif predicate == "iataLocationIdentifier":
                sentence += f"has an IATA location identifier of {obj}"
            elif predicate == "nativeName":
                sentence += f"has a native name of {obj}"
            elif predicate == "leaderParty":
                sentence += f"has a leader party of {obj}"
            elif predicate == "runwayName":
                sentence += f"has a runway named {obj}"
            elif predicate == "runwaySurfaceType":
                sentence += f"has a runway surface type of {obj}"
            elif predicate == "elevationAboveTheSeaLevelInMetres":
                sentence += f"has an elevation of {obj} metres above sea level"
            else:
                sentence += f"has a {predicate} of {obj}"
            if i < len(triples) - 1:
                if predicate in ["location", "country", "isPartOf", "operatingOrganisation", "cityServed"]:
                    sentence += " and "
                else:
                    sentence += ", "
    return sentence + "."