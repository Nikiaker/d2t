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

    sentences = []
    for subject, triples in subject_map.items():
        base_sentence = ""
        clauses = []

        for predicate, obj in triples:
            if predicate == "cityServed":
                clauses.append(f"serves the city of {obj}")
            elif predicate == "mayor":
                clauses.append(f"where the mayor is {obj}")
            elif predicate == "isPartOf":
                clauses.append(f"is part of {obj}")
            elif predicate == "operatingOrganisation":
                clauses.append(f"is operated by {obj}")
            elif predicate == "location":
                clauses.append(f"is located in {obj}")
            elif predicate == "elevationAboveTheSeaLevel":
                clauses.append(f"has an elevation of {obj} metres above sea level")
            elif predicate == "runwayLength":
                base_sentence = f"The runway length of {subject} is {obj} metres"
            elif predicate == "country":
                clauses.append(f"is located in {obj}")
            elif predicate == "capital":
                clauses.append(f"has {obj} as its capital")
            elif predicate == "language":
                base_sentence = f"The language of {subject} is {obj}"
            elif predicate == "leader":
                base_sentence = f"The leader of {subject} is {obj}"
            elif predicate == "owner":
                clauses.append(f"is owned by {obj}")
            elif predicate == "1stRunwayLengthFeet":
                base_sentence = f"The length of the 1st runway at {subject} is {obj} feet"
            elif predicate == "1stRunwaySurfaceType":
                clauses.append(f"has a first runway surface type of {obj}")
            elif predicate == "3rdRunwayLengthFeet":
                base_sentence = f"The length of the 3rd runway at {subject} is {obj} feet"
            elif predicate == "icaoLocationIdentifier":
                base_sentence = f"The ICAO location identifier for {subject} is {obj}"
            elif predicate == "locationIdentifier":
                base_sentence = f"The location identifier for {subject} is {obj}"
            elif predicate == "elevationAboveTheSeaLevelInFeet":
                clauses.append(f"has an elevation of {obj} feet above sea level")
            elif predicate == "iataLocationIdentifier":
                base_sentence = f"The IATA location identifier for {subject} is {obj}"
            elif predicate == "nativeName":
                clauses.append(f"has a native name of {obj}")
            elif predicate == "leaderParty":
                clauses.append(f"has a leader party of {obj}")
            elif predicate == "runwayName":
                base_sentence = f"The runway name of {subject} is {obj}"
            elif predicate == "runwaySurfaceType":
                clauses.append(f"has a runway surface type of {obj}")
            elif predicate == "elevationAboveTheSeaLevelInMetres":
                clauses.append(f"has an elevation of {obj} metres above sea level")
            else:
                clauses.append(f"has a {predicate} of {obj}")

        if base_sentence:
            if clauses:
                base_sentence += " and " + ", ".join(clauses)
            sentence = base_sentence
        else:
            sentence = subject
            if clauses:
                sentence += " " + ", ".join(clauses)

        sentences.append(sentence)

    result = " and ".join(sentences)
    return result + "." if result else "."