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

    pred_map = {
        "architecturalStyle": "is designed in the {obj} style",
        "buildingStartDate": "started construction in {obj}",
        "completionDate": "was completed in {obj}",
        "floorCount": "has {obj} floors",
        "location": "is located in {obj}",
        "cost": "cost {obj}",
        "floorArea": "has a floor area of {obj}",
        "architect": "was designed by {obj}",
        "owner": "is owned by {obj}",
        "formerName": "was formerly known as {obj}",
        "height": "has a height of {obj}",
        "buildingType": "is a {obj}",
        "developer": "was developed by {obj}",
        "tenant": "is tenanted by {obj}",
        "isPartOf": "is part of {obj}",
        "country": "is in {obj}",
        "currentTenants": "is currently tenanted by {obj}",
        "address": "is located at {obj}",
        "inaugurationDate": "was inaugurated on {obj}",
        "birthPlace": "was born in {obj}",
        "deathPlace": "died in {obj}",
        "bedCount": "has {obj} beds",
        "region": "is in the {obj} region",
        "state": "is in the state of {obj}",
        "website": "can be found at {obj}",
        "yearOfConstruction": "was constructed in {obj}",
        "NationalRegisterOfHistoricPlacesReferenceNumber": "has the NRHP reference number {obj}",
        "addedToTheNationalRegisterOfHistoricPlaces": "was added to the National Register of Historic Places on {obj}",
        "significantBuilding": "designed the significant building {obj}",
        "governingBody": "is governed by {obj}",
        "leader": "is led by {obj}",
        "chancellor": "has {obj} as chancellor",
        "governmentType": "is governed by {obj}",
        "capital": "has {obj} as its capital",
        "language": "has {obj} as its language",
        "leaderTitle": "is led by the {obj}",
        "currency": "uses the {obj} as currency",
        "ethnicGroup": "is home to the {obj}",
        "origin": "originates from {obj}",
        "significantProject": "is known for the project {obj}",
        "foundationPlace": "was founded in {obj}",
        "demonym": "is known as {obj}",
        "numberOfRooms": "has {obj} rooms",
        "keyPerson": "has {obj} as a key person",
        "architecture": "features {obj} architecture",
        "postalCode": "has the postal code {obj}"
    }

    subjects = {}
    for t in triples:
        subjects.setdefault(t.subject, []).append(t)

    entity_sentences = []
    # Keep track of which entities have been processed to handle chaining
    processed_subjects = set()

    # Order subjects to try and create chains (subject -> object -> subject)
    sorted_subjects = sorted(subjects.keys())

    for subject in sorted_subjects:
        if subject in processed_subjects:
            continue

        t_list = subjects[subject]
        clauses = []
        for t in t_list:
            obj = t.object.strip('"').strip("'")
            phrase = pred_map.get(t.predicate, f"{t.predicate} {obj}").format(obj=obj)
            clauses.append(phrase)

        if len(clauses) > 1:
            sentence = f"{subject} {', '.join(clauses[:-1])}, and {clauses[-1]}"
        elif clauses:
            sentence = f"{subject} {clauses[0]}"
        else:
            sentence = subject

        entity_sentences.append(sentence)
        processed_subjects.add(subject)

    if not entity_sentences:
        return ""

    # Attempt to chain entities using relative clauses for complex sentences
    # If entity B is the object of a triple of entity A, use "which is" or "who is"
    final_text = ""
    if not entity_sentences:
        return ""

    # Simplified chaining: if the next entity starts with something that was an object in the previous
    # For this specific task, we'll use a more robust relative clause connector
    result = entity_sentences[0]
    for i in range(1, len(entity_sentences)):
        current_entity = entity_sentences[i]
        # Find the subject of the current entity sentence
        subj = sorted_subjects[i] if i < len(sorted_subjects) else ""

        # Check if this subject was an object in any previous triple
        is_linked = False
        for prev_subj in sorted_subjects[:i]:
            for t in subjects.get(prev_subj, []):
                if t.object.strip('"').strip("'") == subj:
                    is_linked = True
                    break

        if is_linked:
            # Use relative clause: "which is located in X, which is in Y"
            # We strip the subject from the current entity sentence
            content = current_entity.replace(subj, "").strip()
            if content.startswith(" is"):
                connector = ", which"
            elif content.startswith(" was"):
                connector = ", which"
            else:
                connector = ", and"

            # Remove leading space and potentially "is" if we use "which is"
            # But the pred_map already includes "is", so we just need the connector
            result += f"{connector}{content}"
        else:
            connector = ", and " if i == 1 else ", while "
            result += f"{connector}{current_entity}"

    return result.strip() + "."

# EVOLVE-BLOCK-END