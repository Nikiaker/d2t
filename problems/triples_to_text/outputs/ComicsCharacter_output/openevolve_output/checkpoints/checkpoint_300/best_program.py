from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    sentence = ""
    i = 0
    while i < len(triples):
        subject = triples[i].subject
        predicate = triples[i].predicate
        object_ = triples[i].object

        if predicate == "alternativeName":
            sentence += f"{subject} is also known as {object_}. "
        elif predicate == "creator":
            creators = [object_]
            i += 1
            while i < len(triples) and triples[i].subject == subject and triples[i].predicate == "creator":
                creators.append(triples[i].object)
                i += 1
            if len(creators) > 1:
                sentence += f"{subject} was created by {', '.join(creators)}. "
            else:
                sentence += f"{subject} was created by {object_}. "
            continue
        elif predicate == "fullName":
            sentence += f"{subject}, whose full name is {object_}, "
        elif predicate == "foundedBy":
            sentence += f"{subject} was founded by {object_}. "
        elif predicate == "nationality":
            sentence += f"{subject} is of {object_} nationality. "
            continue
        elif predicate == "birthPlace":
            sentence += f"{subject} was born in {object_}. "
            continue
        elif predicate == "award":
            sentence += f"{subject} won the {object_}. "
            continue
        elif predicate == "broadcastedBy":
            sentence += f"{subject} is broadcasted by {object_}. "
            continue
        elif predicate == "firstAired":
            sentence += f"{subject} first aired on {object_}. "
            continue
        elif predicate == "starring":
            sentence += f"{subject} stars {object_}. "
            continue
        elif predicate == "series":
            sentence += f"{subject} is part of the {object_}. "
            continue
        elif predicate == "alternativeName":
            sentence += f"{subject} is also known as {object_}. "
            continue
        elif predicate == "keyPerson":
            sentence += f"{subject}'s key person is {object_}. "
        elif predicate == "city":
            sentence += f"{subject} is located in {object_}. "
        elif predicate == "product":
            sentence += f"{subject} produces {object_}. "
        elif predicate == "lastAired":
            sentence += f"{subject} last aired on {object_}. "
        elif predicate == "starring":
            sentence += f"{subject} stars {object_}. "
        elif predicate == "firstAppearanceInFilm":
            sentence += f"{subject} first appeared in {object_}. "
        elif predicate == "voice":
            sentence += f"{subject} is voiced by {object_}. "
        elif predicate == "distributor":
            sentence += f"{subject} is distributed by {object_}. "
        elif predicate == "birthPlace":
            sentence += f"{subject} was born in {object_}. "
        elif predicate == "nationality":
            sentence += f"{subject} is of {object_} nationality. "
        elif predicate == "award":
            sentence += f"{subject} won the {object_}. "
        elif predicate == "broadcastedBy":
            sentence += f"{subject} is broadcasted by {object_}. "
        elif predicate == "firstAired":
            sentence += f"{subject} first aired on {object_}. "
        elif predicate == "series":
            sentence += f"{subject} is part of the {object_}. "
        elif predicate == "child":
            sentence += f"{subject}'s child is {object_}. "
        else:
            sentence += f"The {predicate} of {subject} is {object_}. "
        i += 1

    return sentence.strip()

# EVOLVE-BLOCK-END

    def combine_triples(sentence, triple, i, triples):
        subject = triple.subject
        predicate = triple.predicate
        object_ = triple.object

        if i + 1 < len(triples) and triples[i + 1].subject == subject:
            next_triple = triples[i + 1]
            next_predicate = next_triple.predicate
            next_object_ = next_triple.object

            if next_predicate == "alternativeName":
                sentence += f", also known as {next_object_}"
            elif next_predicate == "creator":
                sentence += f", created by {next_object_}"
            elif next_predicate == "nationality":
                sentence += f", who is of {next_object_} nationality"
            elif next_predicate == "birthPlace":
                sentence += f", born in {next_object_}"
            elif next_predicate == "series":
                sentence += f", part of the {next_object_}"
            else:
                sentence += f" and {next_predicate} is {next_object_}"
            i += 1  # Skip the next triple as it's been combined
        return sentence, i