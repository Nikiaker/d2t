from benchmark_reader import Benchmark, Entry
from benchmark_reader import select_files, select_test_file
from dataclasses import dataclass
import os

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

def write_triples(triples: dict[str, PredicateData], predicates_path: str):
    for k, v in triples.items():
        example_triple = [triple for triple in v.sentences[0].triples if triple.predicate == k][0]
        txt = f"Predicate: {k} - Example triple: {example_triple.__str__()}"
        with open(predicates_path, "a", encoding="utf-8") as f:
            f.write(txt + "\n")

def extract_triples(predicates_path: str = "predicates.txt"):
    WEBNLG_DOMAIN = os.getenv(
        "WEBNLG_DOMAIN",
        "Airport",
    )

    WEBNLG_BASE_PATH = os.getenv(
        "WEBNLG_BASE_PATH",
        "./",
    )
    if not WEBNLG_BASE_PATH.endswith("/"):
        WEBNLG_BASE_PATH += "/"

    train_files = select_files(WEBNLG_BASE_PATH + "train")
    dev_files = select_files(WEBNLG_BASE_PATH + "dev")
    test_dir = WEBNLG_BASE_PATH + "test"
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

    category_entries  = [e for e in entries if e.category == WEBNLG_DOMAIN]

    print("Number of selected entries: ", len(category_entries))

    triples_dict: dict[str, PredicateData] = {}
    for entry in category_entries:
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
    write_triples(triples_dict, predicates_path)

if __name__ == "__main__":
    extract_triples()