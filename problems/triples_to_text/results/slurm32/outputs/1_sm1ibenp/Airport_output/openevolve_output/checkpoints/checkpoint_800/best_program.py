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
    # Group triples by subject to allow multiple entities
    from collections import defaultdict
    subject_map = defaultdict(list)
    for t in triples:
        subject_map[t.subject].append(t)

    # Simple predicate → phrase templates
    templates = {
        # Airport‑specific predicates
        "cityServed": "serves the city of {obj}",
        "elevationAboveTheSeaLevel": "is {obj} metres above sea level",
        "elevationAboveTheSeaLevelInMetres": "is {obj} metres above sea level",
        "elevationAboveTheSeaLevelInFeet": "is {obj} feet above sea level",
        # more natural phrasing without redundant unit words
        "runwayLength": "has a runway length of {obj}",
        "runwayName": "has a runway named {obj}",
        "location": "is located in {obj}",
        "operatingOrganisation": "is operated by {obj}",
        "country": "is in {obj}",
        "isPartOf": "is part of {obj}",
        "icaoLocationIdentifier": "ICAO location identifier is {obj}",
        "locationIdentifier": "location identifier is {obj}",
        "iataLocationIdentifier": "IATA location identifier is {obj}",
        "1stRunwayLengthFeet": "has a first runway length of {obj} feet",
        "1stRunwayLengthMetre": "has a first runway length of {obj} metres",
        "1stRunwaySurfaceType": "its first runway has a {obj} surface",
        "1stRunwayNumber": "its first runway number is {obj}",
        "2ndRunwaySurfaceType": "its second runway has a {obj} surface",
        "3rdRunwaySurfaceType": "its third runway has a {obj} surface",
        "4thRunwaySurfaceType": "its fourth runway has a {obj} surface",
        "5thRunwaySurfaceType": "its fifth runway has a {obj} surface",
        "runwaySurfaceType": "runway surface is {obj}",
        # Generic entity predicates
        "leader": "leader is {obj}",
        "capital": "capital is {obj}",
        "language": "language is {obj}",
        "officialLanguage": "official language is {obj}",
        "currency": "currency is {obj}",
        "owner": "owner is {obj}",
        "foundingYear": "was founded in {obj}",
        "founder": "was founded by {obj}",
        "postalCode": "postal code is {obj}",
        "areaCode": "area code is {obj}",
        "largestCity": "largest city is {obj}",
        "countySeat": "county seat is {obj}",
        "mayor": "mayor is {obj}",
        "leaderParty": "leader party is {obj}",
        "leaderTitle": "leader title is {obj}",
        "chief": "chief is {obj}",
        "hubAirport": "hub airport is {obj}",
        "regionServed": "serves region {obj}",
        "nativeName": "native name is {obj}",
        "jurisdiction": "has jurisdiction in {obj}",
        # Biological classification predicates
        "class": "is of the class {obj}",
        "division": "is of the division {obj}",
        "order": "is of the order {obj}",
        "species": "is of the species {obj}",
        "demonym": "demonym is {obj}",
    }

    # Helper to format numbers nicely (remove trailing .0 and add commas)
    def _fmt_number(val: str) -> str:
        try:
            num = float(val.replace(",", ""))
            if num.is_integer():
                num = int(num)
            return f"{num:,}"
        except Exception:
            return val

    sentences = []
    for subject, tlist in subject_map.items():
        parts = []  # will store tuples (predicate, phrase, raw_obj)
        for t in tlist:
            tmpl = templates.get(t.predicate)
            obj = t.object.strip('"')
            if tmpl:
                # Try to format numeric objects nicely
                try:
                    num = float(obj.replace(",", ""))
                    fmt_obj = _fmt_number(obj)
                except Exception:
                    fmt_obj = obj
                parts.append((t.predicate, tmpl.format(obj=fmt_obj), obj))
            else:
                pred = t.predicate.replace('_', ' ')
                parts.append((t.predicate, f"{pred} {obj}", obj))

        # Combine parts into a fluent sentence
        if parts:
            if len(parts) == 1:
                pred, phrase, raw_obj = parts[0]
                # Unified single‑predicate templates for more natural phrasing
                single_templates = {
                    "runwayLength": "The runway length of {subject} is {obj}.",
                    "runwayName": "The runway name of {subject} is {obj}.",
                    "1stRunwayLengthMetre": "The length of the first runway at {subject} is {obj} metres.",
                    "1stRunwayLengthFeet": "The length of the first runway at {subject} is {obj} feet.",
                    "1stRunwayNumber": "The first runway number of {subject} is {obj}.",
                    "5thRunwayNumber": "The fifth runway number of {subject} is {obj}.",
                    "1stRunwaySurfaceType": "The first runway at {subject} is made of {obj}.",
                    "2ndRunwaySurfaceType": "The second runway at {subject} is made of {obj}.",
                    "3rdRunwaySurfaceType": "The third runway at {subject} is made of {obj}.",
                    "4thRunwaySurfaceType": "The fourth runway at {subject} is made of {obj}.",
                    "5thRunwaySurfaceType": "The fifth runway at {subject} is made of {obj}.",
                    "runwaySurfaceType": "The runway surface at {subject} is {obj}.",
                    "locationIdentifier": "The location identifier for {subject} is {obj}.",
                    "icaoLocationIdentifier": "The ICAO identifier for {subject} is {obj}.",
                    "iataLocationIdentifier": "The IATA identifier for {subject} is {obj}.",
                    "capital": "The capital of {subject} is {obj}.",
                    "language": "The language spoken in {subject} is {obj}.",
                    "officialLanguage": "The official language of {subject} is {obj}.",
                }
                if pred in single_templates:
                    # surface types are usually lower‑cased in natural language
                    obj_formatted = raw_obj.lower() if pred.endswith("RunwaySurfaceType") else raw_obj
                    sentence = single_templates[pred].format(subject=subject, obj=obj_formatted)
                elif pred == "language":
                    # fallback for plural “languages”
                    if raw_obj.lower().endswith("languages"):
                        sentence = f"The {raw_obj} are spoken in {subject}."
                    else:
                        sentence = f"The language spoken in {subject} is {raw_obj}."
                else:
                    sentence = f"{subject} {phrase}."
            else:
                # Combine multiple predicates into one fluent sentence
                # Define a priority order for predicates to improve natural flow
                priority = {
                    "location": 0,
                    "cityServed": 1,
                    "country": 2,
                    "isPartOf": 3,
                    "elevationAboveTheSeaLevel": 4,
                    "elevationAboveTheSeaLevelInMetres": 4,
                    "elevationAboveTheSeaLevelInFeet": 4,
                    "runwayLength": 5,
                    "1stRunwayLengthMetre": 5,
                    "1stRunwayLengthFeet": 5,
                    "runwayName": 6,
                    "1stRunwayNumber": 7,
                    "2ndRunwaySurfaceType": 8,
                    "3rdRunwaySurfaceType": 8,
                    "4thRunwaySurfaceType": 8,
                    "5thRunwaySurfaceType": 8,
                    "runwaySurfaceType": 8,
                    "operatingOrganisation": 9,
                    "owner": 10,
                    "icaoLocationIdentifier": 11,
                    "iataLocationIdentifier": 12,
                    "locationIdentifier": 13,
                }
                # Sort parts according to priority (default large number if not listed)
                sorted_parts = sorted(parts, key=lambda x: priority.get(x[0], 100))
                phrase_list = [p for _, p, _ in sorted_parts]
                # Build sentence with proper commas and conjunction
                if len(phrase_list) == 2:
                    combined = " and ".join(phrase_list)
                else:
                    combined = ", ".join(phrase_list[:-1]) + ", and " + phrase_list[-1]
                sentence = f"{subject} {combined}."
            sentences.append(sentence)

    return " ".join(sentences)

# EVOLVE-BLOCK-END