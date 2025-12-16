from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triple: Triple) -> str:
    if triple.predicate in ['elevationAboveTheSeaLevel', 'elevationAboveTheSeaLevelInFeet']:
        return f"{triple.subject} airport is {triple.object} {triple.predicate} above sea level."
    elif triple.predicate in ['runwayLength', '1stRunwayLengthFeet', '3rdRunwayLengthFeet', '4thRunwayLengthFeet', '1stRunwayLengthMetre']:
        return f"{triple.subject} Airport runway length is {triple.object} {triple.predicate}."
    else:
        return f"The {triple.predicate} of {triple.subject} is {triple.object}."

# EVOLVE-BLOCK-END