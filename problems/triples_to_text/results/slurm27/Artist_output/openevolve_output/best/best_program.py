from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

# New replacement code
def predict(triples: list[Triple]) -> str:
    subjects = {}
    for triple in triples:
        if triple.subject not in subjects:
            subjects[triple.subject] = []
        subjects[triple.subject].append((triple.predicate, triple.object))

    sentences = []
    for subject, predicates in subjects.items():
        sentence = f"{subject} "
        descriptions = []

        for predicate, obj in predicates:
            if predicate == "associatedBand/associatedMusicalArtist":
                descriptions.append(f"is associated with the band {obj}")
            elif predicate == "genre":
                descriptions.append(f"performs in the {obj} genre")
            elif predicate == "instrument":
                descriptions.append(f"plays the {obj}")
            elif predicate == "occupation":
                descriptions.append(f"works as a {obj}")
            elif predicate == "background":
                descriptions.append(f"has a background as a {obj}")
            elif predicate == "birthPlace":
                descriptions.append(f"was born in {obj}")
            elif predicate == "birthDate":
                descriptions.append(f"was born on {obj}")
            elif predicate == "activeYearsStartYear":
                descriptions.append(f"started their career in {obj}")
            elif predicate == "activeYearsEndYear":
                descriptions.append(f"ended their career in {obj}")
            elif predicate == "recordLabel":
                descriptions.append(f"is signed to {obj} records")
            elif predicate == "leaderTitle":
                descriptions.append(f"has a leader title of {obj}")
            elif predicate == "leader":
                descriptions.append(f"has a leader named {obj}")
            elif predicate == "country":
                descriptions.append(f"is located in the country of {obj}")
            elif predicate == "nationality":
                descriptions.append(f"has a nationality of {obj}")
            elif predicate == "deathDate":
                descriptions.append(f"died on {obj}")
            elif predicate == "deathPlace":
                descriptions.append(f"died in {obj}")
            elif predicate == "musicFusionGenre":
                descriptions.append(f"performs music that is a fusion of {obj}")
            elif predicate == "stylisticOrigin":
                descriptions.append(f"has a stylistic origin of {obj}")
            else:
                descriptions.append(f"has a {predicate} of {obj}")

        if descriptions:
            sentence += f" who {', '.join(descriptions)}."
        else:
            sentence += "."

        sentences.append(sentence)

    # Try to create a complex sentence from all the given triples
    if len(sentences) > 1:
        main_subject = sentences[0].split(' ')[0]
        complex_sentence = f"{main_subject} "
        descriptions = []
        relations = []

        for i, sentence in enumerate(sentences):
            subject = sentence.split(' ')[0]
            rest_of_sentence = ' '.join(sentence.split(' ')[1:]).replace('.', '')
            if "who" in rest_of_sentence:
                descriptions.append(rest_of_sentence.replace("who ", ""))
            else:
                if i > 0:
                    relations.append(f"and is also {rest_of_sentence}")
                else:
                    descriptions.append(rest_of_sentence)

        if descriptions:
            complex_sentence += f" who {', '.join(descriptions)}"
        if relations:
            complex_sentence += f" {', '.join(relations)}."
        else:
            complex_sentence += "."
        return complex_sentence
    else:
        # For single sentence, try to rephrase it to make it more coherent
        sentence = sentences[0]
        subject = sentence.split(' ')[0]
        rest_of_sentence = ' '.join(sentence.split(' ')[1:]).replace('.', '')
        if "who" in rest_of_sentence:
            return f"{subject} {rest_of_sentence.replace('who', '')}."
        elif "performs" in rest_of_sentence:
            return f"{subject} is known for {rest_of_sentence}."
        else:
            return sentence

# EVOLVE-BLOCK-END