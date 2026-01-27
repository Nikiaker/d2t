from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    sentence = ""
    first_triple = True
    for triple in triples:
        if triple.predicate == "cityServed":
            if first_triple:
                sentence += f"{triple.subject} serves the city of {triple.object}."
            else:
                sentence += f" which serves the city of {triple.object}."
        elif triple.predicate == "country":
            if first_triple:
                sentence += f"{triple.subject} is located in {triple.object}."
            else:
                sentence += f" and is in {triple.object}."
        elif triple.predicate == "capital":
            if first_triple:
                sentence += f"The capital of {triple.subject} is {triple.object}."
            else:
                sentence += f", where the capital is {triple.object}."
        elif triple.predicate == "elevationAboveTheSeaLevel":
            if first_triple:
                sentence += f"{triple.subject} is {triple.object} meters above sea level."
            else:
                sentence += f" and has an elevation of {triple.object} meters above sea level."
        elif triple.predicate == "location":
            if first_triple:
                sentence += f"{triple.subject} is located in {triple.object}."
            else:
                sentence += f", and is located in {triple.object}."
        elif triple.predicate == "operatingOrganisation":
            if first_triple:
                sentence += f"{triple.subject} is operated by {triple.object}."
            else:
                sentence += f", and is operated by {triple.object}."
        elif triple.predicate == "runwayLength":
            if first_triple:
                sentence += f"The runway length of {triple.subject} is {triple.object} meters."
            else:
                sentence += f", and has a runway length of {triple.object} meters."
        elif triple.predicate == "runwayName":
            if first_triple:
                sentence += f"The runway name of {triple.subject} is {triple.object}."
            else:
                sentence += f", and its runway name is {triple.object}."
        else:
            if triple.predicate == "isPartOf":
                if first_triple:
                    sentence += f"{triple.subject} is part of {triple.object}."
                else:
                    sentence += f" which is part of {triple.object}."
            elif triple.predicate == "elevationAboveTheSeaLevelInFeet":
                if first_triple:
                    sentence += f"{triple.subject} is {triple.object} feet above sea level."
                else:
                    sentence += f" and is {triple.object} feet above sea level."
            elif triple.predicate == "elevationAboveTheSeaLevelInMetres":
                if first_triple:
                    sentence += f"{triple.subject} is {triple.object} metres above sea level."
                else:
                    sentence += f" and is {triple.object} metres above sea level."
            else:
                if first_triple:
                    sentence += f"{triple.subject} {triple.predicate} {triple.object}."
                else:
                    sentence += f" and {triple.predicate} is {triple.object}."
        first_triple = False
    return sentence.strip()

    return sentence.strip()

# EVOLVE-BLOCK-END