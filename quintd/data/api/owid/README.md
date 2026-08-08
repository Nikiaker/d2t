# OWID data source for Quintd

This directory fetches two datasets from the [Our World in Data (OWID)](https://ourworldindata.org) catalog and emits per-country, per-indicator CSV series used by `generate_dataset.py`:

1. **COVID** — 5 indicators (`new_cases_smoothed_per_million`, `new_tests_smoothed_per_thousand`, `people_vaccinated_per_hundred`, `reproduction_rate`, `positive_rate`), one row per country × date.
2. **Life expectancy** — the `life_expectancy_0` column, one row per country × year.

## API: owid-catalog 1.x

This module was migrated from the legacy `owid.catalog.find()` / `.load()` API (removed in `owid-catalog` 1.0) to the new `Client().tables.search(...)` / `TableResult.fetch()` API. See upstream changelog entry: *"`catalog.find()` deprecated in favor of `Client().tables.search()`"* (v1.0.0).

`requirements.txt` pins `owid-catalog>=1.0` to prevent a stale 0.4.x install from re-introducing the removed API.

### How the new API is used

```python
from owid.catalog import Client
client = Client()                                     # module-level singleton via _get_client()

# COVID
results = client.tables.search(
    table="covid", match="exact",
    channel="garden", namespace="owid",
)
table = results[0].fetch()                            # owid.catalog.Table (pandas-like)
countries = table.groupby("location")                 # groupby still works

# Life expectancy — needs the version that has the 'life_expectancy_0' column
results = client.tables.search(
    table="life_expectancy", match="exact",
    channel="garden", namespace="demography", dataset="life_expectancy",
)
for r in results:                                     # results come back in version-desc order;
    tb = r.fetch()                                    # probe each one for the needed column
    if "life_expectancy_0" in tb.columns:
        table = tb; break
```

### Why these specific channel/namespace/dataset names

These were **derived empirically by live-probing the catalog** at migration time (not from the legacy 0.4.x code, which used a generic `catalog.find("covid")` call). The legacy order/columns no longer match — the only robust way to pin them is the explicit queries above plus, for `life_expectancy`, a per-result column probe.

| Dataset | Search query | Catalog hit (verified Aug 2026) | Key columns |
|---|---|---|---|
| COVID | `table="covid", channel="garden", namespace="owid"` | 1 result, dataset `covid` (namespace `owid`, version `latest`) | `location` (group-by key, index level 0), `date` (index level 1), `new_cases_smoothed_per_million`, `new_tests_smoothed_per_thousand`, `people_vaccinated_per_hundred`, `reproduction_rate`, `positive_rate` |
| Life expectancy | `table="life_expectancy", channel="garden", namespace="demography", dataset="life_expectancy"` | 3 versions — `2025-10-22`, `2023-10-09`, `2024-12-03` — only `2023-10-09` has the `life_expectancy_0` column today | `country` (group-by key, index level 0), `year` (index level 1), `life_expectancy_0` |

### Catalog drift / maintenance

The OWID catalog is re-indexed periodically and dataset versions rotate. If the current pinned version stops having the expected column:

- **COVID** — `results[0].fetch()` would raise `KeyError` on a missing column. The 5 columns named in `extract_covid()` are core COVID-19 metrics and are unlikely to disappear, but if they do, update the column list in `extract_covid()` and the corresponding metadata JSON file in `metadata/`.
- **Life expectancy** — `extract_expectancy()` probes each returned version for `life_expectancy_0` and raises a diagnostic `RuntimeError("No life_expectancy table has the 'life_expectancy_0' column")` if none matches. At that point a newer (or older) demography version needs to be added to the probe, or the column name needs updating alongside `metadata/life_expectancy_0.json`.

### Metadata sidecars

The `metadata/` directory contains one JSON per indicator (`new_cases_smoothed_per_million.json`, `people_vaccinated_per_hundred.json`, `reproduction_rate.json`, `positive_rate.json`, `new_tests_smoothed_per_thousand.json`, `life_expectancy_0.json`) with `title`, `description`, and `unit` fields. `preprocess()` prepends these as a header to each CSV before shuffling and splitting. These were authored against the 0.4.x column names and **do not need updating** — the migrated code fetches the same columns by the same names.

### Output format

`generate_dataset(...)` writes:
- `fetched/<dev|test>/<column>-<country>.csv` — raw per-(country, indicator) DataFrames (transient; re-created each run).
- `<out_dir>/<dev|test>/<i>-<column>-<country>.csv` — final sharded CSVs with a metadata header, ready for input to the tripler pipeline.

Since COVID alone yields ~1000 (country, indicator) pairs and life expectancy adds ~260 more, a single run comfortably exceeds `-n 1000` (the script picks `n_examples * 2` random pairs and splits dev/test). No multi-page looping is needed for this domain — unlike `ice_hockey`'s single-date cap.