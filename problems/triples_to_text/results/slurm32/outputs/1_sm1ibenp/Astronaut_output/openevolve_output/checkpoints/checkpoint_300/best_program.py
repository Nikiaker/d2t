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
    fluent English sentence.  The function groups triples by their subject and
    builds a clause for each predicate, then joins the clauses into a single
    (or a few) readable sentences.
    """
    if not triples:
        return ""

    # Helper to turn a predicate/object pair into a descriptor (without repeating the subject)
    def phrase(subj: str, pred: str, obj: str) -> str:
        """Return a natural‑language descriptor for a single predicate."""
        obj = obj.strip().strip('"')
        p = pred.lower().replace(" ", "")
        def fmt_date(d: str) -> str:
            try:
                from datetime import datetime
                dt = datetime.strptime(d, "%Y-%m-%d")
                return dt.strftime("%B %-d, %Y")
            except Exception:
                return d

        if p == "birthdate":
            return f"was born on {fmt_date(obj)}"
        if p == "birthplace":
            return f"was born in {obj}"
        if p == "deathdate":
            return f"died on {fmt_date(obj)}"
        if p == "deathplace":
            return f"died in {obj}"
        if p == "dateofretirement":
            return f"retired on {fmt_date(obj)}"
        if p == "nationality":
            low_obj = obj.lower()
            if low_obj in ("united states", "usa", "united states of america"):
                return "is an American"
            if low_obj.startswith("the "):
                return f"is from {obj}"
            else:
                return f"is from the {obj}"
        if p == "occupation":
            return f"was a {obj.lower()}"
        if p == "status":
            low = obj.lower()
            if low == "retired":
                return "is retired"
            return f"is {low}"
        if p == "selectedbynasa":
            return f"was selected by NASA in {obj}"
        if p == "mission":
            return f"was a crew member of {obj}"
        if p == "timeinspace":
            try:
                mins = float(obj)
                hrs = int(mins // 60)
                rem = int(mins % 60)
                if hrs:
                    return f"spent {hrs} hour{'s' if hrs>1 else ''}" + (f" and {rem} minute{'s' if rem!=1 else ''}" if rem else "") + " in space"
                else:
                    return f"spent {rem} minute{'s' if rem!=1 else ''} in space"
            except Exception:
                return f"spent {obj} minutes in space"
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
        if p == "crewmembers":
            return f"{obj} was a crew member of {subj}"
        if p == "alternativename":
            return f"is also known as {obj}"
        if p == "servedaschiefoftheastronautofficein":
            return f"served as Chief of the Astronaut Office in {obj}"
        if p == "representative":
            return f"{obj} was the representative of {subj}"
        if p == "bird":
            return f"The {obj.lower()} is a bird found in {subj}"
        # Generic fallback
        return f"is {obj}"

    # Group triples by subject
    from collections import defaultdict
    groups = defaultdict(list)
    for t in triples:
        groups[t.subject].append(t)

    sentences = []
    for subj, items in groups.items():
        descriptors = [phrase(subj, t.predicate, t.object) for t in items]
        if not descriptors:
            continue
        # Adjust each descriptor: if it already starts with the subject, keep it;
        # otherwise prepend the subject.
        # Clean descriptors by removing any leading subject repetition
        clean_desc = []
        for d in descriptors:
            d = d.strip()
            if d.lower().startswith(subj.lower()):
                d = d[len(subj):].strip()
            clean_desc.append(d.rstrip('.'))
        if len(clean_desc) == 1:
            sent = f"{subj} {clean_desc[0]}."
        else:
            if len(clean_desc) == 2:
                body = f"{clean_desc[0]} and {clean_desc[1]}"
            else:
                body = ", ".join(clean_desc[:-1]) + f", and {clean_desc[-1]}"
            sent = f"{subj} {body}."
        sentences.append(sent)

    # Combine sentences for different subjects
    return " ".join(sentences)

# EVOLVE-BLOCK-END