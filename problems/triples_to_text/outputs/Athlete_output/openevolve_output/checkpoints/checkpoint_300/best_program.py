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
            sentences.append(f"{subject} plays as a {object_val}.")
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
            sentences.append(f"{object_val} is a language spoken in {subject}.")
        elif predicate == "generalManager":
            sentences.append(f"{object_val} is the general manager of {subject}.")
        elif predicate == "chairman":
            sentences.append(f"{object_val} is the chairman of {subject}.")
        elif predicate == "season":
            sentences.append(f"{subject} competed in the {object_val}.")
        elif predicate == "currency":
            sentences.append(f"The currency of {subject} is {object_val}.")
        elif predicate == "demonym":
            sentences.append(f"People from {subject} are known as {object_val}.")
        elif predicate == "officialLanguage":
            sentences.append(f"{object_val} is an official language of {subject}.")
        elif predicate == "stadium":
            sentences.append(f"{subject}'s stadium is {object_val}.")
        elif predicate == "universityTeam":
            sentences.append(f"{subject} is the university team of {object_val}.")
        elif predicate == "mostChampions":
            sentences.append(f"{object_val} are the most champions of {subject}.")
        elif predicate == "leaderTitle":
            sentences.append(f"{object_val} is the leader title of {subject}.")
        elif predicate == "isPartOf":
            sentences.append(f"{subject} is part of {object_val}.")
        elif predicate == "country":
            sentences.append(f"{subject} is a city in {object_val}.")
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