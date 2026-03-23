from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    """Generate a readable sentence from a list of triples."""
    if not triples:
        return ""

    parts: list[str] = []
    for t in triples:
        s, p, o = t.subject, t.predicate, t.object

        # Specific phrasing for common airport predicates
        if p == "cityServed":
            parts.append(f"{s} serves the city of {o}")
        elif p == "elevationAboveTheSeaLevel":
            # Don't assume units - let the data speak for itself
            if not any(unit in str(o).lower() for unit in ['metre', 'meter', 'm', 'foot', 'feet', 'ft']):
                parts.append(f"{s} is at an elevation of {o} above sea level")
            else:
                parts.append(f"{s} is at an elevation of {o} above sea level")
        elif p == "elevationAboveTheSeaLevelInFeet":
            parts.append(f"{s} is at an elevation of {o} feet above sea level")
        elif p == "elevationAboveTheSeaLevelInMetres":
            parts.append(f"{s} is at an elevation of {o} metres above sea level")
        elif p == "location":
            parts.append(f"{s} is located in {o}")
        elif p == "operatingOrganisation":
            parts.append(f"{s} is operated by {o}")
        elif p == "runwayLength":
            # Don't assume units - let the data speak for itself
            if not any(unit in str(o).lower() for unit in ['metre', 'meter', 'm', 'foot', 'feet', 'ft']):
                parts.append(f"{s} has a runway length of {o}")
            else:
                parts.append(f"{s} has a runway length of {o}")
        elif p == "runwayName":
            parts.append(f"{s}'s runway is named {o}")
        elif p == "country":
            parts.append(f"{s} is in {o}")
        elif p == "isPartOf":
            parts.append(f"{s} is part of {o}")
        elif p == "icaoLocationIdentifier":
            parts.append(f"{s} has ICAO code {o}")
        elif p == "locationIdentifier":
            parts.append(f"{s} has location identifier {o}")
        elif p == "iataLocationIdentifier":
            parts.append(f"{s} has IATA code {o}")
        elif p == "nativeName":
            parts.append(f"{s} is also known as {o}")
        elif p == "leader":
            # Check if there are multiple leaders for the same subject
            leader_count = sum(1 for t in triples if t.predicate == "leader" and t.subject == s)
            if leader_count > 1:
                # Collect all leaders for this subject
                leaders = [t.object for t in triples if t.predicate == "leader" and t.subject == s]
                parts.append(f"{s} is led by {', '.join(leaders[:-1]) + ' and ' if len(leaders) > 1 else ''}{leaders[-1]}")
            else:
                parts.append(f"{s} is led by {o}")
        elif p == "leaderTitle":
            parts.append(f"{s} has the leader title of {o}")
        elif p == "leaderParty":
            parts.append(f"{s}'s leader party is {o}")
        elif p == "owner":
            parts.append(f"{s} is owned by {o}")
        elif p == "capital":
            parts.append(f"{s}'s capital is {o}")
        elif p == "language":
            parts.append(f"{s}'s language is {o}")
        elif p == "officialLanguage":
            parts.append(f"{s}'s official language is {o}")
        elif p == "mayor":
            parts.append(f"{s}'s mayor is {o}")
        elif p == "largestCity":
            parts.append(f"{s}'s largest city is {o}")
        elif p == "countySeat":
            parts.append(f"{s}'s county seat is {o}")
        elif p == "jurisdiction":
            parts.append(f"{s} has jurisdiction over {o}")
        elif p == "demonym":
            parts.append(f"{s}'s demonym is {o}")
        elif p == "currency":
            parts.append(f"{s}'s currency is {o}")
        elif p == "city":
            parts.append(f"{s} is located in {o}")
        elif p == "headquarter":
            # Check if there are multiple headquarters for the same subject
            hq_count = sum(1 for t in triples if t.predicate == "headquarter" and t.subject == s)
            if hq_count > 1:
                # Collect all headquarters for this subject
                headquarters = [t.object for t in triples if t.predicate == "headquarter" and t.subject == s]
                parts.append(f"{s} has headquarters in {', '.join(headquarters[:-1]) + ' and ' if len(headquarters) > 1 else ''}{headquarters[-1]}")
            else:
                parts.append(f"{s}'s headquarter is {o}")
        elif p == "regionServed":
            parts.append(f"{s} serves the region of {o}")
        elif p == "hubAirport":
            parts.append(f"{s} has hub airport at {o}")
        elif p == "foundedBy":
            parts.append(f"{s} was founded by {o}")
        elif p == "foundingYear":
            parts.append(f"{s} was founded in {o}")
        elif p == "postalCode":
            parts.append(f"{s}'s postal code is {o}")
        elif p == "areaCode":
            parts.append(f"{s}'s area code is {o}")
        elif p == "ceremonialCounty":
            parts.append(f"{s} is in ceremonial county {o}")
        elif p == "administrativeArrondissement":
            parts.append(f"{s} is in administrative arrondissement {o}")
        elif p == "chief":
            parts.append(f"{s}'s chief is {o}")
        elif p == "class":
            parts.append(f"{s} belongs to class {o}")
        elif p == "division":
            parts.append(f"{s} belongs to division {o}")
        elif p == "order":
            parts.append(f"{s} belongs to order {o}")
        elif p == "aircraftHelicopter":
            parts.append(f"{s} uses helicopter {o}")
        elif p == "transportAircraft":
            parts.append(f"{s} uses transport aircraft {o}")
        elif p == "aircraftFighter":
            parts.append(f"{s} uses fighter aircraft {o}")
        elif p == "attackAircraft":
            parts.append(f"{s} uses attack aircraft {o}")
        elif p == "battle":
            parts.append(f"{s} was involved in the battle of {o}")
        elif p.endswith("RunwayLengthFeet"):
            rn = p.split("Runway")[0].lower()
            if rn == "1st":
                parts.append(f"{s}'s first runway has a length of {o} feet")
            elif rn == "2nd":
                parts.append(f"{s}'s second runway has a length of {o} feet")
            elif rn == "3rd":
                parts.append(f"{s}'s third runway has a length of {o} feet")
            elif rn == "4th":
                parts.append(f"{s}'s fourth runway has a length of {o} feet")
            elif rn == "5th":
                parts.append(f"{s}'s fifth runway has a length of {o} feet")
            else:
                parts.append(f"{s} has a {rn} runway length of {o} feet")
        elif p.endswith("RunwayLengthMetre"):
            rn = p.split("Runway")[0].lower()
            if rn == "1st":
                parts.append(f"{s}'s first runway has a length of {o} metres")
            elif rn == "2nd":
                parts.append(f"{s}'s second runway has a length of {o} metres")
            elif rn == "3rd":
                parts.append(f"{s}'s third runway has a length of {o} metres")
            elif rn == "4th":
                parts.append(f"{s}'s fourth runway has a length of {o} metres")
            elif rn == "5th":
                parts.append(f"{s}'s fifth runway has a length of {o} metres")
            else:
                parts.append(f"{s} has a {rn} runway length of {o} metres")
        elif p.endswith("RunwaySurfaceType"):
            rn = p.split("Runway")[0].lower()
            if rn == "1st":
                parts.append(f"{s}'s first runway has a surface of {o}")
            elif rn == "2nd":
                parts.append(f"{s}'s second runway has a surface of {o}")
            elif rn == "3rd":
                parts.append(f"{s}'s third runway has a surface of {o}")
            elif rn == "4th":
                parts.append(f"{s}'s fourth runway has a surface of {o}")
            elif rn == "5th":
                parts.append(f"{s}'s fifth runway has a surface of {o}")
            else:
                parts.append(f"The {rn} runway of {s} has a surface of {o}")
        elif p.endswith("RunwayNumber"):
            rn = p.split("Runway")[0].lower()
            if rn == "1st":
                parts.append(f"{s}'s first runway is numbered {o}")
            elif rn == "2nd":
                parts.append(f"{s}'s second runway is numbered {o}")
            elif rn == "3rd":
                parts.append(f"{s}'s third runway is numbered {o}")
            elif rn == "4th":
                parts.append(f"{s}'s fourth runway is numbered {o}")
            elif rn == "5th":
                parts.append(f"{s}'s fifth runway is numbered {o}")
            else:
                parts.append(f"The {rn} runway of {s} is numbered {o}")
        else:
            # Generic fallback - handle REDACTED_TOKEN properly
            clean_p = p.replace("<REDACTED_TOKEN>", "").strip()
            if clean_p and clean_p != p:
                # If predicate was redacted, use generic but grammatically correct phrasing
                parts.append(f"{s}'s {clean_p if clean_p else 'property'} is {o}")
            else:
                parts.append(f"{s} has {o} {p}")

    # Build a complex sentence by chaining related information with proper connectors
    # Deduplicate parts that are essentially the same
    unique_parts = []
    seen_content = set()
    for part in parts:
        if part not in seen_content:
            unique_parts.append(part)
            seen_content.add(part)

    parts = unique_parts

    if len(parts) == 0:
        return ""
    elif len(parts) == 1:
        sentence = parts[0] + "."
    elif len(parts) == 2:
        sentence = parts[0] + ", and " + parts[1] + "."
    else:
        # Create a more complex sentence structure with proper connectors
        # Use "which" to create relative clauses for better flow and reduce redundancy
        sentence = parts[0]
        for i, part in enumerate(parts[1:], 1):
            if i == len(parts) - 1:
                # Last part - use "and" before it
                sentence += ", and " + part
            else:
                # Middle parts - use semicolons with "which" for relative clauses
                sentence += "; " + part
        sentence += "."

    # Ensure the first character is capitalised
    if sentence:
        sentence = sentence[0].upper() + sentence[1:]
    return sentence

# EVOLVE-BLOCK-END