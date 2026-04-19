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
        "icaoLocationIdentifier": "ICAO code is {obj}",
        "locationIdentifier": "location identifier is {obj}",
        "iataLocationIdentifier": "IATA code is {obj}",
        "1stRunwayLengthFeet": "has a first runway length of {obj} feet",
        "1stRunwayLengthMetre": "has a first runway length of {obj} metres",
        "1stRunwaySurfaceType": "its first runway has a {obj} surface",
        "1stRunwayNumber": "its first runway number is {obj}",
        "2ndRunwaySurfaceType": "its second runway has a {obj} surface",
        "3rdRunwaySurfaceType": "its third runway has a {obj} surface",
        "4thRunwaySurfaceType": "its fourth runway has a {obj} surface",
        "5thRunwaySurfaceType": "its fifth runway has a {obj} surface",
        "runwaySurfaceType": "runway surface is {obj}",
        # Added missing runway length predicates for higher order runways
        "2ndRunwayLengthFeet": "has a second runway length of {obj} feet",
        "3rdRunwayLengthFeet": "has a third runway length of {obj} feet",
        "4thRunwayLengthFeet": "has a fourth runway length of {obj} feet",
        "5thRunwayLengthFeet": "has a fifth runway length of {obj} feet",
        # Generic entity predicates
        "leader": "leader is {obj}",
        "capital": "capital is {obj}",
        "language": "language is {obj}",
        "officialLanguage": "official language is {obj}",
        "currency": "currency is {obj}",
        "owner": "is owned by {obj}",
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
        "class": "belongs to the class {obj}",
        "division": "belongs to the division of {obj}",
        "order": "belongs to the order {obj}",
        "species": "is of the species {obj}",
        "demonym": "demonym is {obj}",
    }

    # Helper to format numbers nicely (remove trailing .0 and add commas)
    def _fmt_number(val: str) -> str:
        try:
            num = float(val.replace(",", ""))
            if num.is_integer():
                num = int(num)
            return str(num)
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
                phrase = tmpl.format(obj=fmt_obj)
            else:
                # Predicates that are better expressed with object first
                if t.predicate in {"mayor", "leader", "headquarter", "chief", "founder", "owner"}:
                    # e.g., "John Doe is the mayor of City"
                    phrase = f"{obj} is the {t.predicate} of {t.subject}"
                else:
                    pred = t.predicate.replace('_', ' ')
                    phrase = f"{pred} {obj}"
            parts.append((t.predicate, phrase, obj))

        # Combine parts into a fluent sentence
        if parts:
            if len(parts) == 1:
                pred, phrase, raw_obj = parts[0]
                # Special handling for a few common predicates
                if pred == "runwayLength":
                    sentence = f"The runway length of {subject} is {raw_obj}."
                elif pred == "runwayName":
                    sentence = f"The runway name of {subject} is {raw_obj}."
                elif pred == "1stRunwayLengthMetre":
                    sentence = f"The length of the first runway at {subject} is {raw_obj} metres."
                elif pred == "1stRunwayLengthFeet":
                    sentence = f"The length of the first runway at {subject} is {raw_obj} feet."
                elif pred == "1stRunwayNumber":
                    sentence = f"The first runway number of {subject} is {raw_obj}."
                elif pred == "5thRunwayNumber":
                    sentence = f"The fifth runway number of {subject} is {raw_obj}."
                elif pred == "1stRunwaySurfaceType":
                    sentence = f"The first runway at {subject} is made from {raw_obj}."
                elif pred == "4thRunwaySurfaceType":
                    sentence = f"The fourth runway at {subject} is made of {raw_obj.lower()}."
                elif pred == "runwaySurfaceType":
                    sentence = f"The runway surface at {subject} is {raw_obj}."
                elif pred == "locationIdentifier":
                    sentence = f"The location identifier for {subject} is {raw_obj}."
                elif pred == "icaoLocationIdentifier":
                    sentence = f"The ICAO code of {subject} is {raw_obj}."
                elif pred == "iataLocationIdentifier":
                    sentence = f"The IATA code of {subject} is {raw_obj}."
                elif pred == "capital":
                    sentence = f"The capital of {subject} is {raw_obj}."
                elif pred == "language":
                    # If object ends with "languages" use passive form
                    if raw_obj.lower().endswith("languages"):
                        sentence = f"The {raw_obj} are spoken in {subject}."
                    else:
                        # Strip redundant “ language” suffix if present
                        lang = raw_obj
                        if lang.lower().endswith(" language"):
                            lang = lang[: -len(" language")]
                        sentence = f"The language spoken in {subject} is {lang}."
                elif pred == "officialLanguage":
                    # Strip redundant “ language” suffix if present
                    lang = raw_obj
                    if lang.lower().endswith(" language"):
                        lang = lang[: -len(" language")]
                    sentence = f"The official language of {subject} is {lang}."
                elif pred == "demonym":
                    # Use a more natural phrasing for demonyms
                    # Ensure the demonym is pluralized by adding 's' if not already ending with s
                    dem = raw_obj
                    if not dem.lower().endswith("s"):
                        dem = dem + "s"
                    sentence = f"The people of {subject} are called {dem}."
                elif pred == "4thRunwayLengthFeet":
                    # More natural phrasing for specific runway length
                    sentence = f"The fourth runway at {subject} is {_fmt_number(raw_obj)} feet long."
                elif pred == "icaoLocationIdentifier":
                    sentence = f"The ICAO location identifier of {subject} is {raw_obj}."
                elif pred == "iataLocationIdentifier":
                    sentence = f"The IATA location identifier of {subject} is {raw_obj}."
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