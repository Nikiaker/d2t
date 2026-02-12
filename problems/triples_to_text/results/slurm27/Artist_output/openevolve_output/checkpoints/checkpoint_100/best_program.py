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

    sentences = []
    for subject, predicates in subjects.items():
        sentence = f"{subject} "
        associated_bands = []
        genres = []
        instruments = []
        occupations = []
        backgrounds = []
        birth_places = []
        other_predicates = []
        birth_years = []
        active_years_start = []
        active_years_end = []
        record_labels = []

        for predicate, obj in predicates:
            if predicate == "associatedBand/associatedMusicalArtist":
                associated_bands.append(obj)
            elif predicate == "genre":
                genres.append(obj)
            elif predicate == "instrument":
                instruments.append(obj)
            elif predicate == "occupation":
                occupations.append(obj)
            elif predicate == "background":
                backgrounds.append(obj)
            elif predicate == "birthPlace":
                birth_places.append(obj)
            elif predicate == "birthYear":
                birth_years.append(obj)
            elif predicate == "activeYearsStartYear":
                active_years_start.append(obj)
            elif predicate == "activeYearsEndYear":
                active_years_end.append(obj)
            elif predicate == "recordLabel":
                record_labels.append(obj)
            else:
                other_predicates.append((predicate, obj))

        if genres:
            sentence += f"is a {', '.join(genres)} musician"
        if instruments:
            sentence += f" who plays the {', '.join(instruments)}"
        if occupations:
            sentence += f" and works as a {', '.join(occupations)}"
        if backgrounds:
            sentence += f" with a background as {', '.join(backgrounds)}"
        if birth_places:
            sentence += f", born in {', '.join(birth_places)}"
        if birth_years:
            sentence += f", born in {', '.join(birth_years)}"
        if active_years_start:
            sentence += f", active since {', '.join(active_years_start)}"
        if active_years_end:
            sentence += f", active until {', '.join(active_years_end)}"
        if associated_bands:
            sentence += f", and is associated with the bands {', '.join(associated_bands)}"
        if record_labels:
            sentence += f", and is signed to {', '.join(record_labels)} records"
        for predicate, obj in other_predicates:
            sentence += f", with a {predicate} of {obj}"

        sentences.append(sentence)

    # Try to create a complex sentence from all the given triples
    if len(sentences) > 1:
        complex_sentence = sentences[0]
        for sentence in sentences[1:]:
            if "is a" in sentence:
                complex_sentence += f", and {sentence}"
            else:
                complex_sentence += f", {sentence}"
        return complex_sentence + "."
    else:
        return sentences[0] + "."

# EVOLVE-BLOCK-END