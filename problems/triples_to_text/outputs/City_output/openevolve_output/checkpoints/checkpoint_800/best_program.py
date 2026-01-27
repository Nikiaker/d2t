from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    sentence = ""
    first = True
    for i, triple in enumerate(triples):
        if first:
            sentence += f"{triple.subject} "
            first = False
        if triple.predicate == "areaOfWater":
            sentence += f"has an area of water of {triple.object}, "
        elif triple.predicate == "areaTotal":
            sentence += f"has a total area of {triple.object}, "
        elif triple.predicate == "country":
            sentence += f"is in {triple.object} and "
        elif triple.predicate == "capital":
            sentence += f"has a capital of {triple.object}, "
        elif triple.predicate == "elevationAboveTheSeaLevel":
            sentence += f"with an elevation of {triple.object} above sea level, "
        elif triple.predicate == "isPartOf":
            sentence += f"which is part of {triple.object} and "
        elif triple.predicate == "populationDensity":
            sentence += f"has a population density of {triple.object}, "
        elif triple.predicate == "areaCode":
            sentence += f"with area codes {triple.object}, "
        elif triple.predicate == "leaderTitle":
            sentence += f"led by a {triple.object}, "
        elif triple.predicate == "areaOfLand":
            sentence += f"has an area of land of {triple.object}, "
        elif triple.predicate == "leader":
            sentence += f"led by {triple.object}, "
        elif triple.predicate == "utcOffset":
            sentence += f"with a UTC offset of {triple.object}, "
        elif triple.predicate == "populationTotal":
            sentence += f"has a population of {triple.object}, "
        elif triple.predicate == "postalCode":
            sentence += f"with postal codes {triple.object}, "
        elif triple.predicate == "largestCity":
            sentence += f"its largest city is {triple.object}, "
        elif triple.predicate == "language":
            sentence += f"where the language is {triple.object}, "
        elif triple.predicate == "location":
            sentence += f"located in {triple.object}, "
        elif triple.predicate == "chairperson":
            sentence += f"with {triple.object} as its chairperson, "
        elif triple.predicate == "headquarter":
            sentence += f"and its headquarter is {triple.object}, "
        elif triple.predicate == "countySeat":
            sentence += f"with {triple.object} as its county seat, "
        elif triple.predicate == "demonym":
            sentence += f"and its people are known as {triple.object}, "
        elif triple.predicate == "ethnicGroup":
            sentence += f"with a significant {triple.object} population, "
        elif triple.predicate == "state":
            sentence += f"in the state of {triple.object}, "
        elif triple.predicate == "populationMetro":
            sentence += f"with a metropolitan population of {triple.object}, "
        elif triple.predicate == "type":
            sentence += f"which is a {triple.object}, "
        elif triple.predicate == "governmentType":
            sentence += f"with a {triple.object} government, "
        elif triple.predicate == "timeZone":
            sentence += f"in the {triple.object} time zone, "
        else:
            sentence += f"{triple.predicate} is {triple.object}, "

    return sentence.strip(", ")

# EVOLVE-BLOCK-END