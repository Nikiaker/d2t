from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    sentences = []
    for triple in triples:
        predicate = triple.predicate
        subject = triple.subject
        object_value = triple.object

        if predicate == "country":
            sentences.append(f"{subject} is located in {object_value}.")
        elif predicate == "foundingDate":
            sentences.append(f"{subject} was founded on {object_value}.")
        elif predicate == "industry":
            sentences.append(f"{subject} operates in the {object_value} industry.")
        else:
            if predicate == "capital":
                sentences.append(f"{subject}'s capital is {object_value}.")
            elif predicate == "motto":
                sentences.append(f"{subject}'s motto is \"{object_value}\".")
            elif predicate == "officialLanguage":
                sentences.append(f"The official language of {subject} is {object_value}.")
            elif predicate == "leader":
                sentences.append(f"The leader of {subject} is {object_value}.")
            elif predicate == "leaderTitle":
                sentences.append(f"The leader's title is {object_value}.")
            elif predicate == "populationDensity":
                sentences.append(f"The population density of {subject} is {object_value}.")
            elif predicate == "areaTotal":
                sentences.append(f"The area of {subject} is {object_value}.")
            else:
                sentences.append(f"The {predicate} of {subject} is {object_value}.")

    return " ".join(sentences)

# EVOLVE-BLOCK-END