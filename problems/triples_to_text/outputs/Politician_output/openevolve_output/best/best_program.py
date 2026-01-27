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
        if triple.predicate == "birthDate":
            sentence += f"{triple.subject} was born on {triple.object}. "
        elif triple.predicate == "birthPlace":
            sentence += f"{triple.subject} was born in {triple.object}. "
        elif triple.predicate == "deathDate":
            sentence += f"{triple.subject} died on {triple.object}. "
        elif triple.predicate == "deathPlace":
            sentence += f"{triple.subject} died in {triple.object}. "
        elif triple.predicate == "nationality":
            sentence += f"{triple.subject} is of {triple.object} nationality. "
        elif triple.predicate == "office":
            sentence += f"{triple.subject} held the office of {triple.object}. "
        elif triple.predicate == "party":
            sentence += f"{triple.subject} was a member of the {triple.object} party. "
        elif triple.predicate == "country":
            sentence += f"{triple.subject} is from {triple.object}, "
        elif triple.predicate == "capital":
            sentence += f"{triple.object} is the capital of {triple.subject}, "
        else:
            if triple.predicate == "successor":
                sentence += f"{triple.subject} was succeeded by {triple.object}. "
            elif triple.predicate == "predecessor":
                sentence += f"{triple.subject} succeeded {triple.object}. "
            elif triple.predicate == "inOfficeWhileVicePresident":
                sentence += f"{triple.subject} was in office while {triple.object} was Vice President. "
            elif triple.predicate == "inOfficeWhilePrimeMinister":
                sentence += f"{triple.subject} was in office while {triple.object} was Prime Minister. "
            elif triple.predicate == "inOfficeWhilePresident":
                sentence += f"{triple.subject} was in office while {triple.object} was President. "
            elif triple.predicate == "battle":
                sentence += f"{triple.subject} fought in the {triple.object}. "
            else:
                if triple.predicate == "region":
                    sentence += f"{triple.subject} is from the {triple.object} region. "
                elif triple.predicate == "militaryBranch":
                    sentence += f"{triple.subject} served in the {triple.object}. "
                elif triple.predicate == "language":
                    sentence += f"{triple.object} is spoken in {triple.subject}. "
                elif triple.predicate == "currency":
                    sentence += f"The currency of {triple.subject} is {triple.object}. "
                elif triple.predicate == "ethnicGroup":
                    sentence += f"{triple.subject} is home to the {triple.object} ethnic group. "
                elif triple.predicate == "religion":
                    sentence += f"{triple.subject} practices {triple.object}. "
                elif triple.predicate == "affiliation":
                    sentence += f"{triple.subject} is affiliated with {triple.object}. "
                elif triple.predicate == "leader":
                    sentence += f"{triple.subject}'s leader is {triple.object}. "
                elif triple.predicate == "largestCity":
                    sentence += f"{triple.object} is the largest city in {triple.subject}. "
                elif triple.predicate == "officialLanguage":
                    sentence += f"{triple.object} is an official language of {triple.subject}. "
                elif triple.predicate == "award":
                    sentence += f"{triple.subject} was awarded the {triple.object}. "
                elif triple.predicate == "trainerAircraft":
                    sentence += f"{triple.subject} uses {triple.object} as a trainer aircraft. "
                elif triple.predicate == "activeYearsStartDate":
                    sentence += f"{triple.subject}'s active years began on {triple.object}. "
                elif triple.predicate == "activeYearsEndDate":
                    sentence += f"{triple.subject}'s active years ended on {triple.object}. "
                elif triple.predicate == "militaryRank":
                    sentence += f"{triple.subject} held the military rank of {triple.object}. "
                elif triple.predicate == "serviceStartYear":
                    sentence += f"{triple.subject}'s military service began in {triple.object}. "
                elif triple.predicate == "numberOfVotesAttained":
                    sentence += f"{triple.subject} attained {triple.object} votes. "
                else:
                    if i > 0 and triples[i-1].subject == triple.subject:
                        sentence += f" and {triple.predicate} is {triple.object}."
                    else:
                        sentence += f"{triple.subject} {triple.predicate} is {triple.object}."
    return sentence

# EVOLVE-BLOCK-END