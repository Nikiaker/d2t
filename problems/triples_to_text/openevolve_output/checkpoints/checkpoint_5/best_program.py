from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triple: Triple) -> str:
    # Handle different types of objects and provide more context
    if triple.object.isnumeric():
        object_type = "length"
    elif triple.object.lower() in ["yes", "no"]:
        object_type = "status"
    else:
        object_type = "other"

    if triple.predicate == "location":
        return f"{triple.subject} is located in {triple.object}."
    elif triple.predicate == "cityServed":
        return f"{triple.subject} serves the city of {triple.object}."
    elif triple.predicate == "elevationAboveTheSeaLevel":
        return f"{triple.subject} is {triple.object} metres above sea level."
    elif triple.predicate == "runwayLength":
        return f"The runway length of {triple.subject} is {triple.object} {object_type}."
    elif triple.predicate == "runwayName":
        return f"The runway name of {triple.subject} is {triple.object}."
    else:
        return f"{triple.subject} has a {triple.predicate} of {triple.object}."

# EVOLVE-BLOCK-END