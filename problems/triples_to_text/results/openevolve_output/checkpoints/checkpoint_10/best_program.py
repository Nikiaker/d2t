from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triple: Triple) -> str:
    if triple.predicate in ["elevationAboveTheSeaLevel", "elevationAboveTheSeaLevelInMetres"]:
        return f"{triple.subject} airport is {triple.object} metres above sea level."
    elif triple.predicate in ["runwayLength", "runwayLengthFeet", "runwayLengthMetre"]:
        return f"The runway length of {triple.subject} airport is {triple.object} {['metres', 'feet'][triple.predicate == 'runwayLengthFeet']} long."
    elif triple.predicate in ["runwayName"]:
        return f"The runway name of {triple.subject} airport is {triple.object}."
    else:
        return f"The {triple.predicate} of {triple.subject} is {triple.object}."

# EVOLVE-BLOCK-END