from benchmark_reader.benchmark_reader import Benchmark, Entry
from benchmark_reader.benchmark_reader import select_files, select_test_file
from dataclasses import dataclass

@dataclass
class TestTriple:
    subject: str
    predicate: str
    object: str

    def __str__(self):
        return f"({self.subject} | {self.predicate} | {self.object})"

@dataclass
class TestSentence:
    triples: list[TestTriple]
    example_texts: list[str]

@dataclass
class PredicateData:
    predicate: str
    sentences: list[TestSentence]

def write_triples(triples: dict[str, PredicateData]):
    for k, v in triples.items():
        example_triple = [triple for triple in v.sentences[0].triples if triple.predicate == k][0]
        txt = f"Predicate: {k} - Example triple: {example_triple.__str__()}"
        with open("predicates_multiple_airport.txt", "a", encoding="utf-8") as f:
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

airport_entries  = [e for e in entries if e.category == "Airport"]

print("Number of selected entries: ", len(airport_entries))

triples_dict: dict[str, PredicateData] = {}
for entry in airport_entries:
    triples = [TestTriple(*triple) for triple in entry.get_clean_triples_tuple_list()]
    example_texts = entry.get_lexs_list()
    test_sentence = TestSentence(triples=triples, example_texts=example_texts)

    for test_triple in triples:
        if test_triple.predicate not in triples_dict:
            triples_dict[test_triple.predicate] = PredicateData(predicate=test_triple.predicate, sentences=[test_sentence])
        else:
            triples_dict[test_triple.predicate].sentences.append(test_sentence)

print("Number of unique predicates: ", len(triples_dict))
print("Done")
write_triples(triples_dict)