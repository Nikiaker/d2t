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
            runway_length = next((t.object for t in triples if t.predicate == "runwayLength" and t.subject == triple.subject), None)
            runway_surface = next((t.object for t in triples if t.predicate == "runwaySurfaceType" and t.subject == triple.subject), None)
            first_runway_length_feet = next((t.object for t in triples if t.predicate == "1stRunwayLengthFeet" and t.subject == triple.subject), None)
            first_runway_surface_type = next((t.object for t in triples if t.predicate == "1stRunwaySurfaceType" and t.subject == triple.subject), None)

            details = []
            if runway_length:
                details.append(f"is {runway_length} meters long")
            if runway_surface:
                details.append(f"has a {runway_surface} surface")
            if first_runway_length_feet:
                details.append(f"is {first_runway_length_feet} feet long")
            if first_runway_surface_type:
                details.append(f"has a {first_runway_surface_type} surface")

            if details:
                sentence += f"{subject}'s runway {runway_name} has " + ", ".join(details) + "."
            else:
                sentence += f"The runway name of {subject} is {runway_name}. "
        elif triple.predicate == "1stRunwayLengthFeet":
            # Combine with runway surface type if available
            runway_surface = next((t.object for t in triples if t.predicate == "1stRunwaySurfaceType" and t.subject == triple.subject), None)
            if runway_surface:
                sentence += f"The first runway at {subject} is {triple.object} feet long with a {runway_surface} surface. "
            else:
                sentence += f"The first runway at {subject} is {triple.object} feet long. "
        elif triple.predicate == "1stRunwaySurfaceType":
            runway_length = next((t.object for t in triples if t.predicate == "1stRunwayLengthFeet" and t.subject == triple.subject), None)
            if runway_length:
                sentence += f"The first runway at {subject} has a {triple.object} surface and is {runway_length} feet long. "
            else:
                sentence += f"The first runway at {subject} has a {triple.object} surface. "
        elif triple.predicate == "3rdRunwayLengthFeet":
            third_runway_surface = next((t.object for t in triples if t.predicate == "3rdRunwaySurfaceType" and t.subject == triple.subject), None)
            if third_runway_surface:
                sentence += f"The third runway at {subject} is {triple.object} feet long and has a {third_runway_surface} surface. "
            else:
                sentence += f"The third runway at {subject} is {triple.object} feet long. "
        elif triple.predicate == "3rdRunwaySurfaceType":
            # Avoid redundant sentence if 3rdRunwayLengthFeet already handled
            pass
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