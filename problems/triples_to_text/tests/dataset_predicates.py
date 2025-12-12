from benchmark_reader.benchmark_reader import Benchmark, Entry
from benchmark_reader.benchmark_reader import select_files, select_test_file
from dataclasses import dataclass

@dataclass
class TestTriple:
    subject: str
    predicate: str
    object: str
    example_texts: list[str]

@dataclass
class PredicateData:
    predicate: str
    triples: list[TestTriple]

def write_triples(triples: dict[str, PredicateData]):
    for k, v in triples.items():
        txt = f"Predicate: {k}\nExample text: {v.triples[0].example_texts[0]}"
        with open("predicates_airport.txt", "a", encoding="utf-8") as f:
            f.write(txt + "\n")


train_files = select_files("/home/nikiaker/Projects/studia/stop2/magisterka/d2t/problems/triples_to_text/tests/webnlg/release_v3.0/en/train")
dev_files = select_files("/home/nikiaker/Projects/studia/stop2/magisterka/d2t/problems/triples_to_text/tests/webnlg/release_v3.0/en/dev")
test_dir = "/home/nikiaker/Projects/studia/stop2/magisterka/d2t/problems/triples_to_text/tests/webnlg/release_v3.0/en/test"
test_file = select_test_file(test_dir, "rdf-to-text-generation-test-data-with-refs-en.xml")

train_benchmark = Benchmark()
dev_benchmark = Benchmark()
test_benchmark = Benchmark()
train_benchmark.fill_benchmark(train_files)
dev_benchmark.fill_benchmark(dev_files)
test_benchmark.fill_benchmark(test_file)

entries: list[Entry] = []
entries.extend(train_benchmark.entries)
entries.extend(dev_benchmark.entries)
entries.extend(test_benchmark.entries)

print("Number of entries: ", len(entries))

airport_entries  = [e for e in entries if e.category == "Airport" and e.size == "1"]

print("Number of selected entries: ", len(airport_entries))

triples_dict: dict[str, PredicateData] = {}
for entry in airport_entries:
    for triple_tuple in entry.get_triples_tuple_list():
        triple = TestTriple(*triple_tuple, example_texts=entry.get_lexs_list())
        if triple.predicate not in triples_dict:
            triples_dict[triple.predicate] = PredicateData(predicate=triple.predicate, triples=[triple])
        else:
            triples_dict[triple.predicate].triples.append(triple)

print("Number of unique predicates: ", len(triples_dict))
print("Done")
#write_triples(triples_dict)