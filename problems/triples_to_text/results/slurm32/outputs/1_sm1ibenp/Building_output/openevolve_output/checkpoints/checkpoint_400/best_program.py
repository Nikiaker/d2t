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
        "height": "rises to",
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

    # Group triples by their subject to avoid repeating the subject in every clause.
    from collections import defaultdict
    subject_groups = defaultdict(list)
    for t in triples:
        subject_groups[t.subject].append(t)

    sentences = []
    for subject, group in subject_groups.items():
        parts = []
        handled = set()

        # Helper to clean quoted objects and remove surrounding parentheses
        def clean_obj(o: str) -> str:
            # Remove surrounding quotes
            cleaned = o.strip('"').strip("'")
            # Remove surrounding parentheses if present
            cleaned = cleaned.strip()
            if cleaned.startswith("(") and cleaned.endswith(")"):
                cleaned = cleaned[1:-1].strip()
            return cleaned

        # Special predicates that require inverted phrasing or alternative wording
        for tr in group:
            if tr.predicate == "capital":
                parts.append(f"The capital of {subject} is {clean_obj(tr.object)}")
                handled.add(tr.predicate)
            elif tr.predicate == "language":
                # Preferred phrasing: "The English language is spoken in Illinois."
                parts.append(f"The {clean_obj(tr.object)} is spoken in {subject}")
                handled.add(tr.predicate)
            elif tr.predicate == "buildingStartDate":
                parts.append(f"Construction of {subject} began in {clean_obj(tr.object)}")
                handled.add(tr.predicate)
            elif tr.predicate == "inaugurationDate":
                parts.append(f"The inauguration of {subject} was on {clean_obj(tr.object)}")
                handled.add(tr.predicate)
            elif tr.predicate == "leader":
                # Preferred phrasing matching examples
                parts.append(f"The leader of {subject} is {clean_obj(tr.object)}")
                handled.add(tr.predicate)
            elif tr.predicate == "currency":
                # Special phrasing for currency
                parts.append(f"The currency of {subject} is {clean_obj(tr.object)}")
                handled.add(tr.predicate)
            elif tr.predicate == "leaderTitle":
                # Special phrasing matching example expectations
                parts.append(f"{subject} is led via the {clean_obj(tr.object)}")
                handled.add(tr.predicate)
            elif tr.predicate == "significantBuilding":
                # Preferred phrasing for architects/designers
                parts.append(f"One of the significant buildings designed by {subject} is {clean_obj(tr.object)}")
                handled.add(tr.predicate)
            elif tr.predicate == "ethnicGroup":
                # Inverted phrasing: object is the main ethnic group in subject
                parts.append(f"The main ethnic group in {subject} is {clean_obj(tr.object)}")
                handled.add(tr.predicate)
            elif tr.predicate == "origin":
                # Inverted phrasing: object is the hometown of subject
                parts.append(f"{clean_obj(tr.object)} is the hometown of {subject}")
                handled.add(tr.predicate)
            elif tr.predicate == "architecturalStyle":
                # Preferred phrasing for architectural style
                parts.append(f"The {subject} has the architectural style of {clean_obj(tr.object)}")
                handled.add(tr.predicate)
            elif tr.predicate == "height":
                # Clean value and express height naturally
                val = clean_obj(tr.object).replace("(", "").replace(")", "").strip()
                # Ensure unit is present
                if "metre" not in val.lower():
                    val = f"{val} metres"
                parts.append(f"{subject} is {val} high")
                handled.add(tr.predicate)
            elif tr.predicate == "architect":
                # Preferred phrasing matching examples
                parts.append(f"The architect of {subject} is {clean_obj(tr.object)}")
                handled.add(tr.predicate)

        # Preferred ordering of common attributes for readability.
        order = ["location", "height", "architect", "buildingType", "completionDate"]
        for pred in order:
            if pred in handled:
                continue
            for tr in group:
                if tr.predicate == pred:
                    verb = verb_map.get(pred, "has")
                    clause = f"{verb} {clean_obj(tr.object)}"
                    parts.append(clause)
                    handled.add(pred)
                    break

        # Add remaining predicates that were not handled above.
        for tr in group:
            if tr.predicate in handled:
                continue
            verb = verb_map.get(tr.predicate, "has")
            obj = clean_obj(tr.object)
            if tr.predicate in {"floorCount", "bedCount", "numberOfRooms"}:
                clause = f"{verb} {obj} floors"
            else:
                clause = f"{verb} {obj}"
            parts.append(clause)

        # Build the sentence for this subject.
        if parts:
            first_part = parts[0]
            # Avoid duplicating the subject if it already appears in the first clause
            subject_mentioned = subject.lower() in first_part.lower()
            if subject_mentioned:
                sentence = ", ".join(parts) + "."
            else:
                sentence = f"{subject} " + ", ".join(parts) + "."
        else:
            sentence = subject + "."

        sentences.append(sentence)

    # Combine sentences for multiple subjects.
    final_text = " ".join(sentences)
    # Capitalize the first character of the whole output.
    if final_text:
        final_text = final_text[0].upper() + final_text[1:]
    return final_text

# EVOLVE-BLOCK-END