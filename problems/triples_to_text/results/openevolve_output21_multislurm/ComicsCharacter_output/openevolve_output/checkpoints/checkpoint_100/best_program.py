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