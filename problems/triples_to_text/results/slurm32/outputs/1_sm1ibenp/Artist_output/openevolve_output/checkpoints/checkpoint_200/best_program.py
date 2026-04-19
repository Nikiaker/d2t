from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    """Convert a list of triples about artists (or related entities) into a fluent description."""
    if not triples:
        return ""

    def _clean(value: str) -> str:
        """Strip surrounding quotes and whitespace."""
        return value.strip().strip('"').strip("'")

    # Mapping of predicates to natural‑language fragments.
    # The placeholder {obj} will be replaced by the cleaned object string.
    pred_map = {
        "birthDate": "was born on {obj}",
        "birthYear": "was born in {obj}",
        "birthPlace": "was born in {obj}",
        "origin": "originates from {obj}",
        "genre": "genre is {obj}",
        "instrument": "plays the {obj}",
        "occupation": "is a {obj}",
        "nationality": "is {obj}",
        "associatedBand/associatedMusicalArtist": "performed with {obj}",
        "recordLabel": "is signed to {obj}",
        "activeYearsStartYear": "started their career in {obj}",
        "activeYearsEndYear": "ended their career in {obj}",
        "deathDate": "died on {obj}",
        "deathPlace": "died in {obj}",
        "alternativeName": "is also known as {obj}",
        "stylisticOrigin": "has its stylistic origins in {obj}",
        "musicFusionGenre": "is fused with {obj}",
        "musicSubgenre": "is a subgenre of {obj}",
        "derivative": "derives from {obj}",
        "location": "is located in {obj}",
        "governingBody": "is governed by {obj}",
        # leader handled specially below
        "leaderTitle": "has leader title {obj}",
        "country": "belongs to the country {obj}",
        "ethnicGroup": "has ethnic group {obj}",
        "parentCompany": "is owned by {obj}",
        "bandMember": "has band member {obj}",
        "capital": "has capital {obj}",
        "anthem": "has anthem {obj}",
        "currency": "uses the currency {obj}",
        "demonym": "has demonym {obj}",
        "isPartOf": "is part of {obj}",
        "distributingCompany": "is distributed by {obj}",
        "training": "was trained at {obj}",
        "populationDensity": "has a population density of {obj}",
        "meaning": "means \"{obj}\"",
        "longName": "full name is \"{obj}\"",
        "areaTotal": "covers an area of {obj}",
        "foundingDate": "was founded on {obj}",
        "elevationAboveTheSeaLevel": "lies at {obj} meters above sea level",
        "postalCode": "has postal code {obj}",
        "language": "speaks {obj}",
        "officialLanguage": "has official language {obj}",
        "background": "is a {obj}",
    }

    # Build a richer description per subject, handling key artist predicates specially.
    sentences: list[str] = {}

    def _pronoun(_subj: str) -> str:
        # Simple gender‑neutral pronoun; could be enhanced with name‑based heuristics.
        return "their"

    def _join_items(items: list[str]) -> str:
        """Join a list of strings with commas and 'and' for natural‑language lists."""
        if not items:
            return ""
        if len(items) == 1:
            return items[0]
        if len(items) == 2:
            return f"{items[0]} and {items[1]}"
        return ", ".join(items[:-1]) + f", and {items[-1]}"

    # Collect information per subject.
    subject_info: dict[str, dict[str, list[str]]] = {}
    for t in triples:
        subj = t.subject
        pred = t.predicate
        obj = _clean(t.object)

        if pred == "leader":
            # “Boris Johnson is a leader in London.”
            sentences.setdefault("", []).append(f"{obj} is a leader in {subj}.")
            continue

        subject_info.setdefault(subj, {}).setdefault(pred, []).append(obj)

    # Produce sentences.
    result_sentences: list[str] = []
    for subj, info in subject_info.items():
        parts: list[str] = []

        # Primary artist descriptors.
        if "genre" in info:
            genre = info.pop("genre")[0]
            parts.append(f"is a {genre.lower()} artist")
        if "background" in info:
            bg = info.pop("background")[0]
            parts.append(f"is a {bg.lower()}")
        if "instrument" in info:
            instr = info.pop("instrument")[0]
            parts.append(f"plays the {instr}")
        if "occupation" in info:
            occ = info.pop("occupation")[0]
            parts.append(f"is a {occ.lower()}")
        if "associatedBand/associatedMusicalArtist" in info:
            bands = info.pop("associatedBand/associatedMusicalArtist")
            joined = _join_items(bands)
            parts.append(f"is associated with {joined}")
        if "recordLabel" in info:
            rl = info.pop("recordLabel")[0]
            parts.append(f"is signed to {rl}")
        if "activeYearsStartYear" in info:
            start = info.pop("activeYearsStartYear")[0]
            parts.append(f"started { _pronoun(subj) } career in {start}")
        if "activeYearsEndYear" in info:
            end = info.pop("activeYearsEndYear")[0]
            parts.append(f"ended { _pronoun(subj) } career in {end}")
        if "birthDate" in info:
            bd = info.pop("birthDate")[0]
            parts.append(f"was born on {bd}")
        elif "birthYear" in info:
            by = info.pop("birthYear")[0]
            parts.append(f"was born in {by}")
        if "birthPlace" in info:
            bp = info.pop("birthPlace")[0]
            # If we already added a birth date/year, attach place with 'in'.
            if any(p.startswith("was born") for p in parts):
                parts.append(f"in {bp}")
            else:
                parts.append(f"was born in {bp}")
        if "nationality" in info:
            nat = info.pop("nationality")[0]
            parts.append(f"is {nat}")

        # Fallback for any remaining predicates.
        for pred, objs in list(info.items()):
            for o in objs:
                template = pred_map.get(pred, f"{pred} {o}")
                clause = template.format(obj=o) if "{obj}" in template else template
                parts.append(clause)
            info.pop(pred, None)

        sentence = f"{subj} " + ", ".join(parts) + "."
        result_sentences.append(sentence[0].upper() + sentence[1:])

    # Add any special leader sentences collected earlier.
    if "" in sentences:
        result_sentences.extend(sentences[""])

    # Combine all sentences into one paragraph.
    return " ".join(result_sentences)

# EVOLVE-BLOCK-END