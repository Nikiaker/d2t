from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    if not triples:
        return ""

    sentences = []
    for triple in triples:
        predicate = triple.predicate
        subject = triple.subject
        object_val = triple.object

        if predicate == "league":
            sentences.append(f"{subject} plays in the {object_val} league.")
        elif predicate == "manager":
            sentences.append(f"{subject} is managed by {object_val}.")
        elif predicate == "position":
            sentences.append(f"{subject} is in {object_val} position.")
        elif predicate == "ground":
            sentences.append(f"{subject} plays at {object_val}.")
        elif predicate == "birthDate":
            sentences.append(f"{subject} was born on {object_val}.")
        elif predicate == "birthPlace":
            sentences.append(f"{subject} was born in {object_val}.")
        elif predicate == "birthYear":
            sentences.append(f"{subject} was born in {object_val}.")
        elif predicate == "club":
            sentences.append(f"{subject} plays for {object_val}.")
        elif predicate == "draftTeam":
            sentences.append(f"{subject} was drafted by {object_val}.")
        elif predicate == "height":
            sentences.append(f"{subject} is {object_val} tall.")
        elif predicate == "youthclub":
            sentences.append(f"{subject} started his career at {object_val}.")
        elif predicate == "currentclub":
            sentences.append(f"{subject} currently plays for {object_val}.")
        elif predicate == "weight":
            sentences.append(f"{subject} weighs {object_val}.")
        elif predicate == "deathPlace":
            sentences.append(f"{subject} died in {object_val}.")
        elif predicate == "activeYearsStartYear":
            sentences.append(f"{subject} started his career in {object_val}.")
        elif predicate == "currentteam":
            sentences.append(f"{subject} currently plays for {object_val}.")
        elif predicate == "debutTeam":
            sentences.append(f"{subject} debuted with {object_val}.")
        elif predicate == "draftPick":
            sentences.append(f"{subject} was the {object_val} draft pick.")
        elif predicate == "draftRound":
            sentences.append(f"{subject} was drafted in round {object_val}.")
        elif predicate == "formerTeam":
            sentences.append(f"{subject} previously played for {object_val}.")
        elif predicate == "playerNumber":
            sentences.append(f"{subject} wears number {object_val}.")
        elif predicate == "college":
            sentences.append(f"{subject} played college basketball for {object_val}.")
        elif predicate == "draftYear":
            sentences.append(f"{subject} was drafted in {object_val}.")
        elif predicate == "coach":
            sentences.append(f"{subject} is coached by {object_val}.")
        elif predicate == "owner":
            sentences.append(f"{subject} is owned by {object_val}.")
        elif predicate == "city":
            sentences.append(f"{subject} is based in {object_val}.")
        elif predicate == "leader":
            sentences.append(f"{subject} is a leader of {object_val}.")
        elif predicate == "anthem":
            sentences.append(f"{subject} has the anthem {object_val}.")
        elif predicate == "ethnicGroup":
            sentences.append(f"{subject} has the ethnic group {object_val}.")
        elif predicate == "language":
            sentences.append(f"{subject} speaks {object_val}.")
        elif predicate == "generalManager":
            sentences.append(f"{subject} is managed by {object_val}.")
        elif predicate == "chairman":
            sentences.append(f"{subject} is chaired by {object_val}.")
        elif predicate == "season":
            sentences.append(f"{subject} participated in the {object_val}.")
        elif predicate == "currency":
            sentences.append(f"{subject} uses the currency {object_val}.")
        elif predicate == "demonym":
            sentences.append(f"{subject} are known as {object_val}.")
        elif predicate == "officialLanguage":
            sentences.append(f"{subject} has the official language {object_val}.")
        elif predicate == "stadium":
            sentences.append(f"{subject} plays at {object_val}.")
        elif predicate == "universityTeam":
            sentences.append(f"{subject} plays for {object_val}.")
        elif predicate == "mostChampions":
            sentences.append(f"{subject} has the most champions {object_val}.")
        elif predicate == "leaderTitle":
            sentences.append(f"{subject} holds the title of {object_val}.")
        elif predicate == "isPartOf":
            sentences.append(f"{subject} is a part of {object_val}.")
        elif predicate == "country":
            sentences.append(f"{subject} is located in {object_val}.")
        elif predicate == "utcOffset":
            sentences.append(f"{subject} has a UTC offset of {object_val}.")
        elif predicate == "timeZone":
            sentences.append(f"{subject} is in the {object_val} time zone.")
        elif predicate == "areaTotal":
            sentences.append(f"{subject} has an area of {object_val}.")
        elif predicate == "foundingDate":
            sentences.append(f"{subject} was founded on {object_val}.")
        else:
            sentences.append(f"The {predicate} of {subject} is {object_val}.")

    return " ".join(sentences)

# EVOLVE-BLOCK-END