from benchmark_reader.benchmark_reader import Benchmark
from benchmark_reader.benchmark_reader import select_files
from dataclasses import dataclass

def write_triples(triples: dict[str, str]):
    for k, v in triples.items():
        txt = f"Predicate: {k}\nExample text: {v}"
        with open("predicates_airport.txt", "a", encoding="utf-8") as f:
            f.write(txt + "\n")

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str
    example_text: str

b = Benchmark()
files = select_files("/home/nikiaker/Projects/studia/stop2/magisterka/d2t/problems/triples_to_text/tests/webnlg/release_v3.0/en/train")
b.fill_benchmark(files)

print("Number of entries: ", b.entry_count())

entry = b.entries[1000]
airport_entries  = [e for e in b.entries if e.category == "Airport" and e.shape == "(X (X))"]
print(entry.size)
print(entry.category)
print(entry.shape)
print(entry.shape_type)
print(entry.list_triples())
print(entry.get_triples_tuple_list())
print(entry.get_lexs_list())

triples = [Triple(*e.get_triples_tuple_list()[0], example_text=e.get_lexs_list()[0]) for e in airport_entries]
print(len(triples))

triples_dict: dict[str, str] = {}
for triple in triples:
    if triple.predicate not in triples_dict:
        triples_dict[triple.predicate] = triple.example_text

print("Done")
write_triples(triples_dict)