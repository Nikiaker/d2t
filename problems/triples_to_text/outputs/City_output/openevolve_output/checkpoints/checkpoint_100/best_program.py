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
    for triple in triples:
        if not sentence:
            subject = triple.subject
            sentence += f"{triple.subject} "
        if triple.predicate == "country":
            sentence += f"is in {triple.object} "
        elif triple.predicate == "capital":
            sentence += f"and its capital is {triple.object} "
        elif triple.predicate == "areaTotal":
            sentence += f"with a total area of {triple.object} "
        elif triple.predicate == "populationTotal":
            sentence += f"and has a population of {triple.object} "
        elif triple.predicate == "areaOfWater":
            sentence += f"with an area of water of {triple.object} "
        elif triple.predicate == "areaOfLand":
            sentence += f"and an area of land of {triple.object} "
        elif triple.predicate == "elevationAboveTheSeaLevel":
            sentence += f"at an elevation of {triple.object} "
        elif triple.predicate == "isPartOf":
            sentence += f"is part of {triple.object} "
        elif triple.predicate == "utcOffset":
            sentence += f"has a UTC offset of {triple.object} "
        elif triple.predicate == "populationDensity":
            sentence += f"has a population density of {triple.object} "
        elif triple.predicate == "areaCode":
            sentence += f"has area codes {triple.object} "
        elif triple.predicate == "leaderTitle":
            sentence += f"has a {triple.object} "
        elif triple.predicate == "leader":
            sentence += f"is led by {triple.object} "
        elif triple.predicate == "postalCode":
            sentence += f"has postal codes {triple.object} "
        elif triple.predicate == "largestCity":
            sentence += f"largest city is {triple.object} "
        elif triple.predicate == "language":
            sentence += f"speaks {triple.object} "
        elif triple.predicate == "location":
            sentence += f"is located in {triple.object} "
        elif triple.predicate == "chairperson":
            sentence += f"chairperson is {triple.object} "
        elif triple.predicate == "headquarter":
            sentence += f"headquarter is {triple.object} "
        elif triple.predicate == "countySeat":
            sentence += f"county seat is {triple.object} "
        elif triple.predicate == "demonym":
            sentence += f"people are called {triple.object} "
        elif triple.predicate == "ethnicGroup":
            sentence += f"has an ethnic group of {triple.object} "
        elif triple.predicate == "state":
            sentence += f"is in the state of {triple.object} "
        elif triple.predicate == "populationMetro":
            sentence += f"has a metropolitan population of {triple.object} "
        elif triple.predicate == "type":
            sentence += f"is a {triple.object} "
        elif triple.predicate == "governmentType":
            sentence += f"has a {triple.object} government "
        elif triple.predicate == "timeZone":
            sentence += f"is in the {triple.object} time zone "
        else:
            sentence += f"and {triple.predicate} is {triple.object} "

    return sentence.strip()

# EVOLVE-BLOCK-END