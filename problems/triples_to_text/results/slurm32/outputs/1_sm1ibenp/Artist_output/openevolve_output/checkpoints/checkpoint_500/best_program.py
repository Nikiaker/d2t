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
        "origin": "is from {obj}",
        "genre": "is a {obj} artist",
        "instrument": "plays {obj}",
        "occupation": "is a {obj}",
        "nationality": "is {obj}",
        "associatedBand/associatedMusicalArtist": "was associated with {obj}",
        "recordLabel": "is signed to {obj}",
        "activeYearsStartYear": "began his career in {obj}",
        "activeYearsEndYear": "ended their career in {obj}",
        "deathDate": "died on {obj}",
        "deathPlace": "died in {obj}",
        "alternativeName": "is also known as {obj}",
        "stylisticOrigin": "has its stylistic origins in {obj}",
        "musicFusionGenre": "is fused with {obj}",
        "musicSubgenre": "has subgenre {obj}",
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
            "instrument", "genre", "associatedBand/associatedMusicalArtist",
            "background", "occupation", "birthDate", "birthYear",
            "birthPlace", "origin", "nationality", "recordLabel",
            "activeYearsStartYear", "activeYearsEndYear", "deathDate",
            "deathPlace", "alternativeName", "stylisticOrigin",
            "musicFusionGenre", "musicSubgenre", "derivative",
            "location", "governingBody", "leader", "leaderTitle",
            "country", "ethnicGroup", "parentCompany", "bandMember",
            "capital", "anthem", "currency", "demonym", "isPartOf",
            "distributingCompany", "training", "populationDensity",
            "meaning", "longName", "areaTotal", "foundingDate",
            "elevationAboveTheSeaLevel", "postalCode", "language",
            "officialLanguage"
        ]

        # Helper to get extra information about a genre (or any entity) that appears as a subject elsewhere.
        def _genre_extra_info(g: str) -> str:
            extra_parts = []
            # Look for predicates that are meaningful to describe a genre.
            genre_info = subject_pred_objs.get(g, {})
            # Instruments used in the genre.
            if "instrument" in genre_info:
                instruments = _join_objs(genre_info["instrument"])
                extra_parts.append(f"uses {instruments}")
            # Stylistic origins of the genre.
            if "stylisticOrigin" in genre_info:
                origins = _join_objs(genre_info["stylisticOrigin"])
                extra_parts.append(f"originated from {origins}")
            # Derivative genres.
            if "derivative" in genre_info:
                derivatives = _join_objs(genre_info["derivative"])
                extra_parts.append(f"has derivative {derivatives}")
            # Fusion genres.
            if "musicFusionGenre" in genre_info:
                fusions = _join_objs(genre_info["musicFusionGenre"])
                extra_parts.append(f"is fused with {fusions}")
            # Subgenres.
            if "musicSubgenre" in genre_info:
                subgs = _join_objs(genre_info["musicSubgenre"])
                extra_parts.append(f"has subgenre {subgs}")
            if extra_parts:
                return " which " + " and ".join(extra_parts)
            return ""

        # Helper to format a single predicate clause.
        def _format_clause(pred: str, objs: list[str]) -> str:
            # Special case for musicFusionGenre where object becomes subject.
            if pred == "musicFusionGenre":
                obj = _join_objs(objs)
                subj_clean = subj.lower()
                return f"{obj} is a fusion of {subj_clean}"
            # Special case for leader where object becomes the leader.
            if pred == "leader":
                # Produce a clause where the object is the leader of the subject.
                return f"The leader of {subj} is {objs[0]}"
            # Simple handling for genre: state the music style performed.
            if pred == "genre":
                # Join multiple genres, lowercasing for natural phrasing.
                lowered = [o.lower() for o in objs]
                genre_list = _join_objs(lowered)
                # If the genre already contains the word “music”, avoid duplicating it.
                if any("music" in g for g in lowered):
                    return f"performs {genre_list}"
                else:
                    return f"performs {genre_list} music"
            # Choose template, handling aggregation.
            if len(objs) > 1 and pred in agg_map:
                template = agg_map[pred]
                objlist = _join_objs(objs)
                return template.format(objlist=objlist)
            else:
                template = pred_map.get(pred, f"{pred} {{obj}}")
                # Refine some common templates for better fluency.
                if pred == "instrument":
                    # Add article "the" unless object already starts with "the ".
                    obj = _join_objs(objs)
                    if not obj.lower().startswith("the "):
                        obj = "the " + obj
                    return template.format(obj=obj)
                # Use a more natural phrasing for band association.
                if pred == "associatedBand/associatedMusicalArtist":
                    # Use a neutral phrasing that works for both bands and musical artists.
                    objlist = _join_objs(objs)
                    return f"is associated with {objlist}"
                return template.format(obj=_join_objs(objs))

        # Build clauses following the priority order, then any remaining predicates.
        processed = set()
        clauses: list[str] = []
        for pred in priority:
            if pred in pred_objs:
                clauses.append(_format_clause(pred, pred_objs[pred]))
                processed.add(pred)
        for pred, objs in pred_objs.items():
            if pred not in processed:
                clauses.append(_format_clause(pred, objs))

        # Combine clauses into one fluent sentence.
        if len(clauses) == 1:
            body = clauses[0]
        else:
            body = ", ".join(clauses[:-1]) + ", and " + clauses[-1]
        sentence = f"{subj} {body}."
        sentences.append(sentence[0].upper() + sentence[1:])

    # Join sentences for different subjects.
    return " ".join(sentences)

# EVOLVE-BLOCK-END