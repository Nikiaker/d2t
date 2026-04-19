from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    """
    Convert a list of building‑related triples into a fluent, natural‑language sentence.
    """
    # Mapping from predicate to a readable phrase (more concise for common predicates)
    verb_map = {
        "architecturalStyle": "has an architectural style of",
        "buildingStartDate": "was started in",
        "completionDate": "was completed in",
        "floorCount": "has",
        "location": "is located in",
        "cost": "costs",
        "floorArea": "covers a floor area of",
        "architect": "was designed by",
        "owner": "is owned by",
        "formerName": "was formerly known as",
        "height": "has a height of",
        "buildingType": "is a",
        "developer": "was developed by",
        "tenant": "has a tenant",
        "isPartOf": "is part of",
        "country": "is located in the",
        "currentTenants": "currently houses",
        "address": "has the address",
        "inaugurationDate": "was inaugurated on",
        "birthPlace": "was born in",
        "deathPlace": "died in",
        "bedCount": "has",
        "region": "is in the region of",
        "state": "is in the state of",
        "website": "has website",
        "yearOfConstruction": "was constructed in",
        "NationalRegisterOfHistoricPlacesReferenceNumber": "has NRHP reference number",
        "addedToTheNationalRegisterOfHistoricPlaces": "was added to the NRHP on",
        "significantBuilding": "is known for the building",
        "governingBody": "is governed by",
        "leader": "leader is",
        "chancellor": "has chancellor",
        "governmentType": "has government type",
        "capital": "has capital",
        "language": "speaks",
        "leaderTitle": "has leader title",
        "currency": "uses currency",
        "ethnicGroup": "has ethnic group",
        "origin": "originates from",
        "significantProject": "is known for the project",
        "foundationPlace": "was founded in",
        "demonym": "has demonym",
        "numberOfRooms": "has",
        "keyPerson": "has key person",
        "architecture": "features architecture",
        "postalCode": "postal code is",
    }

    # Build a map of persons to the buildings they designed (architect predicate)
    person_buildings = {}
    for t in triples:
        if t.predicate == "architect":
            person = t.object
            building = t.subject
            person_buildings.setdefault(person, []).append(building)

    # Group triples by their subject to avoid repeating the subject in every clause.
    from collections import defaultdict
    subject_groups = defaultdict(list)
    for t in triples:
        subject_groups[t.subject].append(t)

    sentences = []
    persons_handled = set()
    for subject, group in subject_groups.items():
        # Aggregate objects per predicate
        pred_objs = {}
        for tr in group:
            pred_objs.setdefault(tr.predicate, []).append(tr.object)

        parts = []
        handled = set()

        # Helper to clean quoted objects and remove extraneous parentheses/units
        import re
        def clean_obj(o: str) -> str:
            o = o.strip('"').strip("'")
            # Remove surrounding parentheses but keep inner content
            o = re.sub(r'^\((.*)\)$', r'\1', o)
            # Remove any parentheses within the string, keeping the inner text
            o = re.sub(r'\(([^)]+)\)', r'\1', o)
            # Collapse multiple spaces
            o = re.sub(r'\s+', ' ', o).strip()
            return o

        # Special handling for predicates that need inverted or collective phrasing
        if "capital" in pred_objs:
            caps = ", ".join(clean_obj(o) for o in pred_objs["capital"])
            parts.append(f"The capital of {subject} is {caps}")
            handled.add("capital")
        if "currency" in pred_objs:
            cur = ", ".join(clean_obj(o) for o in pred_objs["currency"])
            parts.append(f"The currency of {subject} is {cur}")
            handled.add("currency")
        if "language" in pred_objs:
            langs = ", ".join(clean_obj(o) for o in pred_objs["language"])
            # Use a more natural phrasing for languages
            if len(pred_objs["language"]) == 1:
                parts.append(f"{langs} is spoken in {subject}")
            else:
                parts.append(f"The languages spoken in {subject} include {langs}")
            handled.add("language")
        if "buildingStartDate" in pred_objs:
            parts.append(f"Construction of {subject} began in {clean_obj(pred_objs['buildingStartDate'][0])}")
            handled.add("buildingStartDate")
        if "inaugurationDate" in pred_objs:
            parts.append(f"The inauguration of {subject} was on {clean_obj(pred_objs['inaugurationDate'][0])}")
            handled.add("inaugurationDate")
        # Combined handling for leader and leaderTitle to produce a natural phrasing
        if "leader" in pred_objs:
            leaders = [clean_obj(o) for o in pred_objs["leader"]]
            leader_str = " and ".join(leaders)
            title_str = ""
            if "leaderTitle" in pred_objs:
                titles = [clean_obj(o) for o in pred_objs["leaderTitle"]]
                # Use the first title if multiple, and mark it as handled
                title_str = f", {' and '.join(titles)}"
                handled.add("leaderTitle")
            parts.append(f"The leader of {subject} is {leader_str}{title_str}")
            handled.add("leader")
        if "significantBuilding" in pred_objs:
            buildings = ", ".join(clean_obj(o) for o in pred_objs["significantBuilding"])
            parts.append(f"A significant building associated with {subject} is {buildings}")
            handled.add("significantBuilding")
        # More natural phrasing for ethnic groups
        if "ethnicGroup" in pred_objs:
            groups = [clean_obj(o) for o in pred_objs["ethnicGroup"]]
            if len(groups) == 1:
                parts.append(f"{groups[0]} are an ethnic group in {subject}")
            else:
                parts.append(f"{', '.join(groups)} are ethnic groups in {subject}")
            handled.add("ethnicGroup")
        if "origin" in pred_objs:
            origins = ", ".join(clean_obj(o) for o in pred_objs["origin"])
            parts.append(f"{origins} is the origin of {subject}")
            handled.add("origin")
        if "demonym" in pred_objs:
            demonyms = ", ".join(clean_obj(o) for o in pred_objs["demonym"])
            parts.append(f"People from {subject} are called {demonyms}")
            handled.add("demonym")
        if "buildingType" in pred_objs:
            btype = clean_obj(pred_objs["buildingType"][0])
            parts.append(f"The {subject} is a {btype} type building")
            handled.add("buildingType")

        # If this subject is a person who designs buildings and has a birthPlace, create a combined sentence
        if subject in person_buildings and "birthPlace" in pred_objs and subject not in persons_handled:
            birth = clean_obj(pred_objs["birthPlace"][0])
            buildings = person_buildings[subject]
            # Clean building names
            clean_buildings = [clean_obj(b) for b in buildings]
            if len(clean_buildings) == 1:
                building_str = clean_buildings[0]
            else:
                building_str = ", ".join(clean_buildings[:-1]) + " and " + clean_buildings[-1]
            sentence = f"{subject}, born in {birth}, designed {building_str}."
            sentences.append(sentence)
            persons_handled.add(subject)
            # Skip further processing for this person
            continue

        # Preferred ordering for common attributes
        order = ["location", "height", "architect", "completionDate"]
        for pred in order:
            if pred in handled or pred not in pred_objs:
                continue
            verb = verb_map.get(pred, "has")
            # Skip architect clause if the architect person has already been handled in a combined sentence
            if pred == "architect" and clean_obj(pred_objs[pred][0]) in persons_handled:
                continue
            clause = f"{verb} {clean_obj(pred_objs[pred][0])}"
            parts.append(clause)
            handled.add(pred)

        # Remaining predicates
        for pred, objs in pred_objs.items():
            if pred in handled:
                continue
            verb = verb_map.get(pred, "has")
            if pred in {"floorCount", "bedCount", "numberOfRooms"}:
                clause = f"{verb} {clean_obj(objs[0])} floors"
            else:
                # join multiple objects with commas
                obj_str = ", ".join(clean_obj(o) for o in objs)
                clause = f"{verb} {obj_str}"
            parts.append(clause)

        # Assemble sentence
        if parts:
            first = parts[0]
            if first.lower().startswith("the "):
                sentence = ", ".join(parts) + "."
            else:
                sentence = f"{subject} " + ", ".join(parts) + "."
        else:
            sentence = subject + "."

        sentences.append(sentence)

    final_text = " ".join(sentences)
    if final_text:
        final_text = final_text[0].upper() + final_text[1:]
    return final_text

# EVOLVE-BLOCK-END