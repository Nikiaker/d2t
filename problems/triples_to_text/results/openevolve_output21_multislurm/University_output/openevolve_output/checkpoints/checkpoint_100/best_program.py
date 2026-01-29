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
    for i, triple in enumerate(triples):
        subject = triple.subject
        predicate = triple.predicate
        object_ = triple.object

        if predicate == "city":
            sentence += f"{subject} is a city in {object_}. "
        elif predicate == "country":
            sentence += f"{subject} is located in {object_}. "
        elif predicate == "latinName":
            sentence += f"The Latin name for {subject} is \"{object_}\". "
        elif predicate == "nickname":
            sentence += f"{subject} is also known as {object_}. "
        elif predicate == "rector":
            sentence += f"The rector of {subject} is {object_}. "
        elif predicate == "academicStaffSize":
            sentence += f"{subject} has an academic staff of {object_}. "
        elif predicate == "established":
            sentence += f"{subject} was established in {object_}. "
        elif predicate == "state":
            sentence += f"{subject} is in the state of {object_}. "
        elif predicate == "governmentType":
            sentence += f"{subject} has a {object_} government. "
        elif predicate == "hasToItsNortheast":
            sentence += f"{subject} has {object_} to its northeast. "
        elif predicate == "dean":
            sentence += f"The dean of {subject} is {object_}. "
        elif predicate == "location":
            sentence += f"{subject} is located in {object_}. "
        elif predicate == "numberOfStudents":
            sentence += f"{subject} has {object_} students. "
        elif predicate == "affiliation":
            sentence += f"{subject} is affiliated with {object_}. "
        elif predicate == "director":
            sentence += f"The director of {subject} is {object_}. "
        elif predicate == "motto":
            sentence += f"The motto of {subject} is \"{object_}\". "
        elif predicate == "numberOfPostgraduateStudents":
            sentence += f"{subject} has {object_} postgraduate students. "
        elif predicate == "numberOfUndergraduateStudents":
            sentence += f"{subject} has {object_} undergraduate students. "
        elif predicate == "officialSchoolColour":
            sentence += f"The official school colour of {subject} is {object_}. "
        elif predicate == "outlookRanking":
            sentence += f"{subject} has an outlook ranking of {object_}. "
        elif predicate == "sportsOffered":
            sentence += f"{subject} offers {object_}. "
        elif predicate == "wasGivenTheTechnicalCampusStatusBy":
            sentence += f"{subject} was given the technical campus status by {object_}. "
        elif predicate == "founder":
            sentence += f"{subject} was founded by {object_}. "
        elif predicate == "leader":
            sentence += f"The leader of {subject} is {object_}. "
        elif predicate == "leaderTitle":
            sentence += f"The leader title of {subject} is {object_}. "
        elif predicate == "religion":
            sentence += f"The religion of {subject} is {object_}. "
        elif predicate == "headquarter":
            sentence += f"The headquarter of {subject} is {object_}. "
        elif predicate == "largestCity":
            sentence += f"The largest city in {subject} is {object_}. "
        elif predicate == "river":
            sentence += f"{subject} has the {object_} river. "
        elif predicate == "hasToItsWest":
            sentence += f"{subject} has {object_} to its west. "
        elif predicate == "anthem":
            sentence += f"The anthem of {subject} is {object_}. "
        elif predicate == "ethnicGroup":
            sentence += f"An ethnic group in {subject} is {object_}. "
        elif predicate == "legislature":
            sentence += f"The legislature of {subject} is {object_}. "
        elif predicate == "sportGoverningBody":
            sentence += f"The sport governing body of {subject} is {object_}. "
        elif predicate == "isPartOf":
            sentence += f"{subject} is part of {object_}. "
        elif predicate == "neighboringMunicipality":
            sentence += f"{subject} has {object_} as a neighboring municipality. "
        elif predicate == "capital":
            sentence += f"{object_} is the capital of {subject}. "
        elif predicate == "patronSaint":
            sentence += f"The patron saint of {subject} is {object_}. "
        elif predicate == "hasToItsNorthwest":
            sentence += f"{subject} has {object_} to its northwest. "
        elif predicate == "campus":
            sentence += f"The campus of {subject} is {object_}. "
        elif predicate == "president":
            sentence += f"The president of {subject} is {object_}. "
        elif predicate == "staff":
            sentence += f"{subject} has {object_} staff. "
        elif predicate == "numberOfDoctoralStudents":
            sentence += f"{subject} has {object_} doctoral students. "
        elif predicate == "elevationAboveTheSeaLevel":
            sentence += f"{subject} has an elevation above the sea level of {object_}. "
        elif predicate == "postalCode":
            sentence += f"The postal code of {subject} is {object_}. "
        elif predicate == "longName":
            sentence += f"The long name of {subject} is {object_}. "
        else:
            sentence += f"The {predicate} of {subject} is {object_}. "

    return sentence.strip()

# EVOLVE-BLOCK-END