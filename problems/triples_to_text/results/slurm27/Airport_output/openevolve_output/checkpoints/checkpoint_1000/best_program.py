from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    subjects = {}
    for triple in triples:
        if triple.subject not in subjects:
            subjects[triple.subject] = []
        subjects[triple.subject].append((triple.predicate, triple.object))

    sentence = ""
    airport_info = {}
    location_info = {}
    country_info = {}

    for triple in triples:
        subject = triple.subject
        predicate = triple.predicate
        obj = triple.object

        if predicate == "cityServed":
            airport_info[subject] = obj
        elif predicate == "location":
            location_info[subject] = obj
        elif predicate == "country":
            country_info[subject] = obj

    for subject, triples in subjects.items():
        if subject in airport_info:
            sentence += f"{subject} serves the city of {airport_info[subject]}"

            if subject in location_info:
                sentence += f", which is located in {location_info[subject]}"

            if subject in country_info:
                sentence += f", in {country_info[subject]}"

            for i, (predicate, obj) in enumerate(triples):
                if predicate == "elevationAboveTheSeaLevel":
                    sentence += f", with an elevation of {obj} metres above sea level"
                elif predicate == "runwayLength":
                    sentence += f", and has a runway length of {obj} metres"
                elif predicate == "operatingOrganisation":
                    sentence += f", operated by {obj}"
                elif predicate == "iataLocationIdentifier":
                    sentence += f", with the IATA code {obj}"
                elif predicate == "icaoLocationIdentifier":
                    sentence += f", and the ICAO code {obj}"

            sentence += ". "

    return sentence.strip()

# EVOLVE-BLOCK-END