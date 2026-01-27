from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    sentence = ""
    for i, triple in enumerate(triples):
        subject = triple.subject
        predicate = triple.predicate
        object_ = triple.object

        if predicate == "associatedBand/associatedMusicalArtist":
            sentence += f"{subject} is associated with {object_}."
        elif predicate == "background":
            sentence += f" {subject} has a background as a {object_}."
        elif predicate == "birthDate":
            sentence += f" {subject} was born on {object_}."
        elif predicate == "genre":
            sentence += f" {subject}'s genre is {object_}."
        elif predicate == "instrument":
            sentence += f" {subject} plays the {object_}."
        elif predicate == "origin":
            sentence += f" {subject} originates from {object_}."
        elif predicate == "activeYearsStartYear":
            sentence += f" {subject} became active in {object_}."
        elif predicate == "birthPlace":
            sentence += f" {subject} was born in {object_}."
        elif predicate == "birthYear":
            sentence += f" {subject} was born in {object_}."
        elif predicate == "occupation":
            sentence += f" {subject} works as a {object_}."
        elif predicate == "recordLabel":
            sentence += f" {subject} is signed to {object_}."
        elif predicate == "deathPlace":
            sentence += f" {subject} died in {object_}."
        elif predicate == "alternativeName":
            sentence += f" {subject} is also known as {object_}."
        elif predicate == "activeYearsEndYear":
            sentence += f" {subject} was active until {object_}."
        elif predicate == "deathDate":
            sentence += f" {subject} died on {object_}."
        elif predicate == "nationality":
            sentence += f" {subject} is from {object_}."
        elif predicate == "professionalField":
            sentence += f" {subject} works in the field of {object_}."
        elif predicate == "musicFusionGenre":
            sentence += f" {subject} is a fusion of {object_}."
        elif predicate == "musicSubgenre":
            sentence += f" {subject} is a subgenre of {object_}."
        elif predicate == "stylisticOrigin":
            sentence += f" {subject} originates from {object_}."
        elif predicate == "language":
            sentence += f" {subject} uses {object_}."
        elif predicate == "officialLanguage":
            sentence += f" {subject}'s official language is {object_}."
        elif predicate == "derivative":
            sentence += f" {subject} is derived from {object_}."
        elif predicate == "location":
            sentence += f" {subject} is located in {object_}."
        elif predicate == "governingBody":
            sentence += f" {subject} is governed by {object_}."
        elif predicate == "leader":
            sentence += f" {subject}'s leader is {object_}."
        elif predicate == "leaderTitle":
            sentence += f" {subject}'s leader title is {object_}."
        elif predicate == "country":
            capital = next((t.object for t in triples if t.subject == object_ and t.predicate == "capital"), None)
            currency = next((t.object for t in triples if t.subject == object_ and t.predicate == "currency"), None)
            language = next((t.object for t in triples if t.subject == object_ and t.predicate == "officialLanguage"), None)

            parts = [f"{subject} is in {object_}"]
            if capital:
                parts.append(f"which has {capital} as its capital")
            if currency:
                parts.append(f"where the currency is {currency}")
            if language:
                parts.append(f"and {language} is spoken")

            sentence += ", ".join(parts) + ". "
        elif predicate == "ethnicGroup":
            sentence += f"{object_} are an ethnic group in {subject}. "
        elif predicate == "parentCompany":
            sentence += f"{object_} is the parent company of {subject}. "
        elif predicate == "bandMember":
            sentence += f"{object_} is a member of the band {subject}. "
        elif predicate == "capital":
            sentence += f"{subject} is the capital of {object_}. "
        elif predicate == "anthem":
            sentence += f"The anthem of {subject} is {object_}. "
        elif predicate == "currency":
            sentence += f"The currency of {subject} is {object_}. "
        elif predicate == "demonym":
            sentence += f"People from {subject} are called {object_}. "
        elif predicate == "isPartOf":
            sentence += f"{subject} is part of {object_}. "
        elif predicate == "distributingCompany":
            sentence += f"{subject} is distributed by {object_}. "
        elif predicate == "training":
            sentence += f" {subject} trained at {object_}."
        elif predicate == "populationDensity":
            sentence += f" {subject} has a population density of {object_}."
        elif predicate == "meaning":
            sentence += f" {subject} means {object_}."
        elif predicate == "longName":
            sentence += f" {subject}'s long name is {object_}."
        elif predicate == "areaTotal":
            sentence += f" {subject} has an area of {object_}."
        elif predicate == "foundingDate":
            sentence += f" {subject} was founded on {object_}."
        elif predicate == "elevationAboveTheSeaLevel":
            sentence += f" {subject}'s elevation is {object_}."
        elif predicate == "postalCode":
            sentence += f" {subject}'s postal code is {object_}."
        else:
            sentence += f" {subject} is related to {object_}."

    return sentence

# EVOLVE-BLOCK-END