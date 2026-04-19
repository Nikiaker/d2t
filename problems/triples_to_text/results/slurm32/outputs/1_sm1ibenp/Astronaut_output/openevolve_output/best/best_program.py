from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    """
    Convert a list of triples about astronauts (or related entities) into a
    fluent English paragraph. Handles mission/crewMembers aggregation to
    produce compact sentences.
    """
    if not triples:
        return ""

    # ---------- Helper utilities ----------
    def fmt_date(d: str) -> str:
        try:
            from datetime import datetime
            dt = datetime.strptime(d, "%Y-%m-%d")
            # Use platform‑independent day format
            return dt.strftime("%B %-d, %Y") if hasattr(dt, "strftime") else dt.strftime("%B %d, %Y")
        except Exception:
            return d

    def join_names(names: list[str]) -> str:
        """Join a list of names with commas and 'and'."""
        if not names:
            return ""
        if len(names) == 1:
            return names[0]
        if len(names) == 2:
            return f"{names[0]} and {names[1]}"
        return f"{', '.join(names[:-1])}, and {names[-1]}"

    # ---------- Phrase builder ----------
    def phrase(subj: str, pred: str, obj: str) -> str:
        obj = obj.strip().strip('"')
        p = pred.lower().replace(" ", "")
        if p == "birthdate":
            return f"was born on {fmt_date(obj)}"
        if p == "birthplace":
            return f"was born in {obj}"
        if p == "deathdate":
            return f"died on {fmt_date(obj)}"
        if p == "deathplace":
            return f"died in {obj}"
        if p == "dateofretirement":
            # obj may be quoted; strip quotes
            return f"retired in {obj.strip().strip('\"')}"
        if p == "nationality":
            # Return adjective form if known, else country name
            adj_map = {
                "United States": "American",
                "United Kingdom": "British",
                "Russia": "Russian",
                "China": "Chinese",
                "Canada": "Canadian",
                "France": "French",
                "Germany": "German",
                "Japan": "Japanese",
                "Australia": "Australian",
                "India": "Indian",
                # add more as needed
            }
            return adj_map.get(obj, obj)
        if p == "occupation":
            return f"served as a {obj.lower()}"
        if p == "status":
            low = obj.lower()
            if low == "retired":
                return "is now retired"
            return f"is {low}"
        if p == "selectedbynasa":
            return f"was selected by NASA in {obj}"
        if p == "timeinspace":
            # Keep the raw minute value for simplicity and better matching with reference sentences
            return f"spent {obj.strip('\"')} minutes in space"
        if p == "birthname":
            # Use natural phrasing
            return f"was born as {obj}"
        if p == "title":
            return f"held the title of {obj}"
        if p == "award":
            return f"received the {obj}"
        if p == "awards":
            return f"received {obj} awards"
        if p == "almamater":
            # Remove surrounding quotes if present
            clean_obj = obj.strip().strip('"')
            return f"graduated from {clean_obj}"
        if p == "partstype":
            # Transform objects like "List of counties in Texas" into a natural phrase
            # Expected format: "List of <plural noun> in <Location>"
            low_obj = obj.lower()
            if low_obj.startswith("list of") and " in " in low_obj:
                # Extract the plural noun and location
                try:
                    _, rest = low_obj.split("list of", 1)
                    plural, location = rest.strip().split(" in ", 1)
                    plural = plural.strip()
                    location = location.strip()
                    # Simple singularization
                    if plural.endswith("ies"):
                        singular = plural[:-3] + "y"
                    elif plural.endswith("s"):
                        singular = plural[:-1]
                    else:
                        singular = plural
                    return f"is a {singular} in {location}"
                except Exception:
                    pass
            # Fallback to generic handling
            return f"is a {obj.lower()}"
        if p == "ispartof":
            return f"is part of {obj}"
        if p == "ribbonaward":
            return f"was awarded the {obj}"
        if p == "operator":
            return f"was operated by {obj}"
        if p == "leader":
            # Subject is organization/place, object is person
            return f"{obj} is the leader of {subj}"
        if p == "commander":
            return f"{obj} was the commander of {subj}"
        if p == "backuppilot":
            return f"{subj}'s backup pilot was {obj}"
        if p == "alternativename":
            return f"is also known as {obj}"
        if p == "servedaschiefoftheastronautofficein":
            return f"served as Chief of the Astronaut Office in {obj}"
        if p == "representative":
            return f"{obj} was the representative of {subj}"
        if p == "bird":
            return f"The {obj.lower()} is a bird found in {subj}"
        # generic fallback
        return f"is {obj}"

    # ---------- Aggregate mission/crew data ----------
    from collections import defaultdict

    # Store role information per mission
    mission_info: dict[str, dict[str, list[str]]] = defaultdict(
        lambda: {"commander": [], "backupPilot": [], "crew": []}
    )
    other_triples: list[Triple] = []

    for t in triples:
        p = t.predicate.lower().replace(" ", "")
        if p == "mission":
            # subject is astronaut, object is mission
            mission_info[t.object]["crew"].append(t.subject)
        elif p == "crewmembers":
            mission_info[t.subject]["crew"].append(t.object)
        elif p == "commander":
            # subject is mission, object is person
            mission_info[t.subject]["commander"].append(t.object)
        elif p == "backuppilot":
            mission_info[t.subject]["backupPilot"].append(t.object)
        else:
            other_triples.append(t)

    # Build quick lookup maps for operator and nationality
    operator_map: dict[str, str] = {}
    nationality_map: dict[str, str] = {}
    for t in other_triples:
        p = t.predicate.lower().replace(" ", "")
        if p == "operator":
            operator_map[t.subject] = t.object.strip().strip('"')
        elif p == "nationality":
            # store the adjective form (e.g., "American")
            nat_adj = phrase(t.subject, t.predicate, t.object).strip()
            nationality_map[t.subject] = nat_adj
    # Remove operator triples from further processing to avoid duplicate sentences
    other_triples = [t for t in other_triples if t.predicate.lower().replace(" ", "") != "operator"]
    # Keep track of missions that have been described in mission sentences
    used_missions = set()

    # Set of astronauts that already appear in mission sentences (crew, commander, backupPilot)
    crew_astronauts = {
        astr
        for roles in mission_info.values()
        for astr in roles["crew"] + roles["commander"] + roles["backupPilot"]
    }

    sentences: list[str] = []

    # Build a single sentence per mission combining all roles into compact clauses
    for mission, roles in mission_info.items():
        # Prepare operator prefix if available (e.g., "NASA's ")
        op_prefix = f"{operator_map[mission]}'s " if mission in operator_map else ""

        clause_parts: list[str] = []

        # Commander clause (kept separate)
        if roles["commander"]:
            cmd_display = [
                f"{nationality_map.get(name, '')} {name}".strip()
                for name in roles["commander"]
            ]
            clause_parts.append(f"{join_names(cmd_display)} was the commander of {op_prefix}{mission}")

        # Combine crew members and backup pilots into one natural sentence
        crew = roles["crew"]
        backup = roles["backupPilot"]
        if crew:
            crew_display = [
                f"{nationality_map.get(name, '')} {name}".strip()
                for name in crew
            ]
            primary = crew_display[0]
            others = crew_display[1:]

            # Start clause with primary crew member
            clause = f"{primary} was a crew member of {op_prefix}{mission}"

            companion_phrases: list[str] = []
            if others:
                companion_phrases.extend([f"fellow crew member {name}" for name in others])
            if backup:
                backup_display = [
                    f"{nationality_map.get(name, '')} {name}".strip()
                    for name in backup
                ]
                companion_phrases.extend([f"backup pilot {name}" for name in backup_display])

            if companion_phrases:
                clause += " with " + join_names(companion_phrases)

            clause_parts.append(clause)
        elif backup:
            # No crew members, only backup pilots
            backup_display = [
                f"{nationality_map.get(name, '')} {name}".strip()
                for name in backup
            ]
            clause_parts.append(f"{join_names(backup_display)} was the backup pilot of {op_prefix}{mission}")

        if clause_parts:
            sentence = ", ".join(clause_parts) + "."
            sentences.append(sentence)
            used_missions.add(mission)

    # After mission sentences, generate operator sentences for missions without crew info
    for mission, op in operator_map.items():
        if mission not in used_missions:
            sentences.append(f"{mission} is operated by {op}.")
    # Handle fossil predicate separately to produce correct sentence
    for t in list(other_triples):
        if t.predicate.lower().replace(" ", "") == "fossil":
            # subject is location, object is fossil
            sentences.append(f"The {t.object} is a fossil from {t.subject}.")
            other_triples.remove(t)

    # Process remaining triples (those not mission/crewMembers)
    # Group by subject, handling nationality specially to prepend as adjective
    # Remove nationality triples that have already been used in mission sentences
    # Build a map for leader relations to allow merging with nationality info
    leader_map: dict[str, str] = {}
    groups = defaultdict(list)
    for t in other_triples:
        if t.predicate.lower().replace(" ", "") == "nationality":
            # Skip if this subject already appears in a mission sentence (crew, commander, backupPilot)
            if t.subject in crew_astronauts:
                continue
        groups[t.subject].append(t)

    def _article(word: str) -> str:
        """Return appropriate indefinite article for a word ('a' or 'an')."""
        return "an" if word[0].lower() in "aeiou" else "a"

    for subj, items in groups.items():
        # Separate nationality descriptor
        nat_adj = None
        nat_obj = None
        other_desc = []
        death_date = None
        death_place = None
        skip_subject = False
        for t in items:
            pred_key = t.predicate.lower().replace(" ", "")
            if pred_key == "nationality":
                nat_adj = phrase(subj, t.predicate, t.object).strip()
                nat_obj = t.object.strip().strip('"')
                continue
            if pred_key == "leader":
                # leader predicate already forms a complete sentence (e.g., "Joe Biden is the leader of United States.")
                sentences.append(phrase(subj, t.predicate, t.object).strip() + ".")
                skip_subject = True
                continue
            if pred_key == "deathdate":
                death_date = fmt_date(t.object.strip().strip('"'))
                continue
            if pred_key == "deathplace":
                death_place = t.object.strip().strip('"')
                continue
            other_desc.append(phrase(subj, t.predicate, t.object))
        # Combine death information into a single clause
        if death_date and death_place:
            other_desc.append(f"died on {death_date} in {death_place}")
        elif death_date:
            other_desc.append(f"died on {death_date}")
        elif death_place:
            other_desc.append(f"died in {death_place}")
        if skip_subject:
            continue
        # Build subject string with optional nationality adjective
        if nat_adj and not other_desc:
            # Only nationality information – produce a sentence stating the nationality explicitly
            sentences.append(f"{subj}'s nationality is {nat_obj}.")
            continue

        subject_str = f"{nat_adj} {subj}" if nat_adj else subj

        if not other_desc:
            sentences.append(f"{subject_str}.")
        elif len(other_desc) == 1:
            sentences.append(f"{subject_str} {other_desc[0]}.")
        else:
            body = ", ".join(other_desc[:-1])
            sentences.append(f"{subject_str} {body}, and {other_desc[-1]}.")
    # Merge sentences that share the same subject to produce a more compact description
    # Simply preserve the order of generated sentences
    final_sentences = sentences
    return " ".join(final_sentences)

# EVOLVE-BLOCK-END