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
        "postalCode": "has the postcode area",
    }

    # Build a map of persons to the buildings they designed (architect predicate)
    person_buildings = {}
    for t in triples:
        if t.predicate == "architect":
            person = t.object
            building = t.subject
            person_buildings.setdefault(person, []).append(building)

    # Build a map of entities (usually countries) to their leaders for later use
    leader_map = {}
    for t in triples:
        if t.predicate == "leader":
            leader_map.setdefault(t.subject, []).append(t.object)

    # Group triples by their subject to avoid repeating the subject in every clause.
    from collections import defaultdict
    subject_groups = defaultdict(list)
    for t in triples:
        subject_groups[t.subject].append(t)

    # Build short descriptive phrases for entities that might appear as objects in other triples.
    # Currently we only handle leader information, but this can be extended.
    entity_extras = {}
    for ent, ents_triples in subject_groups.items():
        leaders = [t.object.strip('"\'') for t in ents_triples if t.predicate == "leader"]
        if leaders:
            # Use a natural phrasing; if multiple leaders, join with "and"
            leader_phrase = " and ".join(leaders)
            entity_extras[ent] = f"where {leader_phrase} is the leader"

    sentences = []
    persons_handled = set()
    for subject, group in subject_groups.items():
        # Aggregate objects per predicate
        pred_objs = {}
        for tr in group:
            pred_objs.setdefault(tr.predicate, []).append(tr.object)

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

        parts = []
        handled = set()

        # Simple single‑predicate handling for more natural phrasing
        if len(pred_objs) == 1:
            pred, objs = next(iter(pred_objs.items()))
            obj_clean = clean_obj(objs[0])
            if pred == "architect":
                sentences.append(f"The architect of {subject} was {obj_clean}.")
                continue
            if pred == "ethnicGroup":
                sentences.append(f"The main ethnic group in {subject} is {obj_clean}.")
                continue

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
        # Combine leader and leaderTitle into a single natural phrase when both are present
        if "leader" in pred_objs and "leaderTitle" in pred_objs:
            leader = clean_obj(pred_objs["leader"][0])
            title = clean_obj(pred_objs["leaderTitle"][0])
            parts.append(f"{leader} is the {title} of {subject}")
            handled.update(["leader", "leaderTitle"])
        else:
            if "leader" in pred_objs:
                leaders = " and ".join(clean_obj(o) for o in pred_objs["leader"])
                parts.append(f"The leader of {subject} is {leaders}")
                handled.add("leader")
            if "leaderTitle" in pred_objs:
                titles = " and ".join(clean_obj(o) for o in pred_objs["leaderTitle"])
                # Use a more natural phrasing when only a leader title is given
                parts.append(f"{titles} is a leader in {subject}")
                handled.add("leaderTitle")
        if "significantBuilding" in pred_objs:
            buildings = ", ".join(clean_obj(o) for o in pred_objs["significantBuilding"])
            parts.append(f"A significant building associated with {subject} is {buildings}")
            handled.add("significantBuilding")
        if "significantProject" in pred_objs:
            objs = [clean_obj(o) for o in pred_objs["significantProject"]]
            if len(objs) == 1:
                parts.append(f"{objs[0]} was a significant project of {subject}")
            else:
                proj_str = ", ".join(objs[:-1]) + " and " + objs[-1]
                parts.append(f"{proj_str} were significant projects of {subject}")
            handled.add("significantProject")
        if "significantBuilding" in pred_objs:
            objs = [clean_obj(o) for o in pred_objs["significantBuilding"]]
            if len(objs) == 1:
                parts.append(f"{objs[0]} is a significant building of {subject}")
            else:
                bld_str = ", ".join(objs[:-1]) + " and " + objs[-1]
                parts.append(f"{bld_str} are significant buildings of {subject}")
            handled.add("significantBuilding")
        if "ethnicGroup" in pred_objs:
            groups = [clean_obj(o) for o in pred_objs["ethnicGroup"]]
            if len(groups) == 1:
                parts.append(f"One {subject} ethnic group is {groups[0]}")
            else:
                parts.append(f"The ethnic groups in {subject} include {', '.join(groups)}")
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

        # Skip building subjects that have already been covered in a combined person sentence
        if any(subject in person_buildings[p] for p in persons_handled):
            continue

        # If this subject is a person who designs buildings and has additional info, create a combined sentence
        if subject in person_buildings and any(pred in pred_objs for pred in ("birthPlace", "significantBuilding", "significantProject")) and subject not in persons_handled:
            # Gather birth place if present
            birth_phrase = ""
            if "birthPlace" in pred_objs:
                birth = clean_obj(pred_objs["birthPlace"][0])
                birth_phrase = f", born in {birth}"
            # Gather buildings designed (from architect triples)
            designed_buildings = [clean_obj(b) for b in person_buildings.get(subject, [])]
            # Add buildings from significantBuilding predicate
            if "significantBuilding" in pred_objs:
                designed_buildings += [clean_obj(o) for o in pred_objs["significantBuilding"]]
            # Add projects from significantProject predicate (treated as designs as well)
            if "significantProject" in pred_objs:
                designed_buildings += [clean_obj(o) for o in pred_objs["significantProject"]]

            # Build a natural list string
            if not designed_buildings:
                design_str = ""
            elif len(designed_buildings) == 1:
                design_str = designed_buildings[0]
            else:
                design_str = ", ".join(designed_buildings[:-1]) + " and " + designed_buildings[-1]

            sentence = f"{subject}{birth_phrase}, designed {design_str}."
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
            if pred == "architect":
                obj_clean = clean_obj(pred_objs[pred][0])
                # Use a different phrasing for firms or non‑person architects
                if "(" in obj_clean or "firm" in obj_clean.lower() or "architects" in obj_clean.lower():
                    clause = f"The architect of {subject} is {obj_clean}"
                else:
                    clause = f"{verb} {obj_clean}"
            else:
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