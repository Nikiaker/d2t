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

    if not triples:
        return ""

    sentence = f"{triples[0].subject}"
    relative_clauses = []
    for i, triple in enumerate(triples):
        predicate = triple.predicate
        object_val = triple.object

        if predicate == "league":
            relative_clauses.append(f"who plays in the {object_val}")
        elif predicate == "manager":
            relative_clauses.append(f"who is managed by {object_val}")
        elif predicate == "birthDate":
            relative_clauses.append(f"who was born on {object_val}")
        elif predicate == "birthPlace":
            relative_clauses.append(f"who was born in {object_val}")
        elif predicate == "currentclub":
            relative_clauses.append(f"who currently plays for {object_val}")
        elif predicate == "birthYear":
            relative_clauses.append(f"who was born in {object_val}")
        elif predicate == "club":
            relative_clauses.append(f"who plays for {object_val}")
        elif predicate == "country":
            relative_clauses.append(f"who is from {object_val}")
        elif predicate == "height":
            relative_clauses.append(f"who is {object_val} tall")
        elif predicate == "deathPlace":
            relative_clauses.append(f"who died in {object_val}")
        elif predicate == "activeYearsStartYear":
            relative_clauses.append(f"who began their career in {object_val}")
        else:
            relative_clauses.append(f"whose {predicate} is {object_val}")

    if relative_clauses:
        sentence += " " + ", ".join(relative_clauses[:-1])
        if len(relative_clauses) > 1:
            sentence += f" and {relative_clauses[-1]}"
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