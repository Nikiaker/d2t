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

    import re

    def clean(text: str) -> str:
        t = str(text).strip()
        if len(t) >= 2 and t[0] == '"' and t[-1] == '"':
            t = t[1:-1]
        return t

    def join_parts(parts: list[str]) -> str:
        if not parts:
            return ""
        if len(parts) == 1:
            return parts[0]
        if len(parts) == 2:
            return f"{parts[0]} and {parts[1]}"
        return f"{', '.join(parts[:-1])}, and {parts[-1]}"

    def humanize_predicate(p: str) -> str:
        x = p.replace("_", " ")
        x = re.sub(r"([a-z])([A-Z])", r"\1 \2", x)
        return x.lower()

    templates = {
        "cityServed": "serves {o}",
        "elevationAboveTheSeaLevel": "has an elevation of {o} metres above sea level",
        "location": "is located in {o}",
        "operatingOrganisation": "is operated by {o}",
        "runwayLength": "has a runway length of {o} metres",
        "runwayName": "has a runway named {o}",
        "country": "is in {o}",
        "isPartOf": "is part of {o}",
        "icaoLocationIdentifier": "has the ICAO location identifier {o}",
        "locationIdentifier": "has the location identifier {o}",
        "elevationAboveTheSeaLevelInFeet": "has an elevation of {o} feet above sea level",
        "iataLocationIdentifier": "has the IATA location identifier {o}",
        "nativeName": "is also known as {o}",
        "leaderParty": "has {o} as its leader party",
        "capital": "has the capital {o}",
        "language": "has {o} as its language",
        "leader": "is led by {o}",
        "owner": "is owned by {o}",
        "largestCity": "has the largest city {o}",
        "elevationAboveTheSeaLevelInMetres": "has an elevation of {o} metres above sea level",
        "administrativeArrondissement": "is in the arrondissement of {o}",
        "mayor": "has the mayor {o}",
        "runwaySurfaceType": "has a runway surface of {o}",
        "officialLanguage": "has {o} as an official language",
        "city": "is in {o}",
        "jurisdiction": "has jurisdiction over {o}",
        "demonym": "has the demonym {o}",
        "aircraftHelicopter": "uses {o} as a helicopter",
        "transportAircraft": "uses {o} as a transport aircraft",
        "currency": "uses the currency {o}",
        "headquarter": "is headquartered at {o}",
        "class": "belongs to class {o}",
        "division": "belongs to division {o}",
        "order": "belongs to order {o}",
        "regionServed": "serves {o}",
        "leaderTitle": "has leader title {o}",
        "hubAirport": "has hub airport {o}",
        "aircraftFighter": "uses {o} as a fighter aircraft",
        "attackAircraft": "uses {o} as an attack aircraft",
        "battle": "fought in {o}",
        "countySeat": "has county seat {o}",
        "chief": "has chief {o}",
        "foundedBy": "was founded by {o}",
        "postalCode": "has postal code {o}",
        "areaCode": "has area code {o}",
        "foundingYear": "was founded in {o}",
        "ceremonialCounty": "is in the ceremonial county of {o}",
    }

    grouped: dict[str, dict[str, list[str]]] = {}
    subject_order: list[str] = []

    for t in triples:
        s = clean(t.subject)
        p = t.predicate
        o = clean(t.object)
        if s not in grouped:
            grouped[s] = {}
            subject_order.append(s)
        grouped[s].setdefault(p, []).append(o)

    subject_sentences: list[str] = []
    for s in subject_order:
        pred_map = grouped[s]
        phrases: list[str] = []

        for p, objs in pred_map.items():
            unique_objs = list(dict.fromkeys(objs))
            if p == "country":
                unique_objs = [f"the {x}" if x == "United States" else x for x in unique_objs]
            if p == "isPartOf" and len(unique_objs) > 1:
                obj_text = " as well as ".join(unique_objs)
            else:
                obj_text = join_parts(unique_objs)

            m = re.match(r"^(\d+(?:st|nd|rd|th))Runway(LengthFeet|LengthMetre|SurfaceType|Number)$", p)
            if m:
                idx, kind = m.groups()
                if kind == "LengthFeet":
                    phrase = f"has its {idx} runway length of {obj_text} feet"
                elif kind == "LengthMetre":
                    phrase = f"has its {idx} runway length of {obj_text} metres"
                elif kind == "SurfaceType":
                    phrase = f"has {obj_text} as the surface type of its {idx} runway"
                else:
                    phrase = f"has runway number {obj_text} for its {idx} runway"
            elif p == "isPartOf":
                phrase = f"is part of {obj_text}"
            elif p == "language":
                phrase = f"has {obj_text} as its language"
            elif p == "officialLanguage":
                phrase = f"has {obj_text} as an official language"
            elif p in templates:
                phrase = templates[p].format(o=obj_text)
            else:
                phrase = f"has {humanize_predicate(p)} {obj_text}"

            phrases.append(phrase)

        subject_sentences.append(f"{s} {join_parts(phrases)}")

    if len(subject_sentences) == 1:
        return subject_sentences[0] + "."

    if len(subject_sentences) == 2:
        return f"{subject_sentences[0]}, and {subject_sentences[1]}."

    return f"{', '.join(subject_sentences[:-1])}, and {subject_sentences[-1]}."

# EVOLVE-BLOCK-END