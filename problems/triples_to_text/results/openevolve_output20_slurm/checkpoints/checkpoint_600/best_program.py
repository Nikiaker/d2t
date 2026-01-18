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
            runway_length = next((t.object for t in triples if t.predicate == "runwayLength" and t.subject == triple.subject), None)
            if runway_length:
                sentence += f"The runway {triple.object} at {subject} has a length of {runway_length} meters. "
            else:
                sentence += f"{subject} has a runway named {triple.object}. "
        elif triple.predicate == "1stRunwayLengthFeet":
            runway_surface = next((t.object for t in triples if t.predicate == "1stRunwaySurfaceType" and t.subject == triple.subject), None)
            if runway_surface:
                sentence += f"The first runway is {triple.object} feet long and has a surface of {runway_surface}. "
            else:
                sentence += f"has a first runway length of {triple.object} feet. "
        elif triple.predicate == "1stRunwaySurfaceType":
            runway_length = next((t.object for t in triples if t.predicate == "1stRunwayLengthFeet" and t.subject == triple.subject), None)
            if runway_length:
                sentence += f"The first runway is made of {triple.object} and is {runway_length} feet long. "
            else:
                sentence += f"The first runway is made of {triple.object}. "
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