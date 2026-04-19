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

    # Helper to clean object strings (remove surrounding quotes)
    def _clean(val: str) -> str:
        return val.strip().strip('"').strip("'")

    # Mapping from predicate to a formatting lambda (subject, object) -> phrase
    predicate_map = {
        "birthDate": lambda s, o: f"{s} was born on {_clean(o)}",
        "birthYear": lambda s, o: f"{s} was born in {_clean(o)}",
        "birthPlace": lambda s, o: f"{s} was born in {_clean(o)}",
        "height": lambda s, o: f"{s} is {_clean(o)} meters tall",
        "weight": lambda s, o: f"{s} weighs {_clean(o)}",
        "position": lambda s, o: f"{s} plays as a {_clean(o)}",
        "club": lambda s, o: f"{s} plays for {_clean(o)}",
        "currentclub": lambda s, o: f"{s} currently plays for {_clean(o)}",
        "formerTeam": lambda s, o: f"{s} formerly played for {_clean(o)}",
        "league": lambda s, o: f"{s} competes in the {_clean(o)}",
        # Revised phrasing for clearer ownership / roles
        "manager": lambda s, o: f"{_clean(o)} is the manager of {s}",
        "coach": lambda s, o: f"{_clean(o)} is the coach of {s}",
        "draftTeam": lambda s, o: f"{s}'s draft team is {_clean(o)}",
        "draftYear": lambda s, o: f"{s} was drafted in {_clean(o)}",
        "draftRound": lambda s, o: f"{s} was in draft round {_clean(o)}",
        "draftPick": lambda s, o: f"{s} was the {_clean(o)}th pick",
        "playerNumber": lambda s, o: f"{s} wears number {_clean(o)}",
        "currentteam": lambda s, o: f"{s} currently plays for {_clean(o)}",
        "debutTeam": lambda s, o: f"{s} debuted with {_clean(o)}",
        # Additional predicates beyond the athlete domain
        "leader": lambda s, o: f"{_clean(o)} is the leader of {s}",
        "deathPlace": lambda s, o: f"{s} died in {_clean(o)}",
        "isPartOf": lambda s, o: f"{s} is part of {_clean(o)}",
        "country": lambda s, o: f"{s} is in {_clean(o)}",
        "city": lambda s, o: f"{s} is based in {_clean(o)}",
        "owner": lambda s, o: f"The owner of {s} is {_clean(o)}",
        "chairman": lambda s, o: f"{_clean(o)} is the chairman of {s}",
        "generalManager": lambda s, o: f"{_clean(o)} is the general manager of {s}",
        "stadium": lambda s, o: f"{s}'s stadium is {_clean(o)}",
        "ground": lambda s, o: f"{s}'s ground is located in {_clean(o)}",
        "anthem": lambda s, o: f"The anthem of {s} is {_clean(o)}",
        "ethnicGroup": lambda s, o: f"{s} has an ethnic group of {_clean(o)}",
        "language": lambda s, o: f"{_clean(o)} is spoken in {s}",
        "officialLanguage": lambda s, o: f"The official language of {s} is {_clean(o)}",
        "currency": lambda s, o: f"The currency of {s} is {_clean(o)}",
        "demonym": lambda s, o: f"{_clean(o)} is the demonym of {s}",
        "foundingDate": lambda s, o: f"{s} was founded on {_clean(o)}",
        "areaTotal": lambda s, o: f"{s} covers an area of {_clean(o)}",
        "utcOffset": lambda s, o: f"{s} has a UTC offset of {_clean(o)}",
        "timeZone": lambda s, o: f"{s} is in the {_clean(o)} time zone",
        "season": lambda s, o: f"The season for {s} is {_clean(o)}",
        "youthclub": lambda s, o: f"{s}'s youth club is {_clean(o)}",
    }

    # Helper to build a concise relative clause for an entity that appears as an object.
    # Returns a string starting with "which ..." (or empty if no useful info).
    def _relative_clause(entity: str) -> str:
        if entity not in subject_map:
            return ""
        parts = []
        for p, o in subject_map[entity]:
            if o == entity:
                continue
            # Special phrasing for common relational predicates when used as a relative clause
            if p == "leader":
                parts.append(f"is led by {_clean(o)}")
            elif p == "isPartOf":
                parts.append(f"is part of {_clean(o)}")
            elif p == "manager":
                parts.append(f"is managed by {_clean(o)}")
            elif p == "coach":
                parts.append(f"is coached by {_clean(o)}")
            elif p == "owner":
                parts.append(f"is owned by {_clean(o)}")
            elif p == "city":
                parts.append(f"based in {_clean(o)}")
            elif p == "country":
                parts.append(f"in {_clean(o)}")
            elif p == "ground":
                parts.append(f"whose ground is {_clean(o)}")
            else:
                # fallback to generic mapping
                parts.append(predicate_map.get(p, lambda s, o: f"{s} {p} {o}")(entity, o))
        if not parts:
            return ""
        # join with commas and the final 'and' for readability
        if len(parts) == 1:
            clause = parts[0]
        else:
            clause = ", ".join(parts[:-1]) + " and " + parts[-1]
        return f"which {clause}"

    # Group triples by subject to build a compact description per entity
    subject_map = {}
    for t in triples:
        subject_map.setdefault(t.subject, []).append((t.predicate, t.object))

    # Determine which subjects appear as objects elsewhere (non‑root entities)
    referenced_subjects = set()
    for t in triples:
        if t.object in subject_map:
            referenced_subjects.add(t.object)

    def join_parts(parts):
        """Join a list of strings with commas and an 'and' before the last element."""
        if not parts:
            return ""
        if len(parts) == 1:
            return parts[0]
        return ", ".join(parts[:-1]) + " and " + parts[-1]

    sentences = []
    for subj, pred_objs in subject_map.items():
        # Skip non‑root subjects; they will be described as relative clauses
        if subj in referenced_subjects:
            continue
        phrase_parts = []
        # Process predicates
        for pred, obj in pred_objs:
            phrase = predicate_map.get(pred, lambda s, o: f"{s} {pred} {o}")(subj, obj)
            # If the object has its own triples, attach them as a relative clause
            if obj in subject_map:
                rel_clause = _relative_clause(obj)
                if rel_clause:
                    phrase += f", {rel_clause}"
            phrase_parts.append(phrase)

        # No separate handling for club; it is already expressed via the "club" predicate mapping.

        # Combine all parts for this subject
        subject_clause = join_parts(phrase_parts)
        sentences.append(subject_clause)

    # Combine all subject clauses into a single fluent sentence
    if not sentences:
        return ""
    final_text = ". ".join(sentences) + "."
    return final_text

# EVOLVE-BLOCK-END