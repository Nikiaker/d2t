from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    """Convert a list of triples about an athlete (or related entities) into a fluent sentence."""
    if not triples:
        return ""

    # Mapping from predicate to a formatting lambda (subject, object) -> phrase
    predicate_map = {
        "birthDate": lambda s, o: f"{s} was born on {o}",
        "birthYear": lambda s, o: f"{s} was born in {o}",
        "birthPlace": lambda s, o: f"{s} was born in {o}",
        "height": lambda s, o: f"{s} is {o} meters tall",
        "weight": lambda s, o: f"{s} weighs {o}",
        "position": lambda s, o: f"{s} plays as a {o}",
        "club": lambda s, o: f"{s} plays for {o}",
        "currentclub": lambda s, o: f"{s} plays for {o}",
        "formerTeam": lambda s, o: f"{s} formerly played for {o}",
        "league": lambda s, o: f"{s} competes in the {o}",
        # Revised phrasing for clearer ownership / roles
        "manager": lambda s, o: f"{o} is the manager of {s}",
        "coach": lambda s, o: f"{o} is the coach of {s}",
        "draftTeam": lambda s, o: f"{s}'s draft team is {o}",
        "draftYear": lambda s, o: f"{s} was drafted in {o}",
        "draftRound": lambda s, o: f"{s} was selected in round {o}",
        "draftPick": lambda s, o: f"{s} was the {o}th pick",
        "playerNumber": lambda s, o: f"{s} wears number {o}",
        "currentteam": lambda s, o: f"{s} currently plays for {o}",
        "debutTeam": lambda s, o: f"{s} debuted with {o}",
        # Additional predicates beyond the athlete domain
        "leader": lambda s, o: f"{o} is the leader of {s}",
        "deathPlace": lambda s, o: f"{s} died in {o}",
        "isPartOf": lambda s, o: f"{s} is part of {o}",
        "country": lambda s, o: f"{s} is in {o}",
        "city": lambda s, o: f"{s} is based in {o}",
        "owner": lambda s, o: f"{o} owns {s}",
        "chairman": lambda s, o: f"{o} is the chairman of {s}",
        "generalManager": lambda s, o: f"{o} is the general manager of {s}",
        "stadium": lambda s, o: f"{s}'s stadium is {o}",
        "ground": lambda s, o: f"{s}'s ground is located in {o}",
        "anthem": lambda s, o: f"The anthem of {s} is {o}",
        "ethnicGroup": lambda s, o: f"{s} has an ethnic group of {o}",
        "language": lambda s, o: f"{o} is spoken in {s}",
        "officialLanguage": lambda s, o: f"The official language of {s} is {o}",
        "currency": lambda s, o: f"The currency of {s} is {o}",
        "demonym": lambda s, o: f"The demonym for {s} is {o}",
        "foundingDate": lambda s, o: f"{s} was founded on {o}",
        "areaTotal": lambda s, o: f"{s} covers an area of {o}",
        "utcOffset": lambda s, o: f"{s} has a UTC offset of {o}",
        "timeZone": lambda s, o: f"{s} is in the {o} time zone",
        "season": lambda s, o: f"The season for {s} is {o}",
    }

    # Build a quick lookup for manager of clubs (subject = club, predicate = manager)
    club_manager = {}
    for t in triples:
        if t.predicate == "manager":
            club_manager[t.subject] = t.object

    # Group triples by subject to build a compact description per entity
    subject_map = {}
    for t in triples:
        subject_map.setdefault(t.subject, []).append((t.predicate, t.object))

    def join_parts(parts):
        """Join a list of strings with commas and an 'and' before the last element."""
        if not parts:
            return ""
        if len(parts) == 1:
            return parts[0]
        return ", ".join(parts[:-1]) + " and " + parts[-1]

    # First, build a clause for each subject as before
    raw_clauses = {}
    for subj, pred_objs in subject_map.items():
        phrase_parts = []
        multi_obj_preds = {"club", "currentclub"}
        multi_objs = {p: [] for p in multi_obj_preds}
        for pred, obj in pred_objs:
            if pred in multi_obj_preds:
                multi_objs[pred].append(obj)
            else:
                phrase = predicate_map.get(pred, lambda s, o: f"{s} {pred} {o}")(subj, obj)
                phrase_parts.append(phrase)
        for pred, objs in multi_objs.items():
            if objs:
                if len(objs) > 1:
                    objs_str = ", ".join(objs[:-1]) + f", and {objs[-1]}"
                else:
                    objs_str = objs[0]
                phrase = predicate_map.get(pred, lambda s, o: f"{s} {pred} {o}")(subj, objs_str)
                phrase_parts.append(phrase)
        raw_clauses[subj] = join_parts(phrase_parts)

    # Merge clauses where an object is also a subject, embedding it as a relative clause
    merged_clauses = {}
    used_subjects = set()

    # Helper to strip leading subject phrase from a clause
    import re
    def strip_leading(subj, clause):
        # Remove patterns like "Subject is ...", "Subject was ...", "Subject plays ..."
        pattern = rf'^{re.escape(subj)} (is|was|plays|competes|belongs|has|are|were) '
        return re.sub(pattern, '', clause, flags=re.I)

    # Pre‑compute stripped descriptions for each subject
    stripped_desc = {subj: strip_leading(subj, clause) for subj, clause in raw_clauses.items()}

    for subj, clause in raw_clauses.items():
        # Find any object that is also a subject
        for obj_subj in raw_clauses.keys():
            if obj_subj == subj:
                continue
            # Use word boundaries to avoid partial matches
            pattern = rf'\b{re.escape(obj_subj)}\b'
            if re.search(pattern, clause):
                # Embed the object's description as a relative clause
                rel_clause = f"{obj_subj}, which {stripped_desc[obj_subj]}"
                clause = re.sub(pattern, rel_clause, clause)
                used_subjects.add(obj_subj)
        merged_clauses[subj] = clause

    # Collect clauses that have not been embedded elsewhere
    final_parts = [clause for subj, clause in merged_clauses.items() if subj not in used_subjects]

    if not final_parts:
        return ""
    final_text = join_parts(final_parts) + "."
    return final_text

# EVOLVE-BLOCK-END