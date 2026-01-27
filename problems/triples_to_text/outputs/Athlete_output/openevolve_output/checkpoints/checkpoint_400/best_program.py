from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    if not triples:
        return ""

    sentence = ""
    subject = triples[0].subject
    clauses = []

    for triple in triples:
        predicate = triple.predicate
        object_val = triple.object

        if predicate == "league":
            clauses.append(f"plays in the {object_val}")
        elif predicate == "manager":
            clauses.append(f"is managed by {object_val}")
        elif predicate == "birthDate":
            clauses.append(f"was born on {object_val}")
        elif predicate == "birthPlace":
            clauses.append(f"was born in {object_val}")
        elif predicate == "currentclub":
            clauses.append(f"currently plays for {object_val}")
        elif predicate == "birthYear":
            clauses.append(f"was born in {object_val}")
        elif predicate == "club":
            clauses.append(f"plays for {object_val}")
        elif predicate == "country":
            clauses.append(f"is from {object_val}")
        else:
            clauses.append(f"whose {predicate} is {object_val}")

    sentence = ""
    if not subject:
        return sentence

    clauses = []
    for i, triple in enumerate(triples):
        predicate = triple.predicate
        object_val = triple.object

        if predicate == "league":
            clauses.append(f"plays in the {object_val}")
        elif predicate == "manager":
            clauses.append(f"is managed by {object_val}")
        elif predicate == "birthDate":
            clauses.append(f"was born on {object_val}")
        elif predicate == "birthPlace":
            clauses.append(f"was born in {object_val}")
        elif predicate == "currentclub":
            clauses.append(f"currently plays for {object_val}")
        elif predicate == "birthYear":
            clauses.append(f"was born in {object_val}")
        elif predicate == "club":
            clauses.append(f"plays for {object_val}")
        elif predicate == "country":
            clauses.append(f"is from {object_val}")
        elif predicate == "height":
            clauses.append(f"is {object_val} tall")
        elif predicate == "deathPlace":
            clauses.append(f"died in {object_val}")
        elif predicate == "activeYearsStartYear":
            clauses.append(f"began their career in {object_val}")
        else:
            clauses.append(f"whose {predicate} is {object_val}")

    sentence = f"{subject} "
    if clauses:
        sentence += ", ".join(clauses[:-1])
        if len(clauses) > 1:
            sentence += f" and {clauses[-1]}"
        else:
            sentence += clauses[0]
    sentence += "."

    return sentence

    for i, triple in enumerate(triples):
        if i == 0:
            sentence += f"{subject} {triple.predicate} {triple.object}"
        else:
            if triple.predicate == "league":
                sentence += f" and plays in the {triple.object}"
            elif triple.predicate == "manager":
                sentence += f", who is managed by {triple.object}"
            elif triple.predicate == "birthDate":
                sentence += f" and was born on {triple.object}"
            elif triple.predicate == "birthPlace":
                sentence += f", originally from {triple.object}"
            elif triple.predicate == "currentclub":
                 sentence += f" and currently plays for {triple.object}"
            else:
                if triple.predicate == "country":
                    sentence += f" and is located in {triple.object}"
                else:
                    sentence += f" and {triple.predicate} is {triple.object}"

    return sentence.strip() + "."

# EVOLVE-BLOCK-END