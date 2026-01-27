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

        if predicate == "almaMater":
            sentences.append(f"{subject} attended {object_val}.")
        elif predicate == "birthDate":
            sentences.append(f"{subject} was born on {object_val}.")
        elif predicate == "birthPlace":
            sentences.append(f"{subject} was born in {object_val}.")
        elif predicate == "dateOfRetirement":
            sentences.append(f"{subject} retired in {object_val}.")
        elif predicate == "occupation":
            sentences.append(f"{subject} worked as a {object_val}.")
        elif predicate == "status":
            sentences.append(f"{subject}'s status is {object_val}.")
        elif predicate == "timeInSpace":
            sentences.append(f"{subject} spent {object_val} in space.")
        elif predicate == "mission":
            mission_val = object_val
            nationality = next((t.object for t in triples if t.subject == subject and t.predicate == "nationality"), None)
            operator = next((t.object for t in triples if t.subject == mission_val and t.predicate == "operator"), None)
            commander = next((t.object for t in triples if t.subject == mission_val and t.predicate == "commander"), None)
            backup_pilot = next((t.object for t in triples if t.subject == mission_val and t.predicate == "backupPilot"), None)

            sentence = ""
            if nationality:
                sentence += f"{subject}, a {nationality} national, "
            if operator:
                sentence += f"was a crew member of the {operator} operated {mission_val} mission"
            else:
                sentence += f"was a crew member of the {mission_val} mission"

            if commander:
                sentence += f" commanded by {commander}"
            if backup_pilot:
                sentence += f" with {backup_pilot} as the backup pilot"

            sentence += "."
            sentences.append(sentence)
        elif predicate == "selectedByNasa":
            sentences.append(f"{subject} was selected by NASA in {object_val}.")
        elif predicate == "deathDate":
            sentences.append(f"{subject} died on {object_val}.")
        elif predicate == "nationality":
            sentences.append(f"{subject} was a citizen of {object_val}.")
        elif predicate == "servedAsChiefOfTheAstronautOfficeIn":
            sentences.append(f"{subject} served as Chief of the Astronaut Office in {object_val}.")
        elif predicate == "title":
            sentences.append(f"{subject}'s title was {object_val}.")
        elif predicate == "ribbonAward":
            sentences.append(f"{subject} was awarded the {object_val}.")
        elif predicate == "operator":
            sentences.append(f"{object_val} is operated by {subject}.")
        elif predicate == "backupPilot":
            sentences.append(f"{subject} served as the backup pilot for {object_val}.")
        elif predicate == "commander":
            sentences.append(f"{subject} commanded the {object_val}.")
        elif predicate == "crewMembers":
            sentences.append(f"{object_val}'s crew included {subject}.")
        elif predicate == "representative":
            sentences.append(f"{subject} represented {object_val}.")
        elif predicate == "alternativeName":
            sentences.append(f"{subject} is also known as {object_val}.")
        elif predicate == "awards":
            sentences.append(f"{subject} has received {object_val} awards.")
        elif predicate == "fossil":
            sentences.append(f"{object_val} fossils have been found in {subject}.")
        elif predicate == "senators":
            sentences.append(f"{subject} is represented by senators {object_val}.")
        elif predicate == "part":
            sentences.append(f"{subject} is part of {object_val}.")
        elif predicate == "partsType":
            sentences.append(f"{subject} is a type of {object_val}.")
        elif predicate == "higher":
            sentences.append(f"{subject} is higher than {object_val}.")
        elif predicate == "isPartOf":
            sentences.append(f"{subject} is a part of {object_val}.")
        elif predicate == "bird":
            sentences.append(f"{subject}'s bird is {object_val}.")
        elif predicate == "leader":
            sentences.append(f"{subject} is led by {object_val}.")
        elif predicate == "affiliation":
            sentences.append(f"{subject} is affiliated with {object_val}.")
        elif predicate == "competeIn":
            sentences.append(f"{subject} competes in {object_val}.")
        elif predicate == "president":
            sentences.append(f"{subject}'s president is {object_val}.")
        elif predicate == "award":
            sentences.append(f"{subject} was awarded the {object_val}.")
        elif predicate == "deathPlace":
            sentences.append(f"{subject} died in {object_val}.")
        elif predicate == "gemstone":
            sentences.append(f"{subject}'s gemstone is {object_val}.")
        elif predicate == "mascot":
            sentences.append(f"{subject}'s mascot is {object_val}.")
        elif predicate == "cosparId":
            sentences.append(f"{subject}'s cosparId is {object_val}.")
        elif predicate == "utcOffset":
            sentences.append(f"{subject}'s utcOffset is {object_val}.")
        else:
            sentences.append(f"The {predicate} of {subject} is {object_val}.")

    return " ".join(sentences)

# EVOLVE-BLOCK-END