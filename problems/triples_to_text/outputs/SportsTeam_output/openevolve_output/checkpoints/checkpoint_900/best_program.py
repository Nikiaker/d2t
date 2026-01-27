from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    sentence = ""
    subject = ""
    for triple in triples:
        if not subject:
            subject = triple.subject
            sentence += f"{subject} "

        if triple.predicate == "numberOfMembers":
            sentence += f"has {triple.object} members. "
        elif triple.predicate == "season":
            sentence += f"competed in the {triple.object} season. "
        elif triple.predicate == "league":
            sentence += f"plays in the {triple.object} league. "
        elif triple.predicate == "manager":
            sentence += f"is managed by {triple.object}. "
        elif triple.predicate == "ground":
            sentence += f"plays at {triple.object}. "
        elif triple.predicate == "fullName":
            sentence += f"is formally known as {triple.object}. "
        elif triple.predicate == "chairman":
            sentence += f"has {triple.object} as chairman. "
        elif triple.predicate == "location":
            sentence += f"is located in {triple.object}. "
        elif triple.predicate == "owner":
            sentence += f"is owned by {triple.object}. "
        elif triple.predicate == "nickname":
            sentence += f"is also known as {triple.object}. "
        elif triple.predicate == "chairmanTitle":
            sentence += f"has a chairman titled as {triple.object}. "
        elif triple.predicate == "isPartOf":
            sentence += f"is part of {triple.object}. "
        elif triple.predicate == "leader":
            sentence += f"is led by {triple.object}. "
        elif triple.predicate == "part":
            sentence += f"is a part of {triple.object}. "
        elif triple.predicate == "mayor":
            sentence += f"has {triple.object} as mayor. "
        elif triple.predicate == "champions":
            sentence += f"has {triple.object} as champions. "
        elif triple.predicate == "country":
            sentence += f"is in {triple.object}. "
        elif triple.predicate == "club":
            sentence += f"plays for {triple.object}. "
        elif triple.predicate == "capital":
            if "is in" in sentence:
                sentence += f"and its capital is {triple.object}. "
            else:
                sentence += f"which has {triple.object} as its capital. "
        elif triple.predicate == "currency":
            sentence += f"uses {triple.object} as currency. "
        elif triple.predicate == "demonym":
            sentence += f"is known for its {triple.object}. "
        elif triple.predicate == "language":
            sentence += f"speaks {triple.object}. "
        elif triple.predicate == "leaderParty":
            sentence += f"is led by the {triple.object} party. "
        elif triple.predicate == "officialLanguage":
            sentence += f"has {triple.object} as its official language. "
        elif triple.predicate == "birthPlace":
            sentence += f"was born in {triple.object}. "
        elif triple.predicate == "youthclub":
            sentence += f"came from the youth club {triple.object}. "
        elif triple.predicate == "operator":
            sentence += f"is operated by {triple.object}. "
        elif triple.predicate == "tenant":
            sentence += f"has {triple.object} as tenant. "
        elif triple.predicate == "city":
            sentence += f"is in the city of {triple.object}. "
        elif triple.predicate == "state":
            sentence += f"is in the state of {triple.object}. "
        else:
            sentence += f"with {triple.predicate} being {triple.object}. "

    return sentence.rstrip(". ") + "."

# EVOLVE-BLOCK-END