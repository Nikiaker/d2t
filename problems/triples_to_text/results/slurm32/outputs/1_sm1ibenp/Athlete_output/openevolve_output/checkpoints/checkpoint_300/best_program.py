from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    """Convert a list of triples about an athlete into a fluent, combined sentence."""
    if not triples:
        return ""

    # organise triples by subject for easy lookup
    subj_map: dict[str, list[tuple[str, str]]] = {}
    for t in triples:
        subj_map.setdefault(t.subject, []).append((t.predicate, t.object))

    # helper to render a single (subject, predicate, object) with possible
    # augmentation using information from other triples
    def render(s: str, p: str, o: str) -> str:
        # basic mappings with refined phrasing
        if p == "birthDate":
            # convert ISO date to a readable format if possible
            try:
                from datetime import datetime
                d = datetime.strptime(o, "%Y-%m-%d")
                o_fmt = d.strftime("%-d %B %Y")
            except Exception:
                o_fmt = o
            base = f"{s} was born on {o_fmt}"
        elif p == "birthYear":
            base = f"{s} was born in {o}"
        elif p == "birthPlace":
            base = f"{s} was born in {o}"
        elif p == "height":
            base = f"{s} is {o} metres tall"
        elif p == "weight":
            base = f"{s} weighs {o}"
        elif p == "draftTeam":
            base = f"{s}'s draft team is {o}"
        elif p == "activeYearsStartYear":
            base = f"{s} started playing in {o}"
        elif p == "position":
            # strip parentheses and make lower‑case if appropriate
            clean_o = o.split('(')[0].strip()
            base = f"{s} plays as a {clean_o}"
        elif p in ("club", "currentclub"):
            base = f"{s} plays for {o}"
        elif p == "formerTeam":
            base = f"{s} formerly played for {o}"
        elif p == "league":
            base = f"{s} competes in the {o}"
        elif p == "manager":
            # reverse phrasing for natural style
            base = f"{o} is the manager of {s}"
        elif p == "coach":
            base = f"{o} is the coach of {s}"
        elif p == "ethnicGroup":
            base = f"{s} has an ethnic group called {o}"
        elif p == "anthem":
            base = f"The anthem of {s} is {o}"
        elif p == "currency":
            base = f"The currency of {s} is {o}"
        elif p == "demonym":
            base = f"The demonym for {s} is {o}"
        elif p == "officialLanguage":
            base = f"The official language of {s} is {o}"
        elif p == "draftYear":
            base = f"{s} was drafted in {o}"
        elif p == "draftRound":
            base = f"{s} was selected in round {o}"
        elif p == "draftPick":
            base = f"{s} was the {o}th pick"
        elif p == "playerNumber":
            base = f"{s} wears number {o}"
        elif p == "currentteam":
            base = f"{s} currently plays for {o}"
        elif p == "debutTeam":
            base = f"{s} made his debut with {o}"
        elif p == "leader":
            base = f"{o} is the leader of {s}"
        elif p == "deathPlace":
            base = f"{s} died in {o}"
        elif p == "isPartOf":
            base = f"{s} is part of {o}"
        elif p == "country":
            base = f"{s} is in {o}"
        elif p == "ground":
            base = f"{s}'s ground is {o}"
        elif p == "city":
            base = f"{s} is based in {o}"
        elif p == "owner":
            base = f"{s} is owned by {o}"
        elif p == "chairman":
            base = f"The chairman of {s} is {o}"
        elif p == "youthclub":
            base = f"{s} played for the youth team of {o}"
        else:
            base = f"{s} {p} {o}"

        # augment with secondary information (e.g., club's manager, ground's city)
        if p in ("club", "currentclub") and o in subj_map:
            for sp, so in subj_map[o]:
                if sp == "manager":
                    base += f", which is managed by {so}"
                    break
        if p == "ground" and o in subj_map:
            for sp, so in subj_map[o]:
                if sp == "city":
                    base += f", located in {so}"
                    break
        return base

    # Remove redundant birthYear when birthDate is present for the same subject
    cleaned_phrases = []
    for s, pred_objs in subj_map.items():
        # filter out birthYear if birthDate also exists
        preds = [p for p, _ in pred_objs]
        if "birthDate" in preds:
            pred_objs = [(p, o) for p, o in pred_objs if p != "birthYear"]
        cleaned_phrases.append((s, pred_objs))

    # build phrases per subject, merging multiple predicates of the same subject
    phrases = []
    for s, pred_objs in cleaned_phrases:
        sub_phrases = [render(s, p, o) for p, o in pred_objs]
        if len(sub_phrases) == 1:
            phrases.append(sub_phrases[0])
        else:
            combined = ", ".join(sub_phrases[:-1]) + f", and {sub_phrases[-1]}"
            phrases.append(combined)

    # build phrases per subject, merging multiple predicates of the same subject,
    # and aggregating multiple values for the same predicate (e.g., several clubs)
    def _format_date(d: str) -> str:
        try:
            from datetime import datetime
            dt = datetime.strptime(d, "%Y-%m-%d")
            # platform‑independent day without leading zero
            return dt.strftime("%-d %B %Y")
        except Exception:
            return d

    phrases = []
    for s, pred_objs in subj_map.items():
        # aggregate objects per predicate
        agg: dict[str, list[str]] = {}
        for p, o in pred_objs:
            agg.setdefault(p, []).append(o)

        sub_phrases: list[str] = []

        # combine birthPlace and birthDate into a single fluent clause
        if "birthDate" in agg and "birthPlace" in agg:
            date_str = _format_date(agg["birthDate"][0])
            place = agg["birthPlace"][0]
            sub_phrases.append(f"{s} was born in {place} on {date_str}")
            agg.pop("birthDate")
            agg.pop("birthPlace")
        elif "birthDate" in agg:
            sub_phrases.append(f"{s} was born on {_format_date(agg['birthDate'][0])}")
            agg.pop("birthDate")
        elif "birthPlace" in agg:
            sub_phrases.append(f"{s} was born in {agg['birthPlace'][0]}")
            agg.pop("birthPlace")

        # combine debutTeam and formerTeam into a natural progression
        if "debutTeam" in agg and "formerTeam" in agg:
            debut = agg["debutTeam"][0]
            former = agg["formerTeam"][0]
            sub_phrases.append(f"{s} debuted with {debut} and later played for {former}")
            agg.pop("debutTeam")
            agg.pop("formerTeam")

        for p, objs in agg.items():
            # special handling for language predicate
            if p == "language":
                sub_phrases.append(f"The languages of {s} are {', '.join(objs)}")
                continue

            # aggregation for clubs / current clubs
            if p in ("club", "currentclub"):
                if len(objs) == 1:
                    base = f"{s} plays for {objs[0]}"
                else:
                    clubs = ", ".join(objs[:-1]) + f" and {objs[-1]}"
                    base = f"{s} plays for {clubs}"
                sub_phrases.append(base)
                continue

            # default handling (including possible multiple objects)
            if len(objs) == 1:
                sub_phrases.append(render(s, p, objs[0]))
            else:
                rendered = [render(s, p, o) for o in objs]
                sub_phrases.append(", ".join(rendered))

        # combine all clauses for the current subject
        if not sub_phrases:
            continue
        if len(sub_phrases) == 1:
            phrases.append(sub_phrases[0])
        else:
            phrases.append(", ".join(sub_phrases[:-1]) + f", and {sub_phrases[-1]}")

    # finally join all subject‑level phrases into one sentence
    if len(phrases) == 1:
        return phrases[0] + "."
    else:
        return "; ".join(phrases) + "."

# EVOLVE-BLOCK-END