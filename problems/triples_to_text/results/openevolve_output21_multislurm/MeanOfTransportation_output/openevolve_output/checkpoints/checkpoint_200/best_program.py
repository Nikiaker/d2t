from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    sentences = []
    for triple in triples:
        if triple.predicate == "alternativeName":
            sentences.append(f"{triple.subject} is also known as \"{triple.object}\".")
        elif triple.predicate == "bodyStyle":
            sentences.append(f"{triple.subject} has a {triple.object} body style.")
        elif triple.predicate == "engine":
            sentences.append(f"{triple.subject} is equipped with a {triple.object}.")
        elif triple.predicate == "manufacturer":
            sentences.append(f"{triple.subject} is manufactured by {triple.object}.")
        elif triple.predicate == "relatedMeanOfTransportation":
            sentences.append(f"{triple.subject} is related to {triple.object}.")
        elif triple.predicate == "transmission":
            sentences.append(f"{triple.subject} has a {triple.object} transmission.")
        elif triple.predicate == "wheelbase":
            sentences.append(f"{triple.subject} has a wheelbase of {triple.object}.")
        elif triple.predicate == "builder":
            sentences.append(f"{triple.subject} was built by {triple.object}.")
        elif triple.predicate == "completionDate":
            sentences.append(f"{triple.subject} was completed on {triple.object}.")
        elif triple.predicate == "length":
            sentences.append(f"{triple.subject} has a length of {triple.object}.")
        elif triple.predicate == "powerType":
            sentences.append(f"{triple.subject} is powered by {triple.object}.")
        elif triple.predicate == "shipClass":
            sentences.append(f"{triple.subject} is a {triple.object}.")
        elif triple.predicate == "shipDisplacement":
            sentences.append(f"{triple.subject} has a displacement of {triple.object}.")
        elif triple.predicate == "shipLaunch":
            sentences.append(f"{triple.subject} was launched on {triple.object}.")
        elif triple.predicate == "shipOrdered":
            sentences.append(f"{triple.subject} was ordered on {triple.object}.")
        elif triple.predicate == "shipPower":
            sentences.append(f"{triple.subject} is powered by {triple.object}.")
        elif triple.predicate == "topSpeed":
            sentences.append(f"{triple.subject} has a top speed of {triple.object}.")
        elif triple.predicate == "location":
            sentences.append(f"{triple.object} is located in {triple.subject}.")
        elif triple.predicate == "christeningDate":
            sentences.append(f"{triple.subject} was christened on {triple.object}.")
        elif triple.predicate == "maidenVoyage":
            sentences.append(f"{triple.subject}'s maiden voyage was on {triple.object}.")
        elif triple.predicate == "owner":
            sentences.append(f"{triple.subject} is owned by {triple.object}.")
        elif triple.predicate == "shipBeam":
            sentences.append(f"{triple.subject} has a beam of {triple.object}.")
        elif triple.predicate == "shipInService":
            sentences.append(f"{triple.subject} entered service on {triple.object}.")
        elif triple.predicate == "status":
            sentences.append(f"{triple.subject} is {triple.object}.")
        elif triple.predicate == "activeYearsStartDate":
            sentences.append(f"{triple.subject} started its active years in {triple.object}.")
        elif triple.predicate == "shipLaidDown":
            sentences.append(f"{triple.subject} was laid down on {triple.object}.")
        elif triple.predicate == "buildDate":
            sentences.append(f"{triple.subject} was built between {triple.object}.")
        elif triple.predicate == "cylinderCount":
            sentences.append(f"{triple.subject} has {triple.object} cylinders.")
        elif triple.predicate == "totalProduction":
            sentences.append(f"{triple.subject} had a total production of {triple.object}.")
        elif triple.predicate == "countryOrigin":
            sentences.append(f"{triple.subject} originated in {triple.object}.")
        elif triple.predicate == "diameter":
            sentences.append(f"{triple.subject} has a diameter of {triple.object}.")
        elif triple.predicate == "failedLaunches":
            sentences.append(f"{triple.subject} had {triple.object} failed launches.")
        elif triple.predicate == "rocketStages":
            sentences.append(f"{triple.subject} has {triple.object} rocket stages.")
        elif triple.predicate == "totalLaunches":
            sentences.append(f"{triple.subject} had a total of {triple.object} launches.")
        elif triple.predicate == "assembly":
            sentences.append(f"{triple.subject} was assembled in {triple.object}.")
        elif triple.predicate == "class":
            sentences.append(f"{triple.subject} is a {triple.object}.")
        elif triple.predicate == "designer":
            sentences.append(f"{triple.subject} was designed by {triple.object}.")
        elif triple.predicate == "modelYears":
            sentences.append(f"{triple.subject} was produced in {triple.object}.")
        elif triple.predicate == "country":
            sentences.append(f"{triple.subject} is in {triple.object}.")
        elif triple.predicate == "foundationPlace":
            sentences.append(f"{triple.subject} was founded in {triple.object}.")
        elif triple.predicate == "foundedBy":
            sentences.append(f"{triple.subject} was founded by {triple.object}.")
        elif triple.predicate == "designCompany":
            sentences.append(f"{triple.subject} was designed by {triple.object}.")
        elif triple.predicate == "productionStartYear":
            sentences.append(f"{triple.subject} production started in {triple.object}.")
        elif triple.predicate == "width":
            sentences.append(f"{triple.subject} has a width of {triple.object}.")
        elif triple.predicate == "layout":
            sentences.append(f"{triple.subject} has a {triple.object} layout.")
        elif triple.predicate == "parentCompany":
            sentences.append(f"{triple.subject} is a subsidiary of {triple.object}.")
        elif triple.predicate == "operator":
            sentences.append(f"{triple.subject} is operated by {triple.object}.")
        elif triple.predicate == "product":
            sentences.append(f"{triple.subject} produces {triple.object}.")
        elif triple.predicate == "city":
            sentences.append(f"{triple.subject} is located in {triple.object}.")
        elif triple.predicate == "successor":
            sentences.append(f"{triple.subject} was succeeded by {triple.object}.")
        elif triple.predicate == "fate":
            sentences.append(f"{triple.subject}'s fate was {triple.object}.")
        elif triple.predicate == "keyPerson":
            sentences.append(f"{triple.subject} had a key person named {triple.object}.")
        elif triple.predicate == "subsidiary":
            sentences.append(f"{triple.subject} has a subsidiary named {triple.object}.")
        elif triple.predicate == "comparable":
            sentences.append(f"{triple.subject} is comparable to {triple.object}.")
        elif triple.predicate == "finalFlight":
            sentences.append(f"{triple.subject}'s final flight was on {triple.object}.")
        elif triple.predicate == "function":
            sentences.append(f"{triple.subject} functions as a {triple.object}.")
        elif triple.predicate == "launchSite":
            sentences.append(f"{triple.subject} launches from {triple.object}.")
        elif triple.predicate == "maidenFlight":
            sentences.append(f"{triple.subject}'s maiden flight was on {triple.object}.")
        elif triple.predicate == "capital":
            sentences.append(f"{triple.subject} is the capital of {triple.object}.")
        else:
            sentences.append(f"{triple.subject} {triple.predicate} {triple.object}.")

    return " ".join(sentences)

# EVOLVE-BLOCK-END