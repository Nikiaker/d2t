from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

# EVOLVE-BLOCK-START

def predict(triples: list[Triple]) -> str:
    sentence = ""
    details = []
    for triple in triples:
        if triple.predicate == "architecturalStyle":
            details.append(f"{triple.subject} is built in {triple.object} style")
        elif triple.predicate == "buildingStartDate":
            details.append(f"Construction of {triple.subject} started in {triple.object}")
        elif triple.predicate == "completionDate":
            details.append(f"{triple.subject} was completed in {triple.object}")
        elif triple.predicate == "floorCount":
            details.append(f"{triple.subject} has {triple.object} floors")
        elif triple.predicate == "location":
            details.append(f"{triple.subject} is located in {triple.object}")
        elif triple.predicate == "cost":
            details.append(f"The cost of {triple.subject} was {triple.object}")
        elif triple.predicate == "floorArea":
            details.append(f"{triple.subject} has a floor area of {triple.object}")
        elif triple.predicate == "owner":
            details.append(f"{triple.subject} is owned by {triple.object}")
        elif triple.predicate == "formerName":
            details.append(f"{triple.subject} was formerly known as {triple.object}")
        elif triple.predicate == "height":
            details.append(f"The height of {triple.subject} is {triple.object} meters")
        elif triple.predicate == "buildingType":
            details.append(f"{triple.subject} is a {triple.object}")
        elif triple.predicate == "developer":
            details.append(f"{triple.subject} was developed by {triple.object}")
        elif triple.predicate == "tenant":
            details.append(f"{triple.subject}'s tenant is {triple.object}")
        elif triple.predicate == "isPartOf":
            details.append(f"{triple.subject} is part of {triple.object}")
        elif triple.predicate == "country":
            details.append(f"{triple.subject} is located in {triple.object}")
        elif triple.predicate == "currentTenants":
            details.append(f"Current tenants of {triple.subject} include {triple.object}")
        elif triple.predicate == "address":
            details.append(f"The address of {triple.subject} is {triple.object}")
        elif triple.predicate == "inaugurationDate":
            details.append(f"{triple.subject} was inaugurated on {triple.object}")
        else:
            if triple.predicate == "leader":
                details.append(f"The leader of {triple.subject} is {triple.object}")
            elif triple.predicate == "origin":
                details.append(f"{triple.subject} originates from {triple.object}")
            elif triple.predicate == "birthPlace":
                details.append(f"{triple.subject} was born in {triple.object}")
            elif triple.predicate == "architect":
                details.append(f"{triple.object} was the architect of {triple.subject}")
            elif triple.predicate == "keyPerson":
                details.append(f"{triple.object} is a key person at {triple.subject}")
            else:
                details.append(f"{triple.subject} {triple.predicate} {triple.object}")

    if details:
        sentence = ""
        combined_details = []
        i = 0
        while i < len(details):
            detail = details[i]
            if "location" in detail and i + 1 < len(details) and "country" in details[i + 1] and i + 2 < len(details) and "capital" in details[i+2]:
                location_detail = detail
                country_detail = details[i + 1]
                capital_detail = details[i+2]
                combined_detail = f"{location_detail.split('is located in ')[1]} which is in {country_detail.split('is located in ')[1]}, where the capital is {capital_detail.split('capital ')[1]}"
                combined_details.append(combined_detail)
                i += 3
            elif "location" in detail and i + 1 < len(details) and "country" in details[i + 1]:
                location_detail = detail
                country_detail = details[i + 1]
                combined_detail = f"{location_detail.split('is located in ')[1]} which is in {country_detail.split('is located in ')[1]}"
                combined_details.append(combined_detail)
                i += 2
            else:
                combined_details.append(detail)
                i += 1
        sentence = ", ".join(combined_details) + "."

    return sentence

# EVOLVE-BLOCK-END