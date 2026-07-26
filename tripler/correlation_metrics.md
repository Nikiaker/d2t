# Inter-Rater Correlation Metrics

When comparing scores given by an LLM-as-a-judge against scores given by a human
on the 1-5 ordinal scale, no single statistic fully captures agreement. The
`correlate_scores.py` script reports four complementary metrics, computed per
criterion and per overall variant. This document explains what each metric
measures and how it is calculated.

## Two independent judge tasks

To reduce bias, the judge splits the data-to-triples pipeline into two
independent evaluation tasks, each judged separately:

- **`text_*` (data &rarr; reference):** the judge sees the original structured
  data instance and the generated natural-language text, and scores how well
  the text represents the data. The triples are NOT shown, so the text judgment
  is not contaminated by information the triples might leak about the data.
- **`triples_*` (reference &rarr; triples):** the judge sees the
  natural-language reference text and the generated semantic triples, and
  scores how well the triples represent the text. The original data is NOT
  shown, so the triples are judged purely as a text-to-triples extraction
  rather than being re-grounded against the source.

Each task uses the same four criteria (`summary, completeness, faithfulness,
omissions`) with task-specific prompt wording scoped to the task's own input,
so each instance produces **eight scores**:
`text_summary, text_completeness, text_faithfulness, text_omissions,
triples_summary, triples_completeness, triples_faithfulness, triples_omissions`.

The "overall" variants are computed **per task** (never mixing the two tasks
together), so a cross-task pooled number does not conflate the two independent
judgments.

All metrics range from **-1 to +1**, where:

| value   | meaning                                            |
| ------- | -------------------------------------------------- |
| +1      | perfect positive association / perfect agreement   |
| 0       | no association (or agreement equal to chance)     |
| -1      | perfect negative association                       |

For the three correlation coefficients (Pearson, Spearman, Kendall), high
positive values mean the LLM and human tend to give high/low scores to the same
instances. For Quadratic Weighted Kappa, high positive values mean the two
raters agree beyond what would be expected by chance.

---

## 1. Pearson product-moment correlation (r)

Measures the strength and direction of the **linear** relationship between the
two raters' raw score vectors.

Given two score vectors `LLM = (x_1, ..., x_n)` and `Human = (y_1, ..., y_n)`,
Pearson's r is:

```
        sum_i (x_i - mean(x)) (y_i - mean(y))
r = -------------------------------------------------------------
    sqrt( sum_i (x_i - mean(x))^2 ) * sqrt( sum_i (y_i - mean(y))^2 )
```

- **Range**: [-1, 1]
- **Sensitivity**: captures how well `y = a*x + b` fits; sensitive to outliers
  and assumes interval-level data (scores are truly 1-5 with equal spacing).
- **When useful**: as a baseline; it is the most widely recognized number but is
  technically suboptimal for ordinal (1-5) data.
- Computed via `scipy.stats.pearsonr`. Undefined (returns NaN) when one rater's
  vector is constant.

## 2. Spearman rank correlation (rho)

Measures the strength and direction of the **monotonic** relationship between
the two raters, using the **ranks** of the scores rather than their raw values.

```
rho = Pearson( rank(x), rank(y) )
```

- **Range**: [-1, 1]
- **Sensitivity**: captures whether higher LLM scores correspond to higher
  human scores, regardless of the exact distance between score levels. Robust
  to non-linear-but-monotonic relationships and to outliers.
- **When useful**: this is the recommended headline correlation for ordinal
  data such as 1-5 Likert scores, because it depends only on the ordering of
  ratings, not on the assumption that the gap between "2" and "3" equals the
  gap between "4" and "5".
- Computed via `scipy.stats.spearmanr`. Ties are handled by assigning average
  ranks. Undefined (returns NaN) when one rater's vector is constant.

## 3. Kendall tau-b

Measures rank **concordance**: the difference between the number of
concordant and discordant pairs of observations, normalized by the total number
of comparable pairs. tau-b corrects for ties, which makes it appropriate for
rating scales with many repeated values (such as 1-5 across many instances).

For n observations, consider all `n*(n-1)/2` unordered pairs `(i, j)`:
- a pair is **concordant** if the two raters order the pair the same way
  (both LLM and human score instance i higher than j, or both lower);
- a pair is **discordant** if the two raters order the pair oppositely;
- a pair is **tied** if either rater gives i and j the same score.

```
           concordant - discordant
tau-b = ---------------------------------
         sqrt( (total - ties_x) * (total - ties_y) )
```

- **Range**: [-1, 1]
- **Sensitivity**: like Spearman it detects monotonic association, but it is
  based on pairwise agreement rather than the Pearson-of-ranks formulation,
  so it is usually smaller in magnitude and more conservative. It is
  particularly well-suited to small samples with many ties.
- **When useful**: Kendall's tau tends to be more interpretable as a
  probability-style measure (it is close to the difference between the
  probability that a random pair is concordant vs. discordant) and gives a
  stricter lower bound on the strength of association.
- Computed via `scipy.stats.kendalltau`.

## 4. Quadratic Weighted Cohen's Kappa (QW-k)

Cohen's kappa is a **chance-corrected** agreement coefficient: it compares the
observed agreement between the two raters to the agreement that would be
expected if the two raters assigned scores independently at random according to
their own marginal distributions.

The **weighted** variant is used for ordinal scales: disagreements by one
category cost less than disagreements by several categories. The **quadratic**
weighting scheme (the most common choice) penalizes larger disagreements
quadratically.

Let the score scale be `1..K` (here K = 5). Build the `K x K` confusion matrix
`O` where `O[i][j]` is the number of instances the LLM scored `i` and the human
scored `j`. Define quadratic weights:

```
            (i - j)^2
w[i,j] = 1 - ---------
            (K - 1)^2
```

So `w = 1` on the diagonal (perfect agreement), and decreases quadratically
away from it. Then:

- **Observed (weighted) agreement**:
  ```
  p_o = sum_{i,j} w[i,j] * O[i,j] / N
  ```
- **Expected (weighted) agreement by chance**:
  Let `a[i] = sum_j O[i,j] / N` and `b[j] = sum_i O[i,j] / N` be the
  rater marginals. Then:
  ```
  p_e = sum_{i,j} w[i,j] * a[i] * b[j]
  ```
- **Kappa**:
  ```
  kappa = 1 - (1 - p_o) / (1 - p_e)
  ```

- **Range**: typically [-1, 1], where 1 is perfect agreement, 0 is agreement
  exactly equal to chance, and negative values indicate agreement worse than
  chance.
- **Interpretation guide** (Landis & Koch, 1977 — conventional cut-offs):
  | kappa     | agreement       |
  | --------- | --------------- |
  | < 0.00    | poor            |
  | 0.00-0.20 | slight          |
  | 0.21-0.40 | fair            |
  | 0.41-0.60 | moderate        |
  | 0.61-0.80 | substantial     |
  | 0.81-1.00 | almost perfect  |
- **When useful**: this is the canonical inter-rater agreement statistic for
  ordinal rating scales. Unlike the three correlation coefficients above, it
  is **chance-corrected**: two raters who always give the same constant score
  (e.g. all 3s) will have kappa = 0 rather than a spuriously high value, and
  two raters who agree only because both happen to prefer the middle category
  will not score as high as two raters who agree on a wide spread of scores.
- Implemented in pure Python in `correlate_scores.py` (no scikit-learn
  dependency).

---

## Overall (cross-criterion) variants

The script reports four "overall" rows in addition to the eight per-criterion
rows — two per task (`text`, `triples`):

### Pooled (`overall_text (pooled)` / `overall_triples (pooled)`)
Concatenate the four criteria of one task across instances into a single long
vector per rater:
```
LLM_pooled  = (text_summary_1, text_completeness_1, ..., text_omissions_n)
Human_pooled = (text_summary_1, text_completeness_1, ..., text_omissions_n)
```
This treats each `(instance, criterion)` pair as an independent observation
(4N data points for N instances within one task) and computes the four metrics
once on this long vector. The two tasks are pooled **separately** so a single
cross-task number never conflates the data&rarr;text and text&rarr;triples
judgments.

### Per-instance mean (`overall_text (mean)` / `overall_triples (mean)`)
For each rater, average the four criterion scores of one task per instance to
obtain a "task-level overall quality per instance":
```
LLM_overall_i  = mean(text_summary_i, text_completeness_i, text_faithfulness_i, text_omissions_i)
Human_overall_i = mean(text_summary_i, text_completeness_i, text_faithfulness_i, text_omissions_i)
```
This reduces to N data points per task and measures how well the two raters
agree on which instances are good or bad within that task, abstracting away
per-criterion differences. The correlation coefficients (Pearson, Spearman,
Kendall) are computed on the floating-point means directly; Quadratic Weighted
Kappa is computed on the means rounded back to the nearest integer so that it
operates on the 1-5 confusion matrix.

---

## How `correlate_scores.py` uses these

- Reads two CSVs (`--llm` and `--human`) sharing the schema
  `instance_id, domain, input_data, generated_text, generated_triples,
   summary, completeness, faithfulness, omissions`.
- Matches rows by `instance_id` (warns on mismatches; uses the intersection).
- Drops any `(instance, criterion)` pair where either rater's cell is empty or
  non-integer, so a single missing score never invalidates the whole
  instance.
- For each criterion and for each overall variant, computes all four metrics.
- Prints a formatted table to the terminal and optionally writes a tidy
  long-form summary CSV via `--out-csv`.

Example output:
```
criterion                     N  Pearson r  Spearman p  Kendall t     QW-k
--------------------------------------------------------------------------
text_summary                100      0.979       0.981      0.962    0.973
text_completeness           100      1.000       1.000      1.000    1.000
text_faithfulness           100      1.000       1.000      1.000    1.000
text_omissions              100      1.000       1.000      1.000    1.000
triples_summary             100      0.951       0.949       0.934    0.944
triples_completeness        100      0.962       0.960       0.921    0.955
triples_faithfulness        100      0.973       0.971       0.940    0.966
triples_omissions           100      0.947       0.944       0.918    0.940
overall_text (pooled)       400      0.993       0.996      0.990    0.993
overall_text (mean)         100      0.998       0.981      0.964    1.000
overall_triples (pooled)    400      0.958       0.956       0.928    0.951
overall_triples (mean)      100      0.961       0.958       0.925    0.957
```

### Reading the output
- A high **Spearman rho** (closest to 1) indicates the LLM ranks instances
  similarly to the human, which is the most defensible single-number claim to
  make for 1-5 ordinal data.
- A high **Quadratic Weighted Kappa** indicates strong agreement beyond chance,
  with the quadratic weighting ensuring that being off by 3 points is treated
  as much worse than being off by 1 point.
- The four **overall** rows give per-task summaries:
  - `overall_text (pooled)` / `overall_text (mean)` summarize the
    data&rarr;text judgment; `overall_triples (*)` summarize the
    text&rarr;triples judgment. Comparing the two lets you see whether the
    LLM judge agrees with the human more on the text stage or the triples
    stage of the pipeline.
  - The pooled variant is sensitive to per-criterion disagreement, while the
    mean variant is sensitive to per-instance overall-quality agreement.

For a master thesis on LLM-driven data-to-text evaluation, **report all four
metrics per criterion** and highlight **Spearman rho** and **Quadratic Weighted
Kappa** as the most appropriate for the 1-5 ordinal scale.