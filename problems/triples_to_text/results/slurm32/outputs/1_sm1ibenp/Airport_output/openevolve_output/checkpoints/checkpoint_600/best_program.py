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
                parts.append((t.predicate, tmpl.format(obj=obj), obj))
            else:
                pred = t.predicate.replace('_', ' ')
                parts.append((t.predicate, f"{pred} {obj}", obj))

        # Combine parts into a fluent sentence
        if parts:
            if len(parts) == 1:
                pred, phrase, raw_obj = parts[0]
                # Special handling for a few common predicates
                if pred == "runwayLength":
                    sentence = f"The runway length at {subject} is {raw_obj} meters."
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
                elif pred == "runwaySurfaceType":
                    sentence = f"The runway surface at {subject} is {raw_obj}."
                elif pred == "locationIdentifier":
                    sentence = f"The location identifier for {subject} is {raw_obj}."
                elif pred == "icaoLocationIdentifier":
                    sentence = f"The ICAO code for {subject} is {raw_obj}."
                elif pred == "iataLocationIdentifier":
                    sentence = f"The IATA code for {subject} is {raw_obj}."
                elif pred == "capital":
                    sentence = f"The capital of {subject} is {raw_obj}."
                elif pred in ("language", "officialLanguage"):
                    # Strip redundant “ language” suffix if present
                    lang = raw_obj
                    if lang.lower().endswith(" language"):
                        lang = lang[: -len(" language")]
                    if pred == "language":
                        sentence = f"The language spoken in {subject} is {lang}."
                    else:  # officialLanguage
                        sentence = f"The official language of {subject} is {lang}."
                else:
                    sentence = f"{subject} {phrase}."
            else:
                # For multiple predicates we keep the original style
                phrase_list = [p for _, p, _ in parts]
                sentence = f"{subject} " + ", ".join(phrase_list[:-1]) + ", and " + phrase_list[-1] + "."
            sentences.append(sentence)

    return " ".join(sentences)

# EVOLVE-BLOCK-END