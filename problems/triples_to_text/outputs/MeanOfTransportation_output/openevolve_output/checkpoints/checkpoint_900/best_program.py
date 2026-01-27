from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    if not triples:
        return ""

    sentence = ""
    subject = triples[0].subject

    for triple in triples:
        predicate = triple.predicate
        object_val = triple.object

        if predicate == "alternativeName":
            sentence += f"{subject} is also known as \"{object_val}\". "
        elif predicate == "bodyStyle":
            sentence += f"{subject} has a {object_val} body style. "
        elif predicate == "engine":
            sentence += f"{subject} is powered by a {object_val}. "
        elif predicate == "manufacturer":
            sentence += f"{subject} is manufactured by {object_val}. "
        elif predicate == "relatedMeanOfTransportation":
            sentence += f"{subject} is related to {object_val}. "
        elif predicate == "transmission":
            sentence += f"{subject} has a {object_val} transmission. "
        elif predicate == "wheelbase":
            sentence += f"{subject} has a wheelbase of {object_val}. "
        elif predicate == "builder":
            sentence += f"{subject} was built by {object_val}. "
        elif predicate == "completionDate":
            sentence += f"{subject} was completed on {object_val}. "
        elif predicate == "length":
            sentence += f"{subject} has a length of {object_val}. "
        elif predicate == "powerType":
            sentence += f"{subject} uses {object_val} for power. "
        elif predicate == "shipClass":
            sentence += f"{subject} is a {object_val}. "
        elif predicate == "shipDisplacement":
            sentence += f"{subject} has a displacement of {object_val}. "
        elif predicate == "shipLaunch":
            sentence += f"{subject} was launched on {object_val}. "
        elif predicate == "shipOrdered":
            sentence += f"{subject} was ordered on {object_val}. "
        elif predicate == "shipPower":
            sentence += f"{subject} is powered by {object_val}. "
        elif predicate == "topSpeed":
            sentence += f"{subject} has a top speed of {object_val}. "
        elif predicate == "location":
            sentence += f"{subject} is located in {object_val}. "
        elif predicate == "christeningDate":
            sentence += f"{subject} was christened on {object_val}. "
        elif predicate == "maidenVoyage":
            sentence += f"{subject} had its maiden voyage on {object_val}. "
        elif predicate == "owner":
            sentence += f"{subject} is owned by {object_val}. "
        elif predicate == "shipBeam":
            sentence += f"{subject} has a beam of {object_val}. "
        elif predicate == "shipInService":
            sentence += f"{subject} entered service on {object_val}. "
        elif predicate == "status":
            sentence += f"{subject} is currently {object_val}. "
        elif predicate == "activeYearsStartDate":
            sentence += f"{subject} started its active years in {object_val}. "
        elif predicate == "shipLaidDown":
            sentence += f"{subject} was laid down on {object_val}. "
        elif predicate == "buildDate":
            sentence += f"{subject} was built between {object_val}. "
        elif predicate == "cylinderCount":
            sentence += f"{subject} has {object_val} cylinders. "
        elif predicate == "totalProduction":
            sentence += f"{subject} had a total production of {object_val}. "
        elif predicate == "countryOrigin":
            sentence += f"{subject} originates from {object_val}. "
        elif predicate == "diameter":
            sentence += f"{subject} has a diameter of {object_val}. "
        elif predicate == "failedLaunches":
            sentence += f"{subject} has had {object_val} failed launches. "
        elif predicate == "rocketStages":
            sentence += f"{subject} has {object_val} rocket stages. "
        elif predicate == "totalLaunches":
            sentence += f"{subject} has had {object_val} total launches. "
        elif predicate == "assembly":
            sentence += f"{subject} is assembled in {object_val}. "
        elif predicate == "class":
            sentence += f"{subject} is a {object_val}. "
        elif predicate == "designer":
            sentence += f"{subject} was designed by {object_val}. "
        elif predicate == "modelYears":
            sentence += f"{subject} was produced in {object_val}. "
        elif predicate == "country":
            sentence += f"{subject} is from {object_val}. "
        elif predicate == "foundationPlace":
            sentence += f"{subject} was founded in {object_val}. "
        elif predicate == "foundedBy":
            sentence += f"{subject} was founded by {object_val}. "
        elif predicate == "designCompany":
            sentence += f"{subject} was designed by {object_val}. "
        elif predicate == "productionStartYear":
            sentence += f"{subject} started production in {object_val}. "
        elif predicate == "width":
            sentence += f"{subject} has a width of {object_val}. "
        elif predicate == "layout":
            sentence += f"{subject} has a {object_val} layout. "
        elif predicate == "parentCompany":
            sentence += f"{subject} is a subsidiary of {object_val}. "
        elif predicate == "operator":
            sentence += f"{subject} is operated by {object_val}. "
        elif predicate == "product":
            sentence += f"{subject} produces {object_val}. "
        elif predicate == "city":
            sentence += f"{subject} is located in {object_val}. "
        elif predicate == "successor":
            sentence += f"{subject} was succeeded by {object_val}. "
        elif predicate == "fate":
            sentence += f"{subject}'s fate was {object_val}. "
        elif predicate == "keyPerson":
            sentence += f"{subject} had a key person named {object_val}. "
        elif predicate == "subsidiary":
            sentence += f"{subject} has a subsidiary named {object_val}. "
        elif predicate == "comparable":
            sentence += f"{subject} is comparable to {object_val}. "
        elif predicate == "finalFlight":
            sentence += f"{subject}'s final flight was on {object_val}. "
        elif predicate == "function":
            sentence += f"{subject} functions as a {object_val}. "
        elif predicate == "launchSite":
            sentence += f"{subject} launches from {object_val}. "
        elif predicate == "maidenFlight":
            sentence += f"{subject}'s maiden flight was on {object_val}. "
        elif predicate == "capital":
            sentence += f"{subject}'s capital is {object_val}. "
        elif predicate == "demonym":
            sentence += f"{subject}'s demonym is {object_val}. "
        elif predicate == "leader":
            sentence += f"{subject}'s leader is {object_val}. "
        elif predicate == "partialFailures":
            sentence += f"{subject} has had {object_val} partial failures. "
        elif predicate == "site":
            sentence += f"{subject} is located at {object_val}. "
        elif predicate == "headquarter":
            sentence += f"{subject}'s headquarter is at {object_val}. "
        elif predicate == "associatedRocket":
            sentence += f"{subject} is associated with {object_val}. "
        elif predicate == "saint":
            sentence += f"{subject}'s saint is {object_val}. "
        elif predicate == "employer":
            sentence += f"{subject} was employed by {object_val}. "
        elif predicate == "ethnicGroup":
            sentence += f"{subject}'s ethnic group is {object_val}. "
        elif predicate == "language":
            sentence += f"{subject}'s language is {object_val}. "
        elif predicate == "leaderTitle":
            sentence += f"{subject}'s leader title is {object_val}. "

    return sentence

# EVOLVE-BLOCK-END