from benchmark_reader.benchmark_reader import Benchmark
from benchmark_reader.benchmark_reader import select_files
from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

b = Benchmark()
files = select_files("/home/nikiaker/Projects/studia/stop2/magisterka/d2t/problems/triples_to_text/tests/webnlg/release_v3.0/en/train")
b.fill_benchmark(files)

print("Number of entries: ", b.entry_count())

entry = b.entries[1000]
print(entry.size)
print(entry.category)
print(entry.shape)
print(entry.shape_type)
print(entry.list_triples())
print(entry.get_triples_tuple_list())
print(entry.get_lexs_list())

testset = [(e.get_triples_tuple_list()[0], e.get_lexs_list()[0]) for e in b.entries]
testset = [(Triple(*t[0]), t[1]) for t in testset]

print(f"Triple: ({entry.list_triples()[0]})\nText: {entry.get_lexs_list()[0]}")

for e in b.entries[:100]:
    txt = f"Triple: ({e.list_triples()[0]})\nText: {e.get_lexs_list()[0]}"
    with open("triples_texts.txt", "a", encoding="utf-8") as f:
        f.write(txt + "\n")