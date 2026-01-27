from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    sentence = ""
    subject = ""
    for i, triple in enumerate(triples):
        if i == 0:
            subject = triple.subject
            sentence += f"{subject} "
        if triple.predicate == "category":
            sentence += f"is a {triple.object}. "
        elif triple.predicate == "country":
            country = triple.object
        elif triple.predicate == "location":
            if "country" in locals():
                sentence += f"is located in {triple.object}, which is in {country}. "
            else:
                sentence += f"is located in {triple.object}. "
        elif triple.predicate == "municipality":
            sentence += f"is in the municipality of {triple.object}. "
        elif triple.predicate == "state":
            sentence += f"is in the state of {triple.object}. "
        elif triple.predicate == "district":
            sentence += f"is in the {triple.object}. "
        elif triple.predicate == "established" or triple.predicate == "foundingDate" or triple.predicate == "inaugurationDate":
            sentence += f"was established on {triple.object}. "
        elif triple.predicate == "owner" or triple.predicate == "owningOrganisation":
            sentence += f"is owned by {triple.object}. "
        elif triple.predicate == "hasToItsNorth":
            sentence += f"has {triple.object} to its north. "
        elif triple.predicate == "hasToItsSouthwest":
            sentence += f"has {triple.object} to its southwest. "
        elif triple.predicate == "hasToItsWest":
            sentence += f"has {triple.object} to its west. "
        elif triple.predicate == "hasToItsSoutheast":
            sentence += f"has {triple.object} to its southeast. "
        elif triple.predicate == "dedicatedTo":
            sentence += f"is dedicated to {triple.object}. "
        elif triple.predicate == "designer":
            sentence += f"was designed by {triple.object}. "
        elif triple.predicate == "material":
            sentence += f"is made of {triple.object}. "
        elif triple.predicate == "ethnicGroup":
            sentence += f"has an ethnic group of {triple.object}. "
        elif triple.predicate == "language":
            sentence += f"has a language of {triple.object}. "
        elif triple.predicate == "religion":
            sentence += f"has a religion of {triple.object}. "
        elif triple.predicate == "nearestCity":
            sentence += f"is near {triple.object}. "
        elif triple.predicate == "currency":
            sentence += f"and its currency is the {triple.object}. "
        elif triple.predicate == "largestCity":
            sentence += f"’s largest city is {triple.object}. "
        elif triple.predicate == "leader":
            sentence += f"’s leader is {triple.object}. "
        elif triple.predicate == "leaderTitle":
            sentence += f"’s leader’s title is {triple.object}. "
        elif triple.predicate == "nativeName":
            sentence += f"is also known as {triple.object}. "
        else:
            if i > 0:
                sentence += f" and "
            sentence += f"has a {triple.predicate} of {triple.object}. "
    return sentence

# EVOLVE-BLOCK-END