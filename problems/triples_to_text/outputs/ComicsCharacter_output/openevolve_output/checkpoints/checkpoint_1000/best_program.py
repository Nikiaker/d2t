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

        if predicate == "alternativeName":
            sentence += f"{subject} is also known as {object_}. "
        elif predicate == "creator":
            sentence += f"{subject} was created by {object_}. "
        elif predicate == "fullName":
            sentence += f"{subject}'s full name is {object_}. "
        elif predicate == "foundedBy":
            sentence += f"{subject} was founded by {object_}. "
        elif predicate == "keyPerson":
            sentence += f"{subject} has {object_} as a key person. "
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
            sentence += f"{object_} distributes {subject}. "
        elif predicate == "birthPlace":
            sentence += f"{subject} was born in {object_}. "
        elif predicate == "nationality":
            sentence += f"{subject} is a {object_} national. "
        elif predicate == "award":
            sentence += f"{subject} won the {object_}. "
        elif predicate == "broadcastedBy":
            sentence += f"{subject} is broadcasted by {object_}. "
        elif predicate == "firstAired":
            sentence += f"{subject} first aired on {object_}. "
        elif predicate == "series":
            sentence += f"{subject} is part of the {object_} series. "
        elif predicate == "child":
            sentence += f"{subject}'s child is {object_}. "
        else:
            sentence += f"The {predicate} of {subject} is {object_}. "

    return sentence

# EVOLVE-BLOCK-END