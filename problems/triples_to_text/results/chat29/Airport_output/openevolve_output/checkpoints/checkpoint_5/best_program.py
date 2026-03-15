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

    from collections import defaultdict

    predicate_templates = {
        "cityServed": lambda s, o: f"{s} serves the city of {o}",
        "elevationAboveTheSeaLevel": lambda s, o: f"has an elevation of {o} metres above sea level",
        "elevationAboveTheSeaLevelInFeet": lambda s, o: f"has an elevation of {o} feet above sea level",
        "elevationAboveTheSeaLevelInMetres": lambda s, o: f"has an elevation of {o} metres above sea level",
        "location": lambda s, o: f"is located in {o}",
        "operatingOrganisation": lambda s, o: f"is operated by {o}",
        "runwayLength": lambda s, o: f"has a runway length of {o} metres",
        "runwayName": lambda s, o: f"has a runway named {o}",
        "country": lambda s, o: f"is in {o}",
        "isPartOf": lambda s, o: f"is part of {o}",
        "1stRunwayLengthFeet": lambda s, o: f"has a first runway length of {o} feet",
        "1stRunwayLengthMetre": lambda s, o: f"has a first runway length of {o} metres",
        "1stRunwaySurfaceType": lambda s, o: f"has a first runway surface of {o}",
        "1stRunwayNumber": lambda s, o: f"has a first runway number of {o}",
        "2ndRunwaySurfaceType": lambda s, o: f"has a second runway surface of {o}",
        "3rdRunwayLengthFeet": lambda s, o: f"has a third runway length of {o} feet",
        "3rdRunwaySurfaceType": lambda s, o: f"has a third runway surface of {o}",
        "4thRunwayLengthFeet": lambda s, o: f"has a fourth runway length of {o} feet",
        "4thRunwaySurfaceType": lambda s, o: f"has a fourth runway surface of {o}",
        "5thRunwayNumber": lambda s, o: f"has a fifth runway number of {o}",
        "5thRunwaySurfaceType": lambda s, o: f"has a fifth runway surface of {o}",
        "icaoLocationIdentifier": lambda s, o: f"has the ICAO identifier {o}",
        "iataLocationIdentifier": lambda s, o: f"has the IATA identifier {o}",
        "locationIdentifier": lambda s, o: f"has the location identifier {o}",
        "nativeName": lambda s, o: f"is natively known as {o}",
        "leaderParty": lambda s, o: f"is led by the {o}",
        "capital": lambda s, o: f"the capital of {s} is {o}",
        "language": lambda s, o: f"uses the {o}",
        "officialLanguage": lambda s, o: f"the official language of {s} is {o}",
        "leader": lambda s, o: f"is led by {o}",
        "owner": lambda s, o: f"is owned by {o}",
        "largestCity": lambda s, o: f"the largest city of {s} is {o}",
        "countySeat": lambda s, o: f"the county seat of {s} is {o}",
        "administrativeArrondissement": lambda s, o: f"is in the administrative arrondissement of {o}",
        "mayor": lambda s, o: f"the mayor of {s} is {o}",
        "runwaySurfaceType": lambda s, o: f"has a runway surface of {o}",
        "city": lambda s, o: f"is in the city of {o}",
        "jurisdiction": lambda s, o: f"has jurisdiction over {o}",
        "demonym": lambda s, o: f"people from {s} are called {o}",
        "aircraftHelicopter": lambda s, o: f"operates the {o} helicopter",
        "transportAircraft": lambda s, o: f"uses {o} as a transport aircraft",
        "currency": lambda s, o: f"the currency of {s} is the {o}",
        "headquarter": lambda s, o: f"is headquartered at {o}",
        "class": lambda s, o: f"belongs to the class {o}",
        "division": lambda s, o: f"belongs to the division {o}",
        "order": lambda s, o: f"belongs to the order {o}",
        "regionServed": lambda s, o: f"serves the region of {o}",
        "leaderTitle": lambda s, o: f"the leader title of {s} is {o}",
        "hubAirport": lambda s, o: f"uses {o} as its hub airport",
        "aircraftFighter": lambda s, o: f"operates the {o} fighter aircraft",
        "attackAircraft": lambda s, o: f"uses the {o} as an attack aircraft",
        "battle": lambda s, o: f"participated in the {o}",
        "chief": lambda s, o: f"the chief of {s} is {o}",
        "foundedBy": lambda s, o: f"was founded by {o}",
        "postalCode": lambda s, o: f"has the postal code {o}",
        "areaCode": lambda s, o: f"has the area code {o}",
        "foundingYear": lambda s, o: f"was founded in {o}",
        "ceremonialCounty": lambda s, o: f"is in the ceremonial county of {o}",
    }

    # Standalone predicates that form their own sentence with full subject
    standalone_predicates = {
        "capital", "officialLanguage", "largestCity", "countySeat",
        "mayor", "currency", "chief", "leaderTitle", "demonym"
    }

    # Group triples by subject
    subject_groups = defaultdict(list)
    for triple in triples:
        subject_groups[triple.subject].append(triple)

    # Determine main subject priority: prefer airport, then first triple's subject
    def subject_priority(subj):
        sl = subj.lower()
        if "airport" in sl:
            return 0
        return 1

    subjects_ordered = sorted(subject_groups.keys(), key=subject_priority)
    main_subject = subjects_ordered[0]

    # Build sentence parts grouped by subject
    sentence_parts = []

    for subj in subjects_ordered:
        group = subject_groups[subj]
        subj_phrases = []
        standalone_phrases = []

        for triple in group:
            pred = triple.predicate
            obj = triple.object
            if pred in predicate_templates:
                phrase = predicate_templates[pred](subj, obj)
            else:
                phrase = f"the {pred} of {subj} is {obj}"

            # Check if this predicate needs standalone sentence
            if pred in standalone_predicates:
                standalone_phrases.append(phrase)
            else:
                # Check if template already includes subject
                if phrase.startswith(subj):
                    standalone_phrases.append(phrase)
                else:
                    subj_phrases.append(phrase)

        if subj_phrases:
            # Combine subject-relative phrases
            if len(subj_phrases) == 1:
                combined = f"{subj} {subj_phrases[0]}"
            elif len(subj_phrases) == 2:
                combined = f"{subj} {subj_phrases[0]} and {subj_phrases[1]}"
            else:
                combined = f"{subj} {', '.join(subj_phrases[:-1])}, and {subj_phrases[-1]}"
            sentence_parts.append(combined)

        for sp in standalone_phrases:
            sentence_parts.append(sp)

    if not sentence_parts:
        return ""

    # Capitalize first letter of the whole sentence
    if len(sentence_parts) == 1:
        result = sentence_parts[0]
    elif len(sentence_parts) == 2:
        result = sentence_parts[0] + ", and " + sentence_parts[1]
    else:
        result = ", ".join(sentence_parts[:-1]) + ", and " + sentence_parts[-1]

    result = result[0].upper() + result[1:]
    if not result.endswith("."):
        result += "."
    return result

# EVOLVE-BLOCK-END