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

        predicate = triple.predicate
        object_val = triple.object

        if predicate == "country":
            sentence += f"is in {object_val} "
        elif predicate == "ingredient":
            sentence += f"contains {object_val} "
        elif predicate == "region":
            sentence += f"is from the {object_val} region "
        elif predicate == "capital":
            sentence += f"where the capital is {object_val} "
        elif predicate == "served":
            sentence += f"is served {object_val} "
        elif predicate == "mainIngredient":
            sentence += f"is made with {object_val} "
        else:
            if predicate == "course":
                sentence += f"which is a {object_val} "
            elif predicate == "dishVariation":
                sentence += f", a variation of {object_val} "
            else:
                if predicate == "alternativeName":
                    sentence += f", also known as {object_val} "
                elif predicate == "creatorOfDish":
                    sentence += f" originated from {object_val} "
                elif predicate == "creator":
                    sentence += f" created by {object_val} "
                elif predicate == "leader":
                    sentence += f" and its leader is {object_val} "
                elif predicate == "officialLanguage":
                    sentence += f" and the official language is {object_val} "
                elif predicate == "demonym":
                    sentence += f" and people are known as {object_val} "
                elif predicate == "currency":
                    sentence += f" and uses the currency {object_val} "
                elif predicate == "isPartOf":
                    sentence += f" which is part of {object_val} "
                elif predicate == "foundationPlace":
                    sentence += f" and was founded in {object_val} "
                elif predicate == "servingTemperature":
                    sentence += f" and is served {object_val} "
                elif predicate == "class":
                    sentence += f" which is a {object_val} "
                elif predicate == "carbohydrate":
                    sentence += f" with {object_val}g of carbohydrate "
                elif predicate == "fat":
                    sentence += f" and contains {object_val}g of fat "
                elif predicate == "year":
                    sentence += f" in the year {object_val} "
                elif predicate == "protein":
                    sentence += f" with {object_val}g of protein "
                elif predicate == "servingSize":
                    sentence += f" with a serving size of {object_val}g "
                elif predicate == "order":
                    sentence += f" which is a member of the {object_val} order "
                elif predicate == "family":
                    sentence += f" which belongs to the {object_val} family "
                elif predicate == "division":
                    sentence += f" which is a {object_val} division "
                else:
                    sentence += f" and its {predicate} is {object_val}."
                if triple != triples[-1]:
                    sentence += ", and "

    return sentence.strip() + "."

# EVOLVE-BLOCK-END