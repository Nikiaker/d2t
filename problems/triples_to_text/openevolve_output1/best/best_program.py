from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triple: Triple) -> str:
    # Determine the type of object and provide more context
    if triple.object.isdigit() or triple.object.replace('.', '', 1).replace('-', '', 1).isdigit():
        # Handle numeric objects
        if triple.predicate == "elevationAboveTheSeaLevel" or triple.predicate == "elevationAboveTheSeaLevelInFeet":
            return f"{triple.subject} has an elevation of {triple.object} {triple.predicate} above sea level."
        elif triple.predicate == "runwayLength":
            return f"The runway length of {triple.subject} is {triple.object} {triple.predicate}."
        elif triple.predicate == "1stRunwayLengthFeet":
            return f"The length of the first runway at {triple.subject} is {triple.object} {triple.predicate}."
        elif triple.predicate == "3rdRunwayLengthFeet":
            return f"The third runway at {triple.subject} is {triple.object} {triple.predicate} feet long."
        else:
            return f"{triple.subject} has a {triple.predicate} of {triple.object}."
    elif triple.object.isalpha():
        # Handle string objects
        return f"{triple.subject} is {triple.predicate} by {triple.object}."
    else:
        # Handle other types of objects
        return f"{triple.subject} has a {triple.predicate} of {triple.object}."

# EVOLVE-BLOCK-END