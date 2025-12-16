from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triple: Triple) -> str:
    if triple.predicate == "elevationAboveTheSeaLevelInMetres" or triple.predicate == "elevationAboveTheSeaLevel":
        return f"{triple.subject} airport is {triple.object} metres above sea level."
    elif triple.predicate == "runwayLength":
        return f"The runway length of {triple.subject} is {triple.object} metres."
    elif triple.predicate == "runwaySurfaceType":
        return f"The runway surface type at {triple.subject} is {triple.object}."
    else:
        return f"The {triple.predicate} of {triple.subject} is {triple.object}."

# EVOLVE-BLOCK-END