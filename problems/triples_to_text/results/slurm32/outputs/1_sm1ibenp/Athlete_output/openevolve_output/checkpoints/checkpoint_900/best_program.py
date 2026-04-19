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

    # Helper to add a definite article when appropriate
    def _add_article(val: str) -> str:
        """Prepend 'the' to a noun phrase unless it already starts with an article."""
        stripped = val.strip()
        lower = stripped.lower()
        if lower.startswith(("the ", "a ", "an ")):
            return stripped
        return f"the {stripped}"

    # Helper to clean subject strings (remove parenthetical descriptors)
    def _clean_subject(val: str) -> str:
        """
        Clean the subject string.
        If the subject contains a parenthetical descriptor (e.g., "Abner (footballer)"),
        format it as "The <descriptor> <name>".
        Otherwise, just strip whitespace and surrounding parentheses.
        """
        val = val.strip()
        if '(' in val and ')' in val:
            # Split into name and descriptor
            name_part = val.split('(')[0].strip()
            descriptor = val[val.find('(') + 1:val.find(')')].strip()
            # Capitalize descriptor if needed
            descriptor = descriptor.lower()
            # Use "The" prefix for common role descriptors
            return f"The {descriptor} {name_part}"
        # Fallback: remove any stray parentheses and trim
        return val.replace('(', '').replace(')', '').strip()

    # Mapping from predicate to a formatting lambda (subject, object) -> phrase
    # Helper to format ISO dates into a more natural “2 September 1995” style.
    def _format_date(date_str: str) -> str:
        try:
            parts = date_str.split("-")
            if len(parts) == 3:
                year, month, day = parts
                months = ["January", "February", "March", "April", "May", "June",
                          "July", "August", "September", "October", "November", "December"]
                month_name = months[int(month) - 1]
                # Remove leading zeros
                day_int = int(day)
                return f"{day_int} {month_name} {year}"
        except Exception:
            pass
        return date_str

    predicate_map = {
        "birthDate": lambda s, o: f"{_clean_subject(s)} was born on {_format_date(_clean(o))}",
        "birthYear": lambda s, o: f"{_clean_subject(s)} was born in {_clean(o)}",
        "birthPlace": lambda s, o: f"{_clean_subject(s)} was born in {_clean(o)}",
        "height": lambda s, o: f"{_clean_subject(s)} is {_clean(o)} meters tall",
        "weight": lambda s, o: f"{_clean_subject(s)} weighs {_clean(o)}",
        "position": lambda s, o: f"{_clean_subject(s)} plays in the {_clean(o).split('(')[0].strip()}",
        "club": lambda s, o: (
            f"{_clean_subject(s)} "
            f"{'has represented' if 'national' in _clean(o).lower() else 'plays for'} "
            f"{_clean(o)}"
        ),
        "currentclub": lambda s, o: f"{_clean_subject(s)} currently plays for {_clean(o)}",
        "formerTeam": lambda s, o: f"{_clean_subject(s)} later played for {_clean(o)}",
        "league": lambda s, o: f"{_clean_subject(s)} competes in the {_clean(o)}",
        # Revised phrasing for clearer ownership / roles
        "manager": lambda s, o: f"{_clean(o)} is the manager of {_clean_subject(s)}",
        "coach": lambda s, o: f"{_clean(o)} is the coach of {_clean_subject(s)}",
        "draftTeam": lambda s, o: f"{_clean_subject(s)}'s draft team is {_add_article(_clean(o))}",
        "draftYear": lambda s, o: f"{_clean_subject(s)} was drafted in {_clean(o)}",
        "draftRound": lambda s, o: f"{_clean_subject(s)} was in draft round {_clean(o)}",
        "draftPick": lambda s, o: f"{_clean_subject(s)} was the {_clean(o)}th pick",
        "playerNumber": lambda s, o: f"{_clean_subject(s)} wears number {_clean(o)}",
        "currentteam": lambda s, o: f"{_clean_subject(s)} currently plays for {_clean(o)}",
        "debutTeam": lambda s, o: f"{_clean_subject(s)}'s debut team was {_add_article(_clean(o))}",
        "activeYearsStartYear": lambda s, o: f"{_clean_subject(s)} started playing in {_clean(o)}",
        # Additional predicates beyond the athlete domain
        "leader": lambda s, o: f"{_clean(o)} is the leader of {_clean_subject(s)}",
        "deathPlace": lambda s, o: f"{_clean_subject(s)} died in {_clean(o)}",
        "isPartOf": lambda s, o: f"{_clean_subject(s)} is part of {_clean(o)}",
        "country": lambda s, o: f"{_clean_subject(s)} is in {_clean(o)}",
        "city": lambda s, o: f"{_clean_subject(s)} is based in {_clean(o)}",
        "owner": lambda s, o: f"The owner of {_clean_subject(s)} is {_clean(o)}",
        "chairman": lambda s, o: f"{_clean(o)} is the chairman of {_clean_subject(s)}",
        "generalManager": lambda s, o: f"{_clean(o)} is the general manager of {_clean_subject(s)}",
        "stadium": lambda s, o: f"{_clean_subject(s)}'s stadium is {_clean(o)}",
        "ground": lambda s, o: f"{_clean_subject(s)} ground is {_clean(o)}",
        "anthem": lambda s, o: f"The anthem of {_clean_subject(s)} is {_clean(o)}",
        "ethnicGroup": lambda s, o: f"{_clean(o)} are an ethnic group in {_clean_subject(s)}",
        "language": lambda s, o: f"{_clean(o)} is spoken in {_clean_subject(s)}",
        "officialLanguage": lambda s, o: f"The official language of {_clean_subject(s)} is {_clean(o)}",
        "currency": lambda s, o: f"The currency of {_clean_subject(s)} is {_clean(o)}",
        "demonym": lambda s, o: f"{_clean(o)} is the demonym of {_clean_subject(s)}",
        "foundingDate": lambda s, o: f"{_clean_subject(s)} was founded on {_clean(o)}",
        "areaTotal": lambda s, o: f"{_clean_subject(s)} covers an area of {_clean(o)}",
        "utcOffset": lambda s, o: f"{_clean_subject(s)} has a UTC offset of {_clean(o)}",
        "timeZone": lambda s, o: f"{_clean_subject(s)} is in the {_clean(o)} time zone",
        "season": lambda s, o: f"The season for {_clean_subject(s)} is {_clean(o)}",
        "youthclub": lambda s, o: f"In his youth, {_clean_subject(s)} played for {_clean(o)}",
        # New predicate for championship dominance
        "mostChampions": lambda s, o: f"{_clean(o)} has won the {_clean_subject(s)} the most times",
        # Added missing predicates for education and university affiliations
        "universityTeam": lambda s, o: f"The {_clean_subject(s)} are the university team for {_clean(o)}",
        "stadium": lambda s, o: f"{_clean_subject(s)}'s stadium is {_clean(o)}",
        "ground": lambda s, o: f"{_clean_subject(s)}'s ground is {_clean(o)}",
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
        # Determine if clause should start with "which" or be a pure "whose" style clause
        starts_with_whose = any(p.startswith("whose") for p in parts)
        # join with commas and the final 'and' for readability
        if len(parts) == 1:
            clause_body = parts[0]
        else:
            clause_body = ", ".join(parts[:-1]) + " and " + parts[-1]
        if starts_with_whose:
            # If a part already provides a "whose ..." phrase, omit leading "which"
            return clause_body
        else:
            return f"which {clause_body}"

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
        # Group objects by predicate to allow aggregation
        pred_to_objs = {}
        for pred, obj in pred_objs:
            pred_to_objs.setdefault(pred, []).append(obj)

        for pred, objs in pred_to_objs.items():
            if len(objs) == 1:
                obj = objs[0]
                phrase = predicate_map.get(pred, lambda s, o: f"{s} {pred} {o}")(subj, obj)
                # Attach relative clause if the object has its own triples
                if obj in subject_map:
                    rel_clause = _relative_clause(obj)
                    if rel_clause:
                        phrase += f", {rel_clause}"
                phrase_parts.append(phrase)
            else:
                # Aggregate multiple objects for the same predicate, adding relative clauses per object
                if pred in {"club", "formerTeam", "currentteam", "currentclub", "debutTeam"}:
                    verb = "plays for"
                elif pred == "playerNumber":
                    verb = "wears number"
                else:
                    generic = predicate_map.get(pred, lambda s, o: f"{s} {pred} {o}")(subj, "")
                    verb = generic.replace(subj, "").strip()
                obj_phrases = []
                for o in objs:
                    base = _clean(o)
                    if o in subject_map:
                        rel = _relative_clause(o)
                        if rel:
                            base = f"{base}, {rel}"
                    obj_phrases.append(base)
                if len(obj_phrases) == 1:
                    obj_list = obj_phrases[0]
                elif len(obj_phrases) == 2:
                    obj_list = " and ".join(obj_phrases)
                else:
                    obj_list = ", ".join(obj_phrases[:-1]) + " and " + obj_phrases[-1]
                phrase = f"{subj} {verb} {obj_list}"
                phrase_parts.append(phrase)

        # Combine all parts for this subject
        subject_clause = join_parts(phrase_parts)
        sentences.append(subject_clause)

    # Combine all subject clauses into a single fluent sentence
    if not sentences:
        return ""
    final_text = ". ".join(sentences) + "."
    return final_text

# EVOLVE-BLOCK-END