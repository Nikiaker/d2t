from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    """
    Convert a list of triples about airports (or related entities) into a single
    fluent, complex sentence. Unknown predicates fall back to a generic phrasing.
    """
    if not triples:
        return ""

    def _clean(val: str) -> str:
        """Remove surrounding quotes if present."""
        return val.strip('"').strip("'")

    # Helper to build a clause for a single triple
    def _clause(s: str, p: str, o: str) -> str:
        # Primary airport‑specific predicates
        if p == "cityServed":
            return f"{s} serves the city of {o}"
        if p == "location":
            return f"{s} is located in {o}"
        if p == "country":
            return f"{s} is in {o}"
        if p == "isPartOf":
            return f"{s} is part of {o}"
        if p == "elevationAboveTheSeaLevel":
            return f"{s} lies at an elevation of {o} metres above sea level"
        if p == "elevationAboveTheSeaLevelInFeet":
            return f"{s} lies at an elevation of {o} feet above sea level"
        if p == "elevationAboveTheSeaLevelInMetres":
            return f"{s} lies at an elevation of {o} metres above sea level"
        if p == "operatingOrganisation":
            return f"{s} is operated by {o}"
        if p == "runwaySurfaceType":
            return f"{s} has a runway surface of {o}"
        # Runway length variants
        if p.endswith("RunwayLengthFeet"):
            idx = p.split("Runway")[0]
            return f"{s}'s {idx.lower()} runway is {o} feet long"
        if p.endswith("RunwayLengthMetre"):
            idx = p.split("Runway")[0]
            return f"{s}'s {idx.lower()} runway is {o} metres long"
        # Runway identifiers
        if p == "runwayName":
            return f"{s}'s runway is named {o}"
        if p == "runwayLength":
            return f"{s}'s runway length is {o}"
        # Runway surface types
        if p.endswith("RunwaySurfaceType"):
            idx = p.split("Runway")[0]
            return f"{s}'s {idx.lower()} runway surface is {o}"
        # Runway numbers
        if p.endswith("RunwayNumber"):
            idx = p.split("Runway")[0]
            return f"{s}'s {idx.lower()} runway number is {o}"
        # Aviation codes
        if p == "iataLocationIdentifier":
            return f"{s} has IATA code {o}"
        if p == "icaoLocationIdentifier":
            return f"{s} has ICAO code {o}"
        if p == "locationIdentifier":
            return f"{s} has location identifier {o}"
        # Ownership and administration
        if p == "owner":
            return f"{s} is owned by {o}"
        if p == "largestCity":
            return f"The largest city of {s} is {o}"
        if p == "capital":
            return f"The capital of {s} is {o}"
        if p == "language" or p == "officialLanguage":
            return f"The official language of {s} is {o}"
        if p == "leader":
            return f"The leader of {s} is {o}"
        if p == "leaderTitle":
            return f"The leader title of {s} is {o}"
        if p == "leaderParty":
            return f"The leader of {s} belongs to the {o} party"
        # Native name
        if p == "nativeName":
            return f"{s} is known as {o}"
        # Administrative info
        if p == "administrativeArrondissement":
            return f"{s} is in the administrative arrondissement of {o}"
        if p == "mayor":
            return f"The mayor of {s} is {o}"
        if p == "currency":
            return f"{s} uses the {o}"
        if p == "demonym":
            return f"People from {s} are called {o}"
        if p == "regionServed":
            return f"{s} serves the {o} region"
        if p == "hubAirport":
            return f"{o} is a hub airport for {s}"
        if p == "headquarter":
            return f"{s} has its headquarters at {o}"
        if p == "foundedBy":
            return f"{s} was founded by {o}"
        if p == "foundingYear":
            return f"{s} was founded in {o}"
        if p == "postalCode":
            return f"{s} has postal code {o}"
        if p == "areaCode":
            return f"{s} has area code {o}"
        if p == "ceremonialCounty":
            return f"{s} is in the ceremonial county of {o}"
        if p == "countySeat":
            return f"The county seat of {s} is {o}"
        if p == "chief":
            return f"The chief of {s} is {o}"
        if p == "jurisdiction":
            return f"{s} has jurisdiction over {o}"
        if p == "city":
            return f"{s} is located in {o}"
        # Fallback for any other predicate
        return f"{s} has {p} {o}"

    # Build clauses
    clauses: list[str] = [_clause(t.subject, t.predicate, _clean(t.object)) for t in triples]

    # Combine clauses into a single complex sentence
    if len(clauses) == 1:
        sentence = clauses[0] + "."
    elif len(clauses) == 2:
        # Try to create a relative clause structure for better flow
        sentence = clauses[0] + ", which " + clauses[1].lower() + "."
    else:
        # Use relative clauses for better sentence flow
        parts = []
        for i, clause in enumerate(clauses):
            if i == 0:
                parts.append(clause)
            elif i == 1:
                parts.append(", which " + clause.lower() + ".")
            else:
                parts.append(", where " + clause.lower() + ".")

        # Join properly
        sentence = parts[0] + parts[1]
        for part in parts[2:]:
            sentence = sentence[:-1] + ", and " + part[1:]
        sentence = sentence[:-1] + "."

    # Capitalise first character
    return sentence[0].upper() + sentence[1:]

# EVOLVE-BLOCK-END