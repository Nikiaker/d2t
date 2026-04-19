from dataclasses import dataclass
import re

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

    # Quick handling for single‑triple cases that have a very common natural phrasing.
    # This avoids awkward constructions like “United Kingdom has demonym British people.”
    if len(triples) == 1:
        t = triples[0]
        subj = t.subject
        pred = t.predicate
        obj = t.object.strip().strip('"').strip("'")
        # Simple one‑triple formulations with more natural phrasing.
        if pred == "demonym":
            return f"People from {subj} are called {obj}."
        if pred == "genre":
            # Use a more natural phrasing for musical genre.
            return f"{subj} performs {obj.lower()} music."
        if pred == "derivative":
            # Subject is derived from the object.
            return f"{subj} is derived from {obj}."
        if pred == "associatedBand/associatedMusicalArtist":
            # Use a neutral phrasing for band association.
            return f"{subj} is associated with the band {obj}."
        if pred == "instrument":
            # If the subject looks like a musical genre (contains the word "music"), use "uses".
            if "music" in subj.lower():
                return f"{subj} uses the {obj}."
            else:
                return f"{subj} plays the {obj}."

    def _clean(value: str) -> str:
        """Strip surrounding quotes, whitespace and parenthetical notes like \"(band)\"."""
        val = value.strip().strip('"').strip("'")
        # Remove parenthetical descriptors e.g., "Twilight (band)" -> "Twilight"
        val = re.sub(r'\s*\([^)]*\)', '', val).strip()
        return val

    # Mapping of predicates to natural‑language fragments.
    # The placeholder {obj} will be replaced by the cleaned object string.
    pred_map = {
        "birthDate": "was born on {obj}",
        "birthYear": "was born in {obj}",
        "birthPlace": "was born in {obj}",
        "origin": "is from {obj}",
        "genre": "performs {obj} music",
        "instrument": "plays {obj}",
        "occupation": "is a {obj}",
        "nationality": "is {obj}",
        "associatedBand/associatedMusicalArtist": "is a member of the band {obj}",
        "recordLabel": "is signed to {obj}",
        "activeYearsStartYear": "began performing in {obj}",
        "activeYearsEndYear": "ended their career in {obj}",
        "deathDate": "died on {obj}",
        "deathPlace": "died in {obj}",
        "alternativeName": "is also known as {obj}",
        "stylisticOrigin": "has its stylistic origins in {obj}",
        "musicFusionGenre": "is fused with {obj}",
        "musicSubgenre": "has a subgenre {obj}",
        "derivative": "has a derivative {obj}",
        "location": "is located in {obj}",
        "governingBody": "is governed by {obj}",
        # leader is handled specially to place the object as the subject.
        "leader": "SPECIAL_LEADER",
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

    # Group objects by subject and predicate to enable aggregation.
    subject_pred_objs: dict[str, dict[str, list[str]]] = {}
    for t in triples:
        subj = t.subject
        pred = t.predicate
        obj = _clean(t.object)
        subject_pred_objs.setdefault(subj, {}).setdefault(pred, []).append(obj)

    # Cache information about each entity (especially bands) for cross‑reference.
    # This allows us to enrich statements like “plays for the X band which performs Y music”.
    band_info = {s: preds for s, preds in subject_pred_objs.items()}

    # Helper to join multiple objects with commas and “and”.
    def _join_objs(objs: list[str]) -> str:
        if not objs:
            return ""
        if len(objs) == 1:
            return objs[0]
        return ", ".join(objs[:-1]) + " and " + objs[-1]

    # Aggregated phrase templates for predicates with multiple values.
    agg_map = {
        "recordLabel": "record labels are {objlist}",
        "associatedBand/associatedMusicalArtist": "is associated with {objlist}",
        "genre": "genres are {objlist}",
        "instrument": "plays {objlist}",
        "occupation": "is a {objlist}",
        "nationality": "is {objlist}",
        "language": "speaks {objlist}",
        "officialLanguage": "has official language {objlist}",
        "background": "is a {objlist}",
    }

    sentences: list[str] = []
    for subj, pred_objs in subject_pred_objs.items():
        # Define a priority order for predicates to produce a natural flow.
        priority = [
            "genre", "instrument", "occupation", "background", "activeYearsStartYear",
            "associatedBand/associatedMusicalArtist", "birthDate", "birthYear",
            "birthPlace", "origin", "nationality", "recordLabel",
            "activeYearsEndYear", "deathDate", "deathPlace", "alternativeName",
            "stylisticOrigin", "musicFusionGenre", "musicSubgenre", "derivative",
            "location", "governingBody", "leader", "leaderTitle",
            "country", "ethnicGroup", "parentCompany", "bandMember",
            "capital", "anthem", "currency", "demonym", "isPartOf",
            "distributingCompany", "training", "populationDensity",
            "meaning", "longName", "areaTotal", "foundingDate",
            "elevationAboveTheSeaLevel", "postalCode", "language",
            "officialLanguage"
        ]

        # Helper to format a single predicate clause.
        def _format_clause(pred: str, objs: list[str]) -> str:
            # Special case for musicFusionGenre where object becomes subject.
            if pred == "musicFusionGenre":
                obj = _join_objs(objs)
                subj_clean = subj.lower()
                return f"{obj} is a fusion of {subj_clean}"
            # Special case for leader where object becomes the leader.
            if pred == "leader":
                return f"The leader of {subj} is {objs[0]}"
            # Special case for leaderTitle where the object is the title of the leader.
            if pred == "leaderTitle":
                return f"The leader title of {subj} is {objs[0]}"
            # Special case for language to produce a more natural phrasing.
            if pred == "language":
                return f"{subj}'s language is {objs[0]}"
            # Special case for birthDate to format a readable date.
            if pred == "birthDate":
                try:
                    from datetime import datetime
                    dt = datetime.strptime(objs[0], "%Y-%m-%d")
                    formatted = dt.strftime("%B %-d, %Y")
                except Exception:
                    formatted = objs[0]
                return f"was born on {formatted}"
            # Choose template, handling aggregation.
            if len(objs) > 1 and pred in agg_map:
                template = agg_map[pred]
                objlist = _join_objs(objs)
                return template.format(objlist=objlist)
            else:
                template = pred_map.get(pred, f"{pred} {{obj}}")
                # Refine some common templates for better fluency.
                if pred == "instrument":
                    obj = _join_objs(objs)
                    # If the instrument is actually a vocal role, describe as singer.
                    low = obj.lower()
                    if low in {"singing", "vocals", "voice"} or "vocal" in low:
                        return f"is a singer"
                    # Otherwise keep standard phrasing, adding article if needed.
                    if not low.startswith("the "):
                        obj = "the " + obj
                    return template.format(obj=obj)
                # Use a more natural phrasing for band association.
                # Special handling for predicates where the object is the primary entity.
                if pred == "ethnicGroup":
                    # e.g., "Kashubians are an ethnic group of Poland."
                    return f"{_join_objs(objs)} are an ethnic group of {subj}"
                if pred == "genre":
                    obj = _join_objs(objs).lower()
                    # Avoid duplicate “music” when the genre name already ends with “music”.
                    if obj.rstrip().endswith("music"):
                        return f"performs {obj}"
                    else:
                        return f"performs {obj} music"
                return template.format(obj=_join_objs(objs))

        # Build clauses following the priority order, then any remaining predicates.
        processed = set()
        clauses: list[str] = []
        # Combine genre and instrument into a more natural phrase when both are present.
        if "genre" in pred_objs and "instrument" in pred_objs:
            instr = _join_objs(pred_objs["instrument"])
            gen = _join_objs(pred_objs["genre"])
            # Build a phrase like "is an electric guitar player of post-metal music"
            # Use lower‑case for natural flow, but keep proper nouns capitalised if needed.
            phrase = f"is a {instr.lower()} player of {gen.lower()} music"
            clauses.append(phrase)
            processed.update(["genre", "instrument"])
        # Process remaining predicates in the defined priority order.
        for pred in priority:
            if pred in pred_objs and pred not in processed:
                clauses.append(_format_clause(pred, pred_objs[pred]))
                processed.add(pred)
        # Process any predicates that were not covered by the priority list.
        for pred, objs in pred_objs.items():
            if pred not in processed:
                clauses.append(_format_clause(pred, objs))

        # Combine clauses into a single fluent sentence.
        if not clauses:
            body = ""
        elif len(clauses) == 1:
            body = clauses[0]
        else:
            # Join multiple clauses with commas and an "and" before the last clause.
            body = ", ".join(clauses[:-1]) + " and " + clauses[-1]
        sentence = f"{subj} {body}."
        # Capitalize the first character of the sentence.
        sentences.append(sentence[0].upper() + sentence[1:])

    # Join sentences for different subjects.
    return " ".join(sentences)

# EVOLVE-BLOCK-END