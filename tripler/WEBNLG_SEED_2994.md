# Seed 2994 WebNLG generation

The seed-2994 pipeline runs the domain-specific regularized-capacity Gemma
models directly. Each model emits one JSON object containing both a
natural-language reference and semantic triples. The output is then packaged
into the directory layout read by the WebNLG benchmark reader.

## Remote generation

On the PUT/SLURM machine, with `D2TPATH` exported:

```bash
bash "$D2TPATH/tripler/finetune/run_generate_webnlg_seed_2994.sh"
```

The default model paths are:

```text
$HOME/ft_models/gsmarena_gemma4_31b_regularized_capacity_merged
$HOME/ft_models/openweather_gemma4_31b_regularized_capacity_merged
$HOME/ft_models/owid_gemma4_31b_regularized_capacity_merged
$HOME/ft_models/wikidata_gemma4_31b_regularized_capacity_merged
```

Override `MODEL_DIR` when all tasks should use one model. Override
`OUTPUT_ROOT` and `WEBNLG_ROOT` to publish artifacts elsewhere.

The array has one task for every `domain x {dev,test}` pair. The generated
JSON files are written under `OUTPUT_ROOT/json/`. Packaged XML is written
under `WEBNLG_ROOT/{dev,test}/{1..7}triples/` with categories
`Gsmarena`, `Openweather`, `Owid`, and `Wikidata`.

Each category/split also has a report under
`WEBNLG_ROOT/generated_seed_2994_reports/`. Predictions with no text, no
triples, malformed triples, or more than seven triples are reported and not
included in the benchmark layout because the repository's reader only scans
the one- through seven-triple directories.

## Preparing evolution

After copying or symlinking the generated `dev` and `test` artifacts into the
repository's WebNLG release directory, prepare the four new domains
with:

```bash
cd "$D2TPATH/problems/triples_to_text"
python prepare_evolution.py --domains-file webnlg_domains_seed_2994.json
```

The existing `webnlg_domains.json` remains unchanged for the original WebNLG
experiments. Set `WEBNLG_DOMAIN` to one of the four new category names when
running evaluation or final testing.

To use the generated test entries with `final_test.py`, merge the per-size
files into a separate test file:

```bash
python "$D2TPATH/tripler/merge_webnlg_test_xml.py" \
  --generated-root "$OUTPUT_ROOT/webnlg/release_v3.0/en" \
  --base "$D2TPATH/problems/triples_to_text/tests/webnlg/release_v3.0/en/test/rdf-to-text-generation-test-data-with-refs-en.xml" \
  --output "$OUTPUT_ROOT/webnlg/release_v3.0/en/test/rdf-to-text-generation-test-data-with-refs-seed-2994.xml"
```

Run final testing with `WEBNLG_TEST_FILE=rdf-to-text-generation-test-data-with-refs-seed-2994.xml`.
