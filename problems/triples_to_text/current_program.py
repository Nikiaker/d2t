from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    sentence = ""
    for i, triple in enumerate(triples):
        if i > 0:
            sentence += " and "
        subject = triple.subject
        predicate = triple.predicate
        object = triple.object
        if predicate == "cityServed":
            sentence += f"{subject} serves the city of {object} which is in "
        elif predicate == "country":
            sentence += f"located in {object}, "
        elif predicate == "elevationAboveTheSeaLevel":
            sentence += f"located at an elevation of {object} meters above the sea level, "
        elif predicate == "location":
            sentence += f"located at {object}, "
        elif predicate == "operatingOrganisation":
            sentence += f"operated by {object}, "
        elif predicate == "runwayLength":
            sentence += f"with a runway length of {object} meters, "
        elif predicate == "runwayName":
            sentence += f"with a runway name of {object}, "
        else:
            sentence += f"with a {predicate} of {object}, "
    return sentence.strip() + "."

# EVOLVE-BLOCK-END