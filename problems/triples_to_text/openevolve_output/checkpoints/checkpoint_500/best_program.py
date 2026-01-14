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
        elif triple.predicate == "administrativeArrondissement":
            sentence += f"is located in the {triple.object}. "
        elif triple.predicate == "mayor":
            sentence += f"is led by mayor {triple.object}. "
        elif triple.predicate == "officialLanguage":
            sentence += f"has {triple.object} as an official language. "
        elif triple.predicate == "leaderParty":
            sentence += f"is governed by the {triple.object}. "
        elif triple.predicate == "iataLocationIdentifier":
            sentence += f"has an IATA identifier of {triple.object}. "
        elif triple.predicate == "icaoLocationIdentifier":
            sentence += f"has an ICAO identifier of {triple.object}. "
        elif triple.predicate == "runwayLength":
            sentence += f"has a runway length of {triple.object} meters. "
        elif triple.predicate == "runwayName":
            sentence += f"is named {triple.object}. "
        elif triple.predicate == "1stRunwayLengthFeet":
            sentence += f"has a first runway length of {triple.object} feet. "
        elif triple.predicate == "1stRunwaySurfaceType":
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