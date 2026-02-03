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

    sentences = []
    for triple in triples:
        predicate = triple.predicate
        subject = triple.subject
        object_ = triple.object

        if predicate == "associatedBand/associatedMusicalArtist":
            sentences.append(f"{subject} is associated with {object_}.")
        elif predicate == "background":
            sentences.append(f"{subject} has a background as a {object_}.")
        elif predicate == "birthDate":
            sentences.append(f"{subject} was born on {object_}.")
        elif predicate == "genre":
            sentences.append(f"{subject} performs {object_} music.")
        elif predicate == "instrument":
            sentences.append(f"{subject} plays the {object_}.")
        elif predicate == "origin":
            sentences.append(f"{subject} is from {object_}.")
        elif predicate == "activeYearsStartYear":
            sentences.append(f"{subject} became active in {object_}.")
        elif predicate == "birthPlace":
            sentences.append(f"{subject} was born in {object_}.")
        elif predicate == "birthYear":
            sentences.append(f"{subject} was born in {object_}.")
        elif predicate == "occupation":
            sentences.append(f"{subject} is a {object_}.")
        elif predicate == "recordLabel":
            sentences.append(f"{subject} is signed to {object_}.")
        elif predicate == "deathPlace":
            sentences.append(f"{subject} died in {object_}.")
        elif predicate == "alternativeName":
            sentences.append(f"{subject} is also known as {object_}.")
        elif predicate == "activeYearsEndYear":
            sentences.append(f"{subject} was active until {object_}.")
        elif predicate == "deathDate":
            sentences.append(f"{subject} died on {object_}.")
        elif predicate == "nationality":
            sentences.append(f"{subject} is from {object_}.")
        elif predicate == "professionalField":
            sentences.append(f"{subject} works in {object_}.")
        elif predicate == "musicFusionGenre":
            sentences.append(f"{object_} is a fusion genre of {subject}.")
        elif predicate == "musicSubgenre":
            sentences.append(f"{subject} is a subgenre of {object_}.")
        elif predicate == "stylisticOrigin":
            sentences.append(f"{subject} has stylistic origins in {object_}.")
        elif predicate == "language":
            sentences.append(f"{subject} is spoken in {object_}.")
        elif predicate == "officialLanguage":
            sentences.append(f"{subject} has {object_} as an official language.")
        elif predicate == "derivative":
            sentences.append(f"{subject} is a derivative of {object_}.")
        elif predicate == "location":
            sentences.append(f"{subject} is located in {object_}.")
        elif predicate == "governingBody":
            sentences.append(f"{subject} is governed by {object_}.")
        elif predicate == "leader":
            sentences.append(f"{subject} is led by {object_}.")
        elif predicate == "leaderTitle":
            sentences.append(f"{subject} holds the title of {object_}.")
        elif predicate == "country":
            sentences.append(f"{subject} is located in {object_}.")
        elif predicate == "ethnicGroup":
            sentences.append(f"{subject} is inhabited by the {object_}.")
        elif predicate == "parentCompany":
            sentences.append(f"{subject} is a subsidiary of {object_}.")
        elif predicate == "bandMember":
            sentences.append(f"{subject} features {object_}.")
        elif predicate == "capital":
            sentences.append(f"{subject} has {object_} as its capital.")
        elif predicate == "anthem":
            sentences.append(f"{subject} has the anthem {object_}.")
        elif predicate == "currency":
            sentences.append(f"{subject} uses the currency {object_}.")
        elif predicate == "demonym":
            sentences.append(f"People from {subject} are called {object_}.")
        elif predicate == "isPartOf":
            sentences.append(f"{subject} is part of {object_}.")
        elif predicate == "distributingCompany":
            sentences.append(f"{subject} is distributed by {object_}.")
        elif predicate == "training":
            sentences.append(f"{subject} received training at {object_}.")
        elif predicate == "populationDensity":
            sentences.append(f"{subject} has a population density of {object_}.")
        elif predicate == "meaning":
            sentences.append(f"{subject} means {object_}.")
        elif predicate == "longName":
            sentences.append(f"{subject} is also known as {object_}.")
        elif predicate == "areaTotal":
            sentences.append(f"{subject} has a total area of {object_}.")
        elif predicate == "foundingDate":
            sentences.append(f"{subject} was founded on {object_}.")
        elif predicate == "elevationAboveTheSeaLevel":
            sentences.append(f"{subject} is {object_} above sea level.")
        elif predicate == "postalCode":
            sentences.append(f"{subject} has the postal code {object_}.")
        else:
            sentences.append(f"{subject} {predicate} {object_}.")

    return " ".join(sentences)

# EVOLVE-BLOCK-END