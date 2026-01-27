from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    sentence = ""
    for triple in triples:
        if triple.predicate == "architecturalStyle":
            sentence += f"{triple.subject} is built in {triple.object} style. "
        elif triple.predicate == "buildingStartDate":
            sentence += f"Construction of {triple.subject} started in {triple.object}. "
        elif triple.predicate == "completionDate":
            sentence += f"{triple.subject} was completed in {triple.object}. "
        elif triple.predicate == "floorCount":
            sentence += f"{triple.subject} has {triple.object} floors. "
        elif triple.predicate == "location":
            sentence += f"{triple.subject} is located in {triple.object}. "
        elif triple.predicate == "cost":
            sentence += f"The cost of {triple.subject} was {triple.object}. "
        elif triple.predicate == "floorArea":
            sentence += f"{triple.subject} has a floor area of {triple.object}. "
        elif triple.predicate == "owner":
            sentence += f"{triple.subject} is owned by {triple.object}. "
        elif triple.predicate == "formerName":
            sentence += f"{triple.subject} was formerly known as {triple.object}. "
        elif triple.predicate == "height":
            sentence += f"The height of {triple.subject} is {triple.object} meters. "
        elif triple.predicate == "buildingType":
            sentence += f"{triple.subject} is a {triple.object}. "
        elif triple.predicate == "developer":
            sentence += f"{triple.subject} was developed by {triple.object}. "
        elif triple.predicate == "tenant":
            sentence += f"{triple.subject}'s tenant is {triple.object}. "
        elif triple.predicate == "isPartOf":
            sentence += f"{triple.subject} is part of {triple.object}. "
        elif triple.predicate == "country":
            sentence += f"{triple.subject} is located in {triple.object}. "
        elif triple.predicate == "currentTenants":
            sentence += f"Current tenants of {triple.subject} include {triple.object}. "
        elif triple.predicate == "address":
            sentence += f"The address of {triple.subject} is {triple.object}. "
        elif triple.predicate == "inaugurationDate":
            sentence += f"{triple.subject} was inaugurated on {triple.object}. "
        else:
            if triple.predicate == "leader":
                sentence += f"{triple.subject} is led by {triple.object}. "
            elif triple.predicate == "origin":
                sentence += f"{triple.subject} is from {triple.object}. "
            else:
                sentence += f"and {triple.subject} {triple.predicate} {triple.object}. "
    return sentence

# EVOLVE-BLOCK-END