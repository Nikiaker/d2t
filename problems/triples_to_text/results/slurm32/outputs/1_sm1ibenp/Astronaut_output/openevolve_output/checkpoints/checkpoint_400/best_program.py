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
        if p == "ribbonaward":
            return f"was awarded the {obj}"
        if p == "operator":
            return f"was operated by {obj}"
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

    # Set of astronauts that already appear in mission sentences (crew, commander, backupPilot)
    crew_astronauts = {
        astr
        for roles in mission_info.values()
        for astr in roles["crew"] + roles["commander"] + roles["backupPilot"]
    }

    sentences: list[str] = []

    # Build a single sentence per mission combining all roles
    for mission, roles in mission_info.items():
        parts: list[str] = []

        # Prepare operator prefix if available (e.g., "NASA's ")
        op_prefix = ""
        if mission in operator_map:
            op_prefix = f"{operator_map[mission]}'s "

        if roles["commander"]:
            cmd_names = [f"{nationality_map.get(name, '')} {name}".strip() for name in roles["commander"]]
            cmd = join_names(cmd_names)
            parts.append(f"{cmd} was the commander of {op_prefix}{mission}")

        if roles["backupPilot"]:
            bp_names = [f"{nationality_map.get(name, '')} {name}".strip() for name in roles["backupPilot"]]
            bp = join_names(bp_names)
            parts.append(f"{bp} was the backup pilot of {op_prefix}{mission}")

        crew = roles["crew"]
        if crew:
            crew_names = [f"{nationality_map.get(name, '')} {name}".strip() for name in crew]
            crew_joined = join_names(crew_names)
            verb = "was" if len(crew) == 1 else "were"
            noun = "a crew member" if len(crew) == 1 else "crew members"
            parts.append(f"{crew_joined} {verb} {noun} of {op_prefix}{mission}")

        if parts:
            # Join parts with commas and an 'and' before the last part
            if len(parts) == 1:
                sentence = parts[0] + "."
            else:
                sentence = ", ".join(parts[:-1]) + f", and {parts[-1]}."
            sentences.append(sentence)

    # Handle fossil predicate separately to produce correct sentence
    for t in list(other_triples):
        if t.predicate.lower().replace(" ", "") == "fossil":
            # subject is location, object is fossil
            sentences.append(f"The {t.object} is a fossil from {t.subject}.")
            other_triples.remove(t)

    # Process remaining triples (those not mission/crewMembers)
    # Group by subject, handling nationality specially to prepend as adjective
    # Remove nationality triples that have already been used in mission sentences
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
        other_desc = []
        for t in items:
            pred_key = t.predicate.lower().replace(" ", "")
            if pred_key == "nationality":
                nat_adj = phrase(subj, t.predicate, t.object).strip()
            else:
                other_desc.append(phrase(subj, t.predicate, t.object))
        # Build subject string with optional nationality adjective
        if nat_adj and not other_desc:
            # Only nationality information – produce a sentence that states the nationality explicitly
            sentences.append(f"{subj}'s nationality is {nat_adj}.")
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