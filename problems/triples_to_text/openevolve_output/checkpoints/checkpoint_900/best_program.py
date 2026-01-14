from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    """
    Generates a natural language sentence from a list of triples.
    """
    sentence = ""
    subject = ""
    for triple in triples:
        if not subject:
            subject = triple.subject
            sentence += f"{subject} "

        if triple.predicate == "cityServed":
            sentence += f"serves the city of {triple.object}. "
        elif triple.predicate == "elevationAboveTheSeaLevel":
            sentence += f"is at an elevation of {triple.object} meters above sea level. "
        elif triple.predicate == "location":
            sentence += f"is located in {triple.object}. "
        elif triple.predicate == "country":
            country = triple.object
            capital = None
            for t in triples:
                if t.subject == country and t.predicate == "capital":
                    capital = t.object
                    break
            if capital:
                sentence += f"is in {country}, whose capital is {capital}. "
            else:
                sentence += f"is in {triple.object}. "
        elif triple.predicate == "capital":
            sentence += f"is the capital of {next(t.subject for t in triples if t.predicate == 'country' and t.object == triple.object)}. "
        elif triple.predicate == "iataLocationIdentifier":
            sentence += f"has an IATA identifier of {triple.object}. "
        elif triple.predicate == "icaoLocationIdentifier":
            sentence += f"has an ICAO identifier of {triple.object}. "
        elif triple.predicate == "runwayLength":
            runway_name = next((t.object for t in triples if t.predicate == "runwayName" and t.subject == triple.subject), None)
            if runway_name:
                sentence += f"The runway length of runway {runway_name} at {subject} is {triple.object} meters. "
            else:
                sentence += f"The runway length at {subject} is {triple.object} meters. "
        elif triple.predicate == "runwayName":
            runway_name = triple.object
            runway_details = []
            for t in triples:
                if t.subject == triple.subject and t.predicate in ("runwayLength", "runwaySurfaceType", "1stRunwayLengthFeet", "1stRunwaySurfaceType"):
                    runway_details.append(f"{t.predicate.replace('_', ' ')} is {t.object}")

            if runway_details:
                sentence += f"{subject}'s runway {runway_name} has " + ", ".join(runway_details) + "."
            else:
                sentence += f"The runway name of {subject} is {runway_name}. "
        elif triple.predicate == "1stRunwayLengthFeet":
            # Combine with runway surface type if available
            runway_surface = next((t.object for t in triples if t.predicate == "1stRunwaySurfaceType" and t.subject == triple.subject), None)
            if runway_surface:
                sentence += f"The first runway at {subject} is {triple.object} feet long and has a {runway_surface} surface. "
            else:
                sentence += f"The first runway at {subject} is {triple.object} feet long. "
        elif triple.predicate == "1stRunwaySurfaceType":
            runway_length = next((t.object for t in triples if t.predicate == "1stRunwayLengthFeet" and t.subject == triple.subject), None)
            if runway_length:
                sentence += f"The first runway at {subject} has a {triple.object} surface and is {runway_length} feet long. "
            else:
                sentence += f"The first runway at {subject} has a {triple.object} surface. "
        elif triple.predicate == "3rdRunwayLengthFeet":
            sentence += f"has a third runway length of {triple.object} feet. "
        elif triple.predicate == "3rdRunwaySurfaceType":
            sentence += f"The third runway is made of {triple.object}. "
        elif triple.predicate == "1stRunwayNumber":
            sentence += f"has a runway number of {triple.object}. "
        else:
            if triple.predicate == "isPartOf":
                sentence += f"is part of {triple.object}. "
            elif triple.predicate == "language":
                sentence += f"speaks {triple.object}. "
            elif triple.predicate == "operatingOrganisation":
                sentence += f"is operated by {triple.object}. "
            else:
                sentence += f"and has a {triple.predicate} of {triple.object}. "

    return sentence.strip()

# EVOLVE-BLOCK-END