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
        elif triple.predicate == "isPartOf":
            sentence += f" is part of {triple.object}."
        elif triple.predicate == "areaOfWater":
            sentence += f" has an area of water of {triple.object}."
        elif triple.predicate == "elevationAboveTheSeaLevel":
            sentence += f" has an elevation of {triple.object} meters."
        elif triple.predicate == "leaderTitle":
            sentence += f" is led by a {triple.object}."
        elif triple.predicate == "largestCity":
            sentence += f" has {triple.object} as its largest city."
        elif triple.predicate == "language":
            sentence += f" speaks {triple.object}."
        elif triple.predicate == "location":
            sentence += f" is located in {triple.object}."
        elif triple.predicate == "chairperson":
            sentence += f" is chaired by {triple.object}."
        elif triple.predicate == "headquarter":
            sentence += f" has its headquarters in {triple.object}."
        elif triple.predicate == "countySeat":
            sentence += f" has {triple.object} as its county seat."
        elif triple.predicate == "demonym":
            sentence += f" is inhabited by {triple.object}."
        elif triple.predicate == "ethnicGroup":
            sentence += f" includes the ethnic group of {triple.object}."
        elif triple.predicate == "state":
            sentence += f" is located in the state of {triple.object}."
        elif triple.predicate == "populationMetro":
            sentence += f" has a metropolitan population of {triple.object}."
        elif triple.predicate == "type":
            sentence += f" is a {triple.object}."
        elif triple.predicate == "governmentType":
            sentence += f" operates under a {triple.object} government."
        elif triple.predicate == "timeZone":
            sentence += f" is in the {triple.object} time zone."
        elif triple.predicate == "utcOffset":
            sentence += f" has a UTC offset of {triple.object}."
        elif triple.predicate == "areaCode":
            sentence += f" has area codes {triple.object}."
        elif triple.predicate == "populationDensity":
            sentence += f" has a population density of {triple.object}."
        elif triple.predicate == "areaOfLand":
            sentence += f" has an area of land of {triple.object}."
        else:
            sentence += f"and {triple.predicate} is {triple.object} "
    return sentence.strip()

# EVOLVE-BLOCK-END