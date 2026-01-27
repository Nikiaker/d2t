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
        predicate = triple.predicate
        subject = triple.subject
        object_ = triple.object

        if predicate == "author":
            sentence += f"{subject} is written by {object_}."
        elif predicate == "isbnNumber":
            sentence += f" The ISBN number of {subject} is {object_}."
        elif predicate == "followedBy":
            sentence += f" {subject} is followed by {object_}."
        elif predicate == "language":
            sentence += f" It is written in {object_}."
        elif predicate == "mediaType":
            sentence += f" The media type is {object_}."
        elif predicate == "numberOfPages":
            sentence += f" It has {object_} pages."
        elif predicate == "precededBy":
            sentence += f" It is preceded by {object_}."
        elif predicate == "country":
            sentence += f" {subject} is in {object_}."
        elif predicate == "almaMater":
            sentence += f" {subject} attended {object_}."
        elif predicate == "doctoralAdvisor":
            sentence += f" {subject}'s doctoral advisor was {object_}."
        elif predicate == "nationality":
            sentence += f" {subject} is from {object_}."
        elif predicate == "residence":
            sentence += f" {subject} resides in {object_}."
        elif predicate == "codenCode":
            sentence += f" The coden code is {object_}."
        elif predicate == "issnNumber":
            sentence += f" The ISSN number is {object_}."
        elif predicate == "LCCN_number":
            sentence += f" The LCCN number is {object_}."
        elif predicate == "abbreviation":
            sentence += f" It is abbreviated as {object_}."
        elif predicate == "academicDiscipline":
            sentence += f" It belongs to {object_}."
        elif predicate == "publisher":
            sentence += f" It is published by {object_}."
        elif predicate == "firstPublicationYear":
            sentence += f" It was first published in {object_}."
        elif predicate == "editor":
            sentence += f" The editor is {object_}."
        elif predicate == "impactFactor":
            sentence += f" The impact factor is {object_}."
        elif predicate == "oclcNumber":
            sentence += f" The OCLC number is {object_}."
        elif predicate == "libraryofCongressClassification":
            sentence += f" The Library of Congress Classification is {object_}."
        elif predicate == "genre":
            sentence += f" It is a {object_}."
        elif predicate == "literaryGenre":
            sentence += f" It is a {object_}."
        elif predicate == "eissnNumber":
            sentence += f" The EISSN number is {object_}."
        elif predicate == "frequency":
            sentence += f" It is published {object_}."
        elif predicate == "headquarter":
            sentence += f" The headquarter is in {object_}."
        elif predicate == "leader":
            sentence += f" The leader is {object_}."
        elif predicate == "birthPlace":
            sentence += f" {subject} was born in {object_}."
        elif predicate == "affiliation":
            sentence += f" {subject} is affiliated with {object_}."
        elif predicate == "city":
            sentence += f" {subject} is located in {object_}."
        elif predicate == "president":
            sentence += f" The president is {object_}."
        elif predicate == "state":
            sentence += f" It is in {object_}."
        elif predicate == "spokenIn":
            sentence += f" It is spoken in {object_}."
        elif predicate == "influencedBy":
            sentence += f" {subject} was influenced by {object_}."
        elif predicate == "family":
            sentence += f" It belongs to the {object_} family."
        elif predicate == "ethnicGroup":
            sentence += f" The ethnic group is {object_}."
        elif predicate == "largestCity":
            sentence += f" The largest city is {object_}."
        elif predicate == "location":
            sentence += f" It is located in {object_}."
        elif predicate == "deathPlace":
            sentence += f" {subject} died in {object_}."
        elif predicate == "notableWork":
            sentence += f" A notable work is {object_}."
        elif predicate == "parentCompany":
            sentence += f" The parent company is {object_}."
        elif predicate == "regionServed":
            sentence += f" It serves the {object_} region."
        elif predicate == "founder":
            sentence += f" The founder is {object_}."
        elif predicate == "capital":
            sentence += f" The capital is {object_}."
        elif predicate == "demonym":
            sentence += f" The demonym is {object_}."
        elif predicate == "leaderTitle":
            sentence += f" The leader title is {object_}."
        elif predicate == "nickname":
            sentence += f" The nickname is {object_}."
        elif predicate == "genus":
            sentence += f" The genus is {object_}."
        elif predicate == "releaseDate":
            sentence += f" The release date is {object_}."
        elif predicate == "birthDate":
            sentence += f" The birth date is {object_}."
        else:
            sentence += f" {subject} is related to {object_}."

    return sentence

# EVOLVE-BLOCK-END