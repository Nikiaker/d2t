from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    predicate_descriptions = {
        "cityServed": "serves the city of",
        "elevationAboveTheSeaLevel": "has an elevation of",
        "location": "is located in",
        "operatingOrganisation": "is operated by",
        "runwayLength": "has a runway length of",
        "runwayName": "has a runway named",
        "country": "is located in the country of",
        "isPartOf": "is part of",
        "1stRunwayLengthFeet": "has a first runway length of",
        "1stRunwaySurfaceType": "has a first runway surface type of",
        "3rdRunwayLengthFeet": "has a third runway length of",
        "icaoLocationIdentifier": "has an ICAO location identifier of",
        "locationIdentifier": "has a location identifier of",
        "elevationAboveTheSeaLevelInFeet": "has an elevation of",
        "iataLocationIdentifier": "has an IATA location identifier of",
        "nativeName": "has a native name of",
        "leaderParty": "has a leader party of",
        "capital": "has a capital of",
        "language": "has a language of",
        "leader": "has a leader of",
        "owner": "has an owner of",
        "1stRunwayLengthMetre": "has a first runway length of",
        "4thRunwaySurfaceType": "has a fourth runway surface type of",
        "5thRunwayNumber": "has a fifth runway number of",
        "largestCity": "has a largest city of",
        "4thRunwayLengthFeet": "has a fourth runway length of",
        "1stRunwayNumber": "has a first runway number of",
        "elevationAboveTheSeaLevelInMetres": "has an elevation of",
        "administrativeArrondissement": "has an administrative arrondissement of",
        "mayor": "has a mayor of",
        "2ndRunwaySurfaceType": "has a second runway surface type of",
        "3rdRunwaySurfaceType": "has a third runway surface type of",
        "runwaySurfaceType": "has a runway surface type of",
        "officialLanguage": "has an official language of",
        "city": "has a city of",
        "jurisdiction": "has a jurisdiction of",
        "demonym": "has a demonym of",
        "aircraftHelicopter": "has an aircraft helicopter of",
        "transportAircraft": "has a transport aircraft of",
        "currency": "has a currency of",
        "headquarter": "has a headquarter of",
        "class": "has a class of",
        "division": "has a division of",
        "order": "has an order of",
        "regionServed": "has a region served of",
        "leaderTitle": "has a leader title of",
        "hubAirport": "has a hub airport of",
        "aircraftFighter": "has an aircraft fighter of",
        "attackAircraft": "has an attack aircraft of",
        "battle": "has a battle of",
        "5thRunwaySurfaceType": "has a fifth runway surface type of",
        "countySeat": "has a county seat of",
        "chief": "has a chief of",
        "foundedBy": "was founded by",
        "postalCode": "has a postal code of",
        "areaCode": "has an area code of",
        "foundingYear": "was founded in",
        "ceremonialCounty": "has a ceremonial county of",
    }

    sentences = []
    for triple in triples:
        if triple.predicate in predicate_descriptions:
            sentences.append(f"{triple.subject} {predicate_descriptions[triple.predicate]} {triple.object}.")
        else:
            sentences.append(f"The {triple.predicate} of {triple.subject} is {triple.object}.")
    import nltk
    from nltk import word_tokenize, pos_tag
    nltk.download('averaged_perceptron_tagger_eng')
    nltk.download('punkt')

    # Join sentences using a more sophisticated NLP approach
    sentence = sentences[0]
    for s in sentences[1:]:
        tokens = word_tokenize(s)
        tagged = pos_tag(tokens)
        if tagged[0][1] == 'NN':  # If the first word is a noun, use "and"
            conjunction = "and"
        elif tagged[0][1] == 'VB':  # If the first word is a verb, use "also"
            conjunction = "also"
        else:
            conjunction = "moreover"
        sentence += " " + conjunction + " " + s
    return sentence

# EVOLVE-BLOCK-END