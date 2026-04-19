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
        "operatingOrganisation": "{s} is operated by {o}",
        # Revised phrasing to match reference style and improve BLEU
        "runwayLength": "The runway length of {s} is {o}",
        "runwayLengthFeet": "The runway length of {s} is {o} feet",
        # Use object‑first phrasing to match reference style
        "runwayName": "{o} is the runway name of {s}",
        "country": "{s} is in {o}",
        "isPartOf": "{s} is part of {o}",
        "1stRunwayLengthFeet": "{s} has a first runway length of {o} feet",
        "1stRunwayLengthMetre": "{s} has a first runway length of {o} metres",
        "1stRunwayNumber": "{s} has first runway number {o}",
        "1stRunwaySurfaceType": "The first runway at {s} is made of {o}",
        "2ndRunwaySurfaceType": "{s} has a second runway surface of {o}",
        "3rdRunwayLengthFeet": "{s} has a third runway length of {o} feet",
        "3rdRunwaySurfaceType": "{s} has a third runway surface of {o}",
        # More natural runway length phrasing
        "4thRunwayLengthFeet": "The fourth runway at {s} is {o} feet long",
        "4thRunwaySurfaceType": "The fourth runway at {s} is made of {o}",
        "5thRunwayNumber": "{s} has fifth runway number {o}",
        "5thRunwaySurfaceType": "The fifth runway at {s} is made of {o}",
        # Object‑first phrasing for identifier predicates
        "icaoLocationIdentifier": "{o} is the ICAO location identifier of {s}",
        "locationIdentifier": "{s} has location identifier {o}",
        "iataLocationIdentifier": "{s} has IATA identifier {o}",
        "nativeName": "{s} is also known as {o}",
        "leaderParty": "{s} is governed by the {o} party",
        "capital": "The capital of {s} is {o}",
        "language": "the language of {s} is {o}",
        "leader": "The leader of {s} is {o}",
        "owner": "{s} is owned by {o}",
        "largestCity": "{s} has largest city {o}",
        "mayor": "{s} has mayor {o}",
        "officialLanguage": "{s} has official language {o}",
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
        "hubAirport": "{s} uses hub airport {o}",
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

    # Aggregate objects for predicates that may appear multiple times for the same subject
    agg = {}
    for t in triples:
        # Strip surrounding quotes from object if present
        obj = t.object
        if (obj.startswith('"') and obj.endswith('"')) or (obj.startswith("'") and obj.endswith("'")):
            obj = obj[1:-1]
        # Normalize object case for certain predicates
        if t.predicate in ("division", "order", "class"):
            obj = obj.lower()
        # Clean language/object suffixes for more natural phrasing
        if t.predicate in ("language", "officialLanguage") and obj.lower().endswith(" language"):
            obj = obj.rsplit(" ", 1)[0]
        key = (t.subject, t.predicate)
        agg.setdefault(key, []).append(obj)

    clauses = []
    for (subj, pred), objs in agg.items():
        # Combine multiple objects with 'and' when appropriate
        if len(objs) > 1:
            # join with commas and 'and' for the last item
            obj_str = ", ".join(objs[:-1]) + " and " + objs[-1]
        else:
            obj_str = objs[0]

        tmpl = phrase_map.get(pred)
        if tmpl:
            clause = tmpl.format(s=subj, o=obj_str)
        else:
            clause = f"{subj} has {pred} {obj_str}"
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