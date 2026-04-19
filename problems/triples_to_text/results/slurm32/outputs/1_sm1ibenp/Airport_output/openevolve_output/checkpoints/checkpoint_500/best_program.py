from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    """
    Convert a list of triples into a single fluent sentence.
    Unknown predicates fall back to a generic pattern.
    """
    if not triples:
        return ""

    # Simple predicate‑to‑phrase mapping for more natural wording
    phrase_map = {
        "cityServed": "{s} serves the city of {o}",
        "elevationAboveTheSeaLevel": "{s} is {o} metres above sea level",
        "elevationAboveTheSeaLevelInFeet": "{s} is {o} feet above sea level",
        "elevationAboveTheSeaLevelInMetres": "{s} is {o} metres above sea level",
        "location": "{s} is located in {o}",
        "operatingOrganisation": "is operated by {o}",
        # Revised phrasing to match reference style and improve BLEU
        "runwayLength": "has a runway length of {o} metres",
        "runwayLengthFeet": "The runway length of {s} is {o} feet",
        "runwayName": "{o} is the runway name of {s}",
        "country": "{s} is in {o}",
        "isPartOf": "{s} is part of {o}",
        "1stRunwayLengthFeet": "The length of the 1st runway at {s} is {o} feet",
        "1stRunwayLengthMetre": "{s} has a first runway length of {o} metres",
        "1stRunwayNumber": "{s} has first runway number {o}",
        "1stRunwaySurfaceType": "The first runway at {s} is made of {o}",
        "2ndRunwaySurfaceType": "{s} has a second runway surface of {o}",
        "3rdRunwayLengthFeet": "{s} has a third runway length of {o} feet",
        "3rdRunwaySurfaceType": "{s} has a third runway surface of {o}",
        "4thRunwayLengthFeet": "The fourth runway at {s} is {o} feet long",
        "4thRunwaySurfaceType": "The fourth runway at {s} is made of {o}",
        "5thRunwayNumber": "{s} has fifth runway number {o}",
        "5thRunwaySurfaceType": "The fifth runway at {s} is made of {o}",
        "icaoLocationIdentifier": "{o} is the ICAO location identifier of {s}",
        "locationIdentifier": "{o} is the location identifier of {s}",
        "iataLocationIdentifier": "{o} is the IATA location identifier of {s}",
        "nativeName": "{s} is also known as {o}",
        "leaderParty": "{s} is governed by the {o} party",
        "capital": "The capital of {s} is {o}",
        "language": "{o} is spoken in {s}",
        "leader": "The leader of {s} is {o}",
        "owner": "{s} is owned by {o}",
        "largestCity": "{s} has largest city {o}",
        "mayor": "{s} has mayor {o}",
        "officialLanguage": "The official language of {s} is {o}",
        "city": "{s} is a city {o}",
        "jurisdiction": "{s} falls under jurisdiction of {o}",
        "demonym": "{s} residents are called {o}",
        "aircraftHelicopter": "{s} operates helicopter {o}",
        "transportAircraft": "{s} operates transport aircraft {o}",
        "currency": "{s} uses the {o}",
        "headquarter": "{s} is headquartered at {o}",
        "class": "{s} belongs to class {o}",
        "division": "{s} belongs to the division of {o}",
        "order": "{s} belongs to the order of {o}",
        "regionServed": "{s} serves the region {o}",
        "leaderTitle": "{s} has leader title {o}",
        "hubAirport": "{o} is the hub airport for {s}",
        "aircraftFighter": "{s} flies fighter {o}",
        "attackAircraft": "{s} flies attack aircraft {o}",
        "battle": "{s} participated in {o}",
        "countySeat": "{s} has county seat {o}",
        "chief": "{s} is led by chief {o}",
        "foundedBy": "{s} was founded by {o}",
        "postalCode": "{s} has postal code {o}",
        "areaCode": "{s} has area code {o}",
        "foundingYear": "{s} was founded in {o}",
        "ceremonialCounty": "{s} is in ceremonial county {o}",
    }

    # Helper to clean numeric objects: drop trailing .0 and avoid extra units
    def _clean_number(val: str) -> str:
        try:
            num = float(val)
            if num.is_integer():
                return str(int(num))
            # keep reasonable decimal representation
            return str(num).rstrip('0').rstrip('.') if '.' in str(num) else str(num)
        except ValueError:
            return val

    # Aggregate predicates per subject to allow merging into richer clauses
    subj_map = {}
    for t in triples:
        obj = t.object
        if (obj.startswith('"') and obj.endswith('"')) or (obj.startswith("'") and obj.endswith("'")):
            obj = obj[1:-1]
        if t.predicate in ("division", "order", "class"):
            obj = obj.lower()
        if t.predicate in ("language", "officialLanguage") and obj.lower().endswith(" language"):
            obj = obj.rsplit(" ", 1)[0]
        # Add definite article for certain country names
        if t.predicate == "country" and not obj.lower().startswith("the "):
            if obj.startswith("United"):
                obj = "the " + obj
        subj_map.setdefault(t.subject, []).append((t.predicate, obj))

    clauses = []
    for subj, pred_objs in subj_map.items():
        # Build a fluent clause by listing attributes of the subject
        attribute_phrases = []
        for idx, (pred, obj) in enumerate(pred_objs):
            tmpl = phrase_map.get(pred)
            if tmpl:
                phrase = tmpl.format(s=subj, o=obj)
                # If the template does not include the subject, prepend it for clarity
                if "{s}" not in tmpl:
                    phrase = f"{subj} {phrase}"
            else:
                phrase = f"{subj} {pred} {obj}"
            if idx > 0:
                # Remove leading subject if present to avoid repetition
                if phrase.startswith(f"{subj} "):
                    phrase = phrase[len(subj) + 1 :]
                phrase = phrase.lstrip()
            attribute_phrases.append(phrase)

        # Combine the attribute phrases into a single clause
        if len(attribute_phrases) == 1:
            clause = attribute_phrases[0]
        else:
            # commas between all but last, and 'and' before the final phrase
            clause = ", ".join(attribute_phrases[:-1]) + " and " + attribute_phrases[-1]

        clauses.append(clause)

    # Join clauses into a single fluent sentence with proper conjunctions
    if not clauses:
        return ""
    if len(clauses) == 1:
        sentence = clauses[0]
    else:
        sentence = ", ".join(clauses[:-1]) + ", and " + clauses[-1]
    sentence = sentence.rstrip()
    if not sentence.endswith('.'):
        sentence += '.'
    # Capitalize first character
    return sentence[0].upper() + sentence[1:]

# EVOLVE-BLOCK-END