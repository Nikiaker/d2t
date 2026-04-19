from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    if not triples:
        return ""
    # Group triples by subject to allow multiple entities
    from collections import defaultdict
    subject_map = defaultdict(list)
    for t in triples:
        subject_map[t.subject].append(t)

    # Helper to format numbers with commas and drop trailing .0 (unchanged)
    def _fmt_num(val: str) -> str:
        # Format numbers with commas and drop unnecessary trailing .0
        try:
            num = float(val)
            if num.is_integer():
                return f"{int(num):,}"
            else:
                # Preserve decimal part while adding commas
                formatted = f"{num:,}"
                # Ensure that trailing zeros are not truncated incorrectly
                return formatted
        except Exception:
            return val.strip('"')

    # Convert numeric runway order to ordinal word (first, second, …)
    def _ordinal_word(n: int) -> str:
        mapping = {
            1: "first",
            2: "second",
            3: "third",
            4: "fourth",
            5: "fifth",
            6: "sixth",
            7: "seventh",
            8: "eighth",
            9: "ninth",
            10: "tenth",
        }
        return mapping.get(n, f"{n}th")

    # Simple predicate → phrase templates (used for generic parts) (unchanged)
    templates = {
        # Airport‑specific predicates
        "cityServed": "serves the city of {obj}",
        "elevationAboveTheSeaLevel": "is {obj} metres above sea level",
        "elevationAboveTheSeaLevelInMetres": "is {obj} metres above sea level",
        "elevationAboveTheSeaLevelInFeet": "is {obj} feet above sea level",
        "runwayName": "runway name is {obj}",
        "location": "is located in {obj}",
        "operatingOrganisation": "is operated by {obj}",
        "country": "is in {obj}",
        "isPartOf": "is part of {obj}",
        "locationIdentifier": "location identifier is {obj}",
        "1stRunwayLengthFeet": "the first runway is {obj} feet long",
        "1stRunwayLengthMetre": "the first runway is {obj} metres long",
        "1stRunwaySurfaceType": "the first runway surface is {obj}",
        "1stRunwayNumber": "the first runway number is {obj}",
        "runwaySurfaceType": "runway surface is {obj}",
        # Added/adjusted predicates (unchanged)
        "jurisdiction": "has jurisdiction in {obj}",
        # Generic entity predicates (unchanged)
        "leader": "leader is {obj}",
        "capital": "capital is {obj}",
        "language": "language is {obj}",
        "officialLanguage": "official language is {obj}",
        "currency": "currency is {obj}",
        "owner": "is owned by {obj}",
        "foundingYear": "was founded in {obj}",
        "founder": "was founded by {obj}",
        "postalCode": "postal code is {obj}",
        "areaCode": "area code is {obj}",
        "largestCity": "largest city is {obj}",
        "countySeat": "county seat is {obj}",
        "mayor": "mayor is {obj}",
        "leaderParty": "leader party is {obj}",
        "leaderTitle": "leader title is {obj}",
        "chief": "chief is {obj}",
        "hubAirport": "hub airport is {obj}",
        "regionServed": "serves region {obj}",
        "nativeName": "native name is {obj}",
        # Biological classification predicates (unchanged)
        "class": "class is {obj}",
        "division": "division is {obj}",
        "order": "order is {obj}",
        "species": "species is {obj}",
        "demonym": "demonym is {obj}",
    }

    sentences = []
    for subject, tlist in subject_map.items():
        # collect phrases and special aggregated predicates
        parts = []
        agg = defaultdict(list)   # for predicates that may have multiple values (e.g., leader)

        for t in tlist:
            # identifiers and runway length – keep as separate sentences
            if t.predicate == "iataLocationIdentifier":
                obj = t.object.strip('"')
                sentences.append(f"{obj} is the IATA location identifier for {subject}.")
                continue
            if t.predicate == "icaoLocationIdentifier":
                obj = t.object.strip('"')
                sentences.append(f"{obj} is the ICAO code for {subject}.")
                continue
            if t.predicate == "runwayLength":
                obj = _fmt_num(t.object)
                sentences.append(f"The runway length of {subject} is {obj}.")
                continue

            # language – phrase needs subject after object
            if t.predicate == "language":
                obj = t.object.strip('"')
                sentences.append(f"{obj} is spoken in {subject}.")
                continue

            # leader – may appear multiple times, aggregate later
            if t.predicate == "leader":
                agg["leader"].append(t.object.strip('"'))
                continue

            # Handle ordinal runway predicates (length, surface, number)
            import re
            m_len_feet = re.fullmatch(r'(\d+)(st|nd|rd|th)RunwayLengthFeet', t.predicate)
            m_len_metres = re.fullmatch(r'(\d+)(st|nd|rd|th)RunwayLengthMetre', t.predicate)
            m_surface = re.fullmatch(r'(\d+)(st|nd|rd|th)RunwaySurfaceType', t.predicate)
            m_number = re.fullmatch(r'(\d+)(st|nd|rd|th)RunwayNumber', t.predicate)
            if m_len_feet:
                num = int(m_len_feet.group(1))
                obj = _fmt_num(t.object)
                ord_word = _ordinal_word(num)
                parts.append(f"the {ord_word} runway at {subject} is {obj} feet long")
                continue
            if m_len_metres:
                num = int(m_len_metres.group(1))
                obj = _fmt_num(t.object)
                ord_word = _ordinal_word(num)
                parts.append(f"the {ord_word} runway at {subject} is {obj} metres long")
                continue
            if m_surface:
                num = int(m_surface.group(1))
                obj = t.object.strip('"')
                ord_word = _ordinal_word(num)
                parts.append(f"the {ord_word} runway at {subject} has an {obj.lower()} surface")
                continue
            if m_number:
                num = int(m_number.group(1))
                obj = t.object.strip('"')
                ord_word = _ordinal_word(num)
                parts.append(f"the {ord_word} runway at {subject} is numbered {obj}")
                continue

            # Special handling for biological classification predicates to produce natural phrasing
            if t.predicate in {"order", "class", "division", "species"}:
                obj = t.object.strip('"')
                parts.append(f"is of the {t.predicate} {obj}")
                continue

            tmpl = templates.get(t.predicate)
            if tmpl:
                obj = t.object.strip('"')
                if t.predicate in {"elevationAboveTheSeaLevel", "elevationAboveTheSeaLevelInMetres", "elevationAboveTheSeaLevelInFeet"}:
                    obj = _fmt_num(obj)
                parts.append(tmpl.format(obj=obj))
            else:
                pred = t.predicate.replace('_', ' ')
                obj = t.object.strip('"')
                parts.append(f"{pred} {obj}")

        # handle aggregated leaders
        if agg.get("leader"):
            leaders = agg["leader"]
            if len(leaders) == 1:
                parts.append(f"leader is {leaders[0]}")
            else:
                leaders_str = ", ".join(leaders[:-1]) + f" and {leaders[-1]}"
                parts.append(f"leaders are {leaders_str}")

        # combine all parts for the subject into one sentence (unchanged)
        if parts:
            if len(parts) == 1:
                sentence = f"{subject} {parts[0]}."
            else:
                sentence = f"{subject} " + ", ".join(parts[:-1]) + ", and " + parts[-1] + "."
            sentences.append(sentence)

    return " ".join(sentences)

# EVOLVE-BLOCK-END