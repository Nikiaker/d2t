from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    sentences = []
    for i, triple in enumerate(triples):
        if triple.predicate == "country":
            sentences.append(f"{triple.subject} is in {triple.object}.")
        elif triple.predicate == "foundingDate":
            sentences.append(f"{triple.subject} was founded on {triple.object}.")
        elif triple.predicate == "industry":
            sentences.append(f"{triple.subject} operates in the {triple.object}.")
        elif triple.predicate == "city":
            sentences.append(f"{triple.subject} is located in {triple.object}.")
        elif triple.predicate == "netIncome":
            sentences.append(f"The net income of {triple.subject} is {triple.object}.")
        elif triple.predicate == "operatingIncome":
            sentences.append(f"The operating income of {triple.subject} is {triple.object}.")
        elif triple.predicate == "regionServed":
            sentences.append(f"{triple.subject} serves the {triple.object}.")
        elif triple.predicate == "areaTotal":
            sentences.append(f"{triple.subject} has an area of {triple.object}.")
        elif triple.predicate == "leader":
            sentences.append(f"The leader of {triple.subject} is {triple.object}.")
        elif triple.predicate == "leaderTitle":
            sentences.append(f"{triple.subject}'s leader has the title: {triple.object}.")
        elif triple.predicate == "populationDensity":
            sentences.append(f"The population density of {triple.subject} is {triple.object}.")
        elif triple.predicate == "foundationPlace":
            sentences.append(f"{triple.subject} was founded in {triple.object}.")
        elif triple.predicate == "numberOfEmployees":
            sentences.append(f"{triple.subject} has {triple.object} employees.")
        elif triple.predicate == "numberOfLocations":
            sentences.append(f"{triple.subject} has {triple.object} locations.")
        elif triple.predicate == "service":
            sentences.append(f"{triple.subject} provides {triple.object}.")
        elif triple.predicate == "type":
            sentences.append(f"{triple.subject} is a {triple.object}.")
        elif triple.predicate == "alternativeName":
            sentences.append(f"{triple.subject} is also known as {triple.object}.")
        elif triple.predicate == "birthDate":
            sentences.append(f"{triple.subject} was born on {triple.object}.")
        elif triple.predicate == "keyPerson":
            sentences.append(f"A key person at {triple.subject} is {triple.object}.")
        elif triple.predicate == "cost":
            sentences.append(f"The cost of {triple.subject} is {triple.object}.")
        elif triple.predicate == "location":
            sentences.append(f"{triple.subject} is located in {triple.object}.")
        elif triple.predicate == "product":
            sentences.append(f"{triple.subject} produces {triple.object}.")
        elif triple.predicate == "subsidiary":
            sentences.append(f"{triple.subject} has a subsidiary called {triple.object}.")
        elif triple.predicate == "timeZone":
            sentences.append(f"{triple.subject} is in the {triple.object}.")
        elif triple.predicate == "isPartOf":
            sentences.append(f"{triple.subject} is part of {triple.object}.")
        elif triple.predicate == "parentCompany":
            parent_company = triple.object
            type_triple = next((t for t in triples if t.subject == parent_company and t.predicate == "type"), None)
            if type_triple:
                sentences.append(f"{triple.subject} is a subsidiary of {parent_company}, which is a {type_triple.object}.")
            else:
                sentences.append(f"{triple.subject} is a subsidiary of {triple.object}.")
        elif triple.predicate == "capital":
            sentences.append(f"The capital of {triple.subject} is {triple.object}.")
        elif triple.predicate == "motto":
            sentences.append(f"The motto of {triple.subject} is {triple.object}.")
        elif triple.predicate == "officialLanguage":
            sentences.append(f"The official language of {triple.subject} is {triple.object}.")
        elif triple.predicate == "leaderParty":
            sentences.append(f"The leader party of {triple.subject} is {triple.object}.")
        elif triple.predicate == "areaUrban":
            sentences.append(f"The urban area of {triple.subject} is {triple.object}.")
        elif triple.predicate == "part":
            sentences.append(f"{triple.subject} is part of {triple.object}.")
        elif triple.predicate == "revenue":
            sentences.append(f"The revenue of {triple.subject} is {triple.object}.")
        elif triple.predicate == "ethnicGroup":
            sentences.append(f"{triple.subject} has an ethnic group of {triple.object}.")
        elif triple.predicate == "governmentType":
            sentences.append(f"The government type of {triple.subject} is {triple.object}.")
        elif triple.predicate == "percentageOfAreaWater":
            sentences.append(f"{triple.subject} has {triple.object} percentage of area water.")
        elif triple.predicate == "longName":
            sentences.append(f"The long name of {triple.subject} is {triple.object}.")
        elif triple.predicate == "populationTotal":
            sentences.append(f"The population total of {triple.subject} is {triple.object}.")
        elif triple.predicate == "language":
            sentences.append(f"The language of {triple.subject} is {triple.object}.")
        elif triple.predicate == "elevationAboveTheSeaLevel":
            sentences.append(f"The elevation above the sea level of {triple.subject} is {triple.object}.")
        else:
            sentences.append(f"{triple.subject} {triple.predicate} {triple.object}.")

    return " ".join(sentences)

# EVOLVE-BLOCK-END