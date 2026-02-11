from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

# Load the language model and tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

def predict(triples: list[Triple]) -> str:
    sentences = []
    if not triples:
        return ""

    # Group triples by subject for better coherence
    grouped_triples = {}
    for triple in triples:
        if triple.subject not in grouped_triples:
            grouped_triples[triple.subject] = []
        grouped_triples[triple.subject].append(triple)

    for subject, triple_list in grouped_triples.items():
        sentence = subject
        for triple in triple_list:
            if triple.predicate == "associatedBand/associatedMusicalArtist":
                sentence += f" is associated with {triple.object}."
            elif triple.predicate == "background":
                sentence += f" has a background as a {triple.object}."
            elif triple.predicate == "birthDate":
                sentence += f" was born on {triple.object}."
            elif triple.predicate == "genre":
                sentence += f" performs {triple.object} music."
            elif triple.predicate == "instrument":
                sentence += f" plays the {triple.object}."
            elif triple.predicate == "origin":
                sentence += f" originates from {triple.object}."
            elif triple.predicate == "activeYearsStartYear":
                sentence += f" became active in {triple.object}."
            elif triple.predicate == "birthPlace":
                sentence += f" was born in {triple.object}."
            elif triple.predicate == "birthYear":
                sentence += f" was born in {triple.object}."
            elif triple.predicate == "occupation":
                sentence += f" works as a {triple.object}."
            elif triple.predicate == "recordLabel":
                sentence += f" is signed to {triple.object}."
            elif triple.predicate == "deathPlace":
                sentence += f" died in {triple.object}."
            elif triple.predicate == "alternativeName":
                sentence += f" is also known as {triple.object}."
            elif triple.predicate == "activeYearsEndYear":
                sentence += f" was active until {triple.object}."
            elif triple.predicate == "deathDate":
                sentence += f" died on {triple.object}."
            elif triple.predicate == "nationality":
                sentence += f" is from {triple.object}."
            elif triple.predicate == "professionalField":
                sentence += f" works in the field of {triple.object}."
            elif triple.predicate == "musicFusionGenre":
                sentence += f" is a fusion of {triple.object}."
            elif triple.predicate == "musicSubgenre":
                sentence += f" is a subgenre of {triple.object}."
            elif triple.predicate == "stylisticOrigin":
                sentence += f" originates from {triple.object}."
            elif triple.predicate == "language":
                sentence += f" is spoken in {triple.object}."
            elif triple.predicate == "officialLanguage":
                sentence += f" is an official language of {triple.object}."
            elif triple.predicate == "derivative":
                sentence += f" is a derivative of {triple.object}."
            elif triple.predicate == "location":
                sentence += f" is located in {triple.object}."
            elif triple.predicate == "governingBody":
                sentence += f" is governed by {triple.object}."
            elif triple.predicate == "leader":
                sentence += f" is led by {triple.object}."
            elif triple.predicate == "leaderTitle":
                sentence += f" holds the title of {triple.object}."
            elif triple.predicate == "country":
                sentence += f" is a city in {triple.object}."
            elif triple.predicate == "ethnicGroup":
                sentence += f" is inhabited by {triple.object}."
            elif triple.predicate == "parentCompany":
                sentence += f" is a subsidiary of {triple.object}."
            elif triple.predicate == "bandMember":
                sentence += f" has {triple.object} as a member."
            elif triple.predicate == "capital":
                sentence += f" has {triple.object} as its capital."
            elif triple.predicate == "anthem":
                sentence += f" has {triple.object} as its anthem."
            elif triple.predicate == "currency":
                sentence += f" uses {triple.object} as its currency."
            elif triple.predicate == "demonym":
                sentence += f" people are called {triple.object}."
            elif triple.predicate == "isPartOf":
                sentence += f" is part of {triple.object}."
            elif triple.predicate == "distributingCompany":
                sentence += f" is distributed by {triple.object}."
            elif triple.predicate == "training":
                sentence += f" received training at {triple.object}."
            elif triple.predicate == "populationDensity":
                sentence += f" has a population density of {triple.object}."
            elif triple.predicate == "meaning":
                sentence += f" means {triple.object}."
            elif triple.predicate == "longName":
                sentence += f" is officially known as {triple.object}."
            elif triple.predicate == "areaTotal":
                sentence += f" has a total area of {triple.object}."
            elif triple.predicate == "foundingDate":
                sentence += f" was founded on {triple.object}."
            elif triple.predicate == "elevationAboveTheSeaLevel":
                sentence += f" is located at an elevation of {triple.object}."
            elif triple.predicate == "postalCode":
                sentence += f" uses the postal code {triple.object}."
            else:
                sentence += f" has {triple.predicate} of {triple.object}."
        sentences.append(sentence)
    return " ".join(sentences)

# EVOLVE-BLOCK-END