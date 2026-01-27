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
    clauses = []
    for i, triple in enumerate(triples):
        subject = triple.subject
        predicate = triple.predicate
        object_ = triple.object

        if predicate == "city":
            clauses.append(f"{subject} is a city in {object_}")
        elif predicate == "country":
            clauses.append(f"{subject} is located in {object_}")
        elif predicate == "capital":
            clauses.append(f"{object_} is the capital of {subject}")
        elif predicate == "latinName":
            clauses.append(f"The Latin name for {subject} is \"{object_}\"")
        elif predicate == "nickname":
            clauses.append(f"{subject} is also known as {object_}")
        elif predicate == "rector":
            clauses.append(f"The rector of {subject} is {object_}")
        elif predicate == "academicStaffSize":
            clauses.append(f"{subject} has an academic staff of {object_}")
        elif predicate == "established":
            clauses.append(f"{subject} was established in {object_}")
        elif predicate == "state":
            clauses.append(f"{subject} is in the state of {object_}")
        elif predicate == "hasToItsNortheast":
            clauses.append(f"{subject} has {object_} to its northeast")
        elif predicate == "dean":
            clauses.append(f"The dean of {subject} is {object_}")
        elif predicate == "location":
            clauses.append(f"{subject} is located in {object_}")
        elif predicate == "numberOfStudents":
            clauses.append(f"{subject} has {object_} students")
        elif predicate == "affiliation":
            clauses.append(f"{subject} is affiliated with {object_}")
        elif predicate == "director":
            clauses.append(f"The director of {subject} is {object_}")
        elif predicate == "motto":
            clauses.append(f"The motto of {subject} is \"{object_}\"")
        elif predicate == "numberOfPostgraduateStudents":
            clauses.append(f"{subject} has {object_} postgraduate students")
        elif predicate == "numberOfUndergraduateStudents":
            clauses.append(f"{subject} has {object_} undergraduate students")
        elif predicate == "officialSchoolColour":
            clauses.append(f"The official school colour of {subject} is {object_}")
        elif predicate == "outlookRanking":
            clauses.append(f"{subject} has an outlook ranking of {object_}")
        elif predicate == "sportsOffered":
            clauses.append(f"{subject} offers {object_}")
        elif predicate == "wasGivenTheTechnicalCampusStatusBy":
            clauses.append(f"{subject} was given the technical campus status by {object_}")
        elif predicate == "founder":
            clauses.append(f"{subject} was founded by {object_}")
        elif predicate == "leader":
            clauses.append(f"The leader of {subject} is {object_}")
        elif predicate == "leaderTitle":
            clauses.append(f"The leader title of {subject} is {object_}")
        elif predicate == "religion":
            clauses.append(f"The religion of {subject} is {object_}")
        elif predicate == "headquarter":
            clauses.append(f"The headquarter of {subject} is {object_}")
        elif predicate == "largestCity":
            clauses.append(f"The largest city in {subject} is {object_}")
        elif predicate == "river":
            clauses.append(f"{subject} has the {object_} river")
        elif predicate == "hasToItsWest":
            clauses.append(f"{subject} has {object_} to its west")
        elif predicate == "anthem":
            clauses.append(f"The anthem of {subject} is {object_}")
        elif predicate == "ethnicGroup":
            clauses.append(f"An ethnic group in {subject} is {object_}")
        elif predicate == "legislature":
            clauses.append(f"The legislature of {subject} is {object_}")
        elif predicate == "sportGoverningBody":
            clauses.append(f"The sport governing body of {subject} is {object_}")
        elif predicate == "isPartOf":
            clauses.append(f"{subject} is part of {object_}")
        elif predicate == "neighboringMunicipality":
            clauses.append(f"{subject} has {object_} as a neighboring municipality")
        elif predicate == "patronSaint":
            clauses.append(f"The patron saint of {subject} is {object_}")
        elif predicate == "hasToItsNorthwest":
            clauses.append(f"{subject} has {object_} to its northwest")
        elif predicate == "campus":
            clauses.append(f"The campus of {subject} is {object_}")
        elif predicate == "president":
            clauses.append(f"The president of {subject} is {object_}")
        elif predicate == "staff":
            clauses.append(f"{subject} has {object_} staff")
        elif predicate == "numberOfDoctoralStudents":
            clauses.append(f"{subject} has {object_} doctoral students")
        elif predicate == "elevationAboveTheSeaLevel":
            clauses.append(f"{subject} has an elevation above the sea level of {object_}")
        elif predicate == "postalCode":
            clauses.append(f"The postal code of {subject} is {object_}")
        elif predicate == "longName":
            clauses.append(f"The long name of {subject} is {object_}")
        else:
            clauses.append(f"The {predicate} of {subject} is {object_}")

    if len(clauses) > 1:
        sentence = ", ".join(clauses) + "."
    else:
        sentence = clauses[0] + "." if clauses else ""
    return sentence.strip()

# EVOLVE-BLOCK-END