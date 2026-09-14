# Chapter 5 review comments

Source: `PUT_Dissertation_Template-chapter5&6.pdf`. This file contains only
Chapter 5 annotations. The exact changes below record the implemented revision.

## 1
**Comment:** "w takim razie tutaj od razu musisz uzasadnić dlaczego tę domenę wyjąłeś z eksperymentów"

**Involved section and involved text:** Section 5.1.1, Data Collection: "This distinction is important because ice hockey is included in the automatic pipeline results but is absent from the later $S_1$, $S_2$, $S_3$, and $S_4$ datasets."

**Proposition:** State that ice hockey was excluded from the later experimental tracks because collecting additional data through its API was prohibitively expensive. Keep the source-collection scope and the later four-domain scope distinct.

**Exact changes:**
`chapters/05-experiments.tex`: stated that the later tracks exclude ice hockey
because additional API collection was prohibitively costly.

## 2
**Comment:** "1. nie wiem po co to powtarzasz 2. nie wiem dlaczego to nie powinno być interpretowano jako 'ommision from the source collection' - przecież to jest pominięcie tej domeny? Poza tym: jeśli jednak wykorzystujesz tę domenę do jakichś eksperymentów to powinieneś ją opisać w tej wyliczance"

**Involved section and involved text:** Section 5.1.1, Data Collection: "The fifth domain, \emph{ice hockey}, is therefore included only in the automatic pipeline comparison. Its absence from the human evaluation, fine-tuning, and whole-system experiments should not be interpreted as an omission from the source collection."

**Proposition:** Replace "The four experimental datasets" with "The five source domains," add an ice-hockey description to the list, and state its automatic-pipeline-only scope there. Delete the repeated paragraph after the list.

**Exact changes:**
`chapters/05-experiments.tex`: renamed the list to the five source domains,
added ice hockey with its automatic-comparison-only scope, and removed the
repeated paragraph after the list.

## 3
**Comment:** "wprowadzasz notację, której nie używasz. Wprowadź ją w miejscu gdzie będziesz jej używać. Lub tutaj napisz że 'w dalszej części tekstu będziemy to oznaczać jako...' Natomiast - tak na szybko sprawdzając to nie wiem gdzie D jest użyte"

**Involved section and involved text:** Section 5.1.1, Data Collection: "Let $D = \{d_1, \dots, d_N\}$ denote the set of $N$ such instances extracted from the input JSON for a given domain."

**Proposition:** Delete the unused $D$ notation. It is not referenced elsewhere in the chapter and therefore does not improve the experimental description.

**Exact changes:**
`chapters/05-experiments.tex`: removed the unused $D = \{d_1, \dots, d_N\}$
notation.

## 4
**Comment:** "to jest ważna informacja która pozwala zrozumieć wcześniejsze wyliczenia = dałbym ją wcześniej i też opisałbym dokładnie pierwsze wyliczenie tj. 5 domains/datasets, 100 instances, 2 criteria - tak żeby było wiadomo skąd to się wzięło"

**Involved section and involved text:** Section 5.1.2, Experimental setup for pipelines: "The shared data-to-text evaluation requires $5 \times 100 \times 2 = 1{,}000$ judge calls. The three text-to-triples methods require $5 \times 100 \times 3 \times 2 = 3{,}000$ further calls, for 4,000 calls in total."

**Proposition:** Move the complete calculation before the criteria discussion: five domains times 100 instances gives 500 instances; two criteria give 1,000 shared data-to-text requests; three separately evaluated pipelines give 3,000 text-to-triples requests; total 4,000.

**Exact changes:**
`chapters/05-experiments.tex`: moved the 500-instance and 4,000-call calculation
before the transition criteria and showed the two component calculations.

## 5
**Comment:** "bardziej chodzi o to że także raportujesz inne metryki/statystyki opisowe. To brzmi jakbyś opisywał wyjście ze skryptu ewaluacyjnego"

**Involved section and involved text:** Section 5.1.2, Experimental setup for pipelines: "The evaluation output also contains descriptive statistics."

**Proposition:** Describe these values as supplementary descriptive characteristics reported alongside quality ratings, not as raw evaluator output. Clarify whether the predicate count is a distinct domain-level vocabulary count or an average per-instance count.

**Exact changes:**
`chapters/05-experiments.tex`: recast the values as supplementary descriptive
characteristics and defined predicates as distinct domain-level output vocabulary.

## 6
**Comment:** "jeśli tutaj wstawiasz tabelki, to musisz się tutaj do nich odnieść. Wyniki są przedstawione w tabeli x, coś innego w tabeli Y itd"

**Involved section and involved text:** Section 5.1.2, Experimental setup for pipelines: "The overall text and triples scores are calculated as the mean of the two criteria belonging to the corresponding transition," followed by the automatic pipeline result tables.

**Proposition:** Add a paragraph referring to Tables~\ref{tab:pipeline-text-results}, \ref{tab:pipeline-blueprint-triples-results}, \ref{tab:pipeline-text-first-triples-results}, and~\ref{tab:pipeline-catalog-triples-results}, and define `Overall` as the arithmetic mean of the two transition-specific criteria.

**Exact changes:**
`chapters/05-experiments.tex`: added explicit references to all four automatic
pipeline-result tables and retained the definition of `Overall`.

## 7
**Comment:** "musisz ustandaryzować wielkość tekstu w tabelkach w całej pracy"

**Involved section and involved text:** Section 5.1.3, Human evaluation for pipelines: Table 5.5, "Human evaluation of the shared data-to-text transition," including its table font sizing.

**Proposition:** Adopt one table-font policy for equivalent Chapter 5 tables. As a minimal first step, apply the selected human-evaluation table font consistently to Tables 5.5--5.8; later dense result tables should be redesigned or split rather than made inconsistently small.

**Exact changes:**
`chapters/05-experiments.tex`: applied `\small` consistently to the four
human-evaluation tables.

## 8
**Comment:** "2 miejsca po przecinku"

**Involved section and involved text:** Section 5.1.3, Human evaluation for pipelines: Table 5.6 average row, "\textbf{Average} & 4.525 & 3.825 & 4.175 \\".

**Proposition:** Round all human-evaluation averages to two decimal places, for example `4.53`, `3.83`, and `4.18` in the Blueprint table, and apply the same convention to the other human-evaluation tables.

**Exact changes:**
`chapters/05-experiments.tex`: rounded all human-evaluation averages to two
decimal places.

## 9
**Comment:** "asymetryczna? nie wiem o co chodzi"

**Involved section and involved text:** Section 5.1.3, Human evaluation for pipelines: "Human evaluation follows the same asymmetric rubric as automatic evaluation."

**Proposition:** Replace "asymmetric rubric" with an explicit statement that human evaluation uses summary and faithfulness for data-to-text, and unsupported additions and consequential omissions for text-to-triples, all on the same 1--5 scale as the automatic evaluation.

**Exact changes:**
`chapters/05-experiments.tex`: replaced the unexplained ``asymmetric rubric''
with the explicit task-specific criteria and common scale.

## 10
**Comment:** "tutaj chyba bym listę zrobił"

**Involved section and involved text:** Section 5.1.4, Correlation between LLM and human evaluation: "Four complementary statistics are reported."

**Proposition:** Present Pearson's $r$, Spearman's $\rho$, Kendall's $\tau$-b, and quadratic weighted Cohen's $\kappa$ as an itemized list, then retain a short common interpretation paragraph. Add primary methodological citations for the retained statistic definitions where needed.

**Exact changes:**
`chapters/05-experiments.tex`: converted the four statistic definitions into an
itemized list and retained the common interpretation paragraph.

## 11
**Comment:** "to nie jest jasne\n\nok, chyba rozumiem = ze polaczyles obserwacje z roznych kryteriow i potraktowales je jako 1 kolumne. Obawiam sie ze to jest bledne i wywalilbym to"

**Involved section and involved text:** Section 5.1.4, Correlation between LLM and human evaluation: "A \emph{pooled} text-to-triples result concatenates the additions and omissions score of every matched instance for each rater. With ten matched instances, this produces 20 paired criterion scores: additions and omissions for each instance."

**Proposition:** Remove the pooled 20-score aggregation and every corresponding `Pooled` table row. It concatenates additions and omissions from the same instance as though they were independent observations. Report each criterion separately and retain only an explicitly labelled supplementary per-instance aggregate if needed.

**Exact changes:**
`chapters/05-experiments.tex`: deleted the pooled explanation and all `Pooled`
rows from Table~`tab:judge-human-triples-correlation`.

## 12
**Comment:** "to nie jest overall jakość, to tylko mierzy oba typy halucynacji łącznie"

**Involved section and involved text:** Section 5.1.4, Correlation between LLM and human evaluation: "It answers whether the LLM and human agree about which complete instances are better or worse overall."

**Proposition:** Rename the per-instance aggregate to "Mean of additions and omissions" and state that it combines two text-to-triples semantic-error criteria. It must not be interpreted as overall instance, pipeline, or output quality.

**Exact changes:**
`chapters/05-experiments.tex`: renamed the remaining supplementary aggregate to
``Mean of additions and omissions'' and explicitly disclaimed any overall-quality
interpretation.

## 13
**Comment:** "w tekście bym to opisał albo chociaż zrobił listę konfiguracji + dodatł referencję do tabelki"

**Involved section and involved text:** Section 5.1.6, Training Configuration: Table 5.11 configuration entry "regularized\_capacity".

**Proposition:** Replace the short configuration paragraph with a concise description of all five QLoRA configurations and a reference to Table~\ref{tab:qlora-config}. Explain that `regularized_capacity` combines larger adapter capacity with more training, lower learning rate, longer warm-up, higher dropout, and weight decay; note that these are configuration-level rather than one-factor ablations.

**Exact changes:**
`chapters/05-experiments.tex`: expanded the configuration discussion, referenced
Table~`tab:qlora-config`, and described the five settings as configuration-level
comparisons rather than one-factor ablations.

## 14
**Comment:** "powtórzenie to już było na końcu poprzdniego punktu 5.1.5"

**Involved section and involved text:** Section 5.1.6, Training Configuration: "After training, the LoRA adapter weights are combined with the frozen base model weights to produce a standalone model."

**Proposition:** Delete the repeated adapter-merging paragraph. The preceding fine-tuning setup already explains that adapters are merged before evaluation.

**Exact changes:**
`chapters/05-experiments.tex`: removed the repeated adapter-merging paragraph.

## 15
**Comment:** Empty annotation artifact; the PDF contains no reviewer text.

**Involved section and involved text:** Section 5.1.6, Training Configuration: no text is selected by this zero-area PDF annotation.

**Proposition:** No action is proposed because this is a zero-area PDF annotation with no reviewer comment or selected text.

**Exact changes:**
No change; the annotation has no text or selected content.

## 16
**Comment:** "to jest bardzo dziwne formatowanie, że masz całą stronę pustą"

**Involved section and involved text:** Section 5.1.6, Training Configuration: "The merged model can be served by the same vLLM infrastructure as the base model and produces both a natural-language verbalization and the corresponding semantic triples in a single decode pass."

**Proposition:** Remove the repeated merging paragraph first and recompile. If excessive whitespace remains, adjust only the local float barrier after the training-configuration subsection; do not globally remove float barriers.

**Exact changes:**
`chapters/05-experiments.tex`: removed the repeated paragraph and its local
float barrier; layout is checked during compilation.

## 17
**Comment:** "tak jak wcześniej pisałęm, te tabelki nie są nigdzie opisane, ani nie ma do nich odnośników w tekście. Ogólnie to też ciężko jest porównywać wyniki skoro są one w osobnych tabelkach"

**Involved section and involved text:** Section 5.1.7, Evaluation of fine-tuned models: Table 5.12, "Base-model results on the held-out $S_2$ sets," and the following separate fine-tuning result tables.

**Proposition:** Replace the six separate configuration tables with one macro-average comparison table for the base model and five QLoRA configurations, plus at most one compact domain-level table if detailed reporting is required. Add in-text references and a short comparison of the leading text and triple metrics. Verify the missing OWID `baseline-1epoch` provenance before retaining that aggregate.

**Exact changes:**
`chapters/05-experiments.tex`: replaced six separate configuration tables with
one macro-average comparison table, added a textual comparison, and removed the
unverified domain-level detail. `chapters/06-discussion.tex` now references the
new table and no longer relies on removed domain-level rows.

## 18
**Comment:** "cytowanei"

**Involved section and involved text:** Section 5.2.1, WebNLG dataset and evaluation protocol: the introduction of "WebNLG."

**Proposition:** Cite WebNLG at its first mention, e.g. "the WebNLG benchmark~\cite{gardent-etal-2017-webnlg}," and remove the later duplicate citation if it no longer adds information.

**Exact changes:**
`chapters/05-experiments.tex`: cited WebNLG at first mention and removed the
later duplicate citation.

## 19
**Comment:** "trzeba napisać jaki model"

**Involved section and involved text:** Section 5.2.1, WebNLG dataset and evaluation protocol: "The baseline systems are a rule-based generator by Lango et al., a fine-tuned BART model, and a prompted language model."

**Proposition:** Identify the prompted baseline as the exact Gemma checkpoint, zero-shot prompt, and decoding configuration used for final testing. Describe BART as the precomputed output baseline from the Lango--Dušek work, cite that work and the original BART paper, and do not claim unavailable checkpoint or training details.

**Exact changes:**
`chapters/05-experiments.tex`: identified the zero-shot Gemma checkpoint,
temperature, and token limit; described BART only as retained precomputed output
from Lango--Du\v{s}ek, noted unavailable checkpoint provenance, and cited BART.
`bibliografia.bib`: added the BART reference.

## 20
**Comment:** "opisywałeś LLM-based metryki paragraf wcześniej. Te opisy powinny być razem dla spójności"

**Involved section and involved text:** Section 5.2.1, WebNLG dataset and evaluation protocol: the metric overview followed later by "The grammaticality, additions, and omissions judgments are performed with Gemma~4 31B IT."

**Proposition:** Merge the reference-based metrics, judge models, grammaticality/additions/omissions diagnostics, and descriptive statistics into one unified evaluation paragraph. State which model supplies each diagnostic and cite Themis at first mention.

**Exact changes:**
`chapters/05-experiments.tex`: combined reference metrics, judge models,
Gemma diagnostics, and descriptive statistics into one evaluation description;
added the Themis citation.

## 21
**Comment:** "zbyt duży skrót myślowy"

**Involved section and involved text:** Section 5.2.2, Evolution variants: "Uses Gemma~4 31B IT in non-reasoning mode for program generation."

**Proposition:** Define non-reasoning program generation as the Gemma configuration with `reasoning_effort: none`: optional high-reasoning generation is disabled and the model directly proposes a SEARCH/REPLACE mutation. State that this setting does not describe the separate fitness evaluator.

**Exact changes:**
`chapters/05-experiments.tex`: defined non-reasoning generation using
`reasoning_effort: none` and distinguished it from the fitness evaluator.

## 22
**Comment:** "nie pamiętam czy wcześniej opisywałęś jak wątki działają w twojej implementacji = ale jeśli nie, to bym to tutaj krótko skomentował"

**Involved section and involved text:** Section 5.2.2, Evolution variants: "The preceding mixed-model setup with four parallel evaluator threads."

**Proposition:** Replace "four parallel evaluator threads" with "four concurrent OpenEvolve worker processes." Briefly explain that each process independently selects a parent, requests a mutation, and evaluates one candidate, increasing throughput and allowing results to enter the database out of submission order. Cross-reference the Chapter 4 execution description.

**Exact changes:**
`chapters/05-experiments.tex`: replaced thread wording with concurrent worker
processes, described their asynchronous behavior, and cross-referenced the
OpenEvolve execution description in Chapter 4.

## 23
**Comment:** "w niektórych typach zaznaczasz ile iteracji, w innych nie = trochę nie spójnie. W ogóle nie wiem czy liczba interacji nie powinna być jakoś raportowana przy tabelce z wynikami, a tutaj skupić się tylko na ewaluowanych wariantach"

**Involved section and involved text:** Section 5.2.2, Evolution variants: "A 100-iteration mixed Gemma~4 31B run" and the inconsistent iteration counts across the variant list.

**Proposition:** Move iteration budgets and all execution settings to a variant-configuration table with columns for domains, iterations, fitness, inspirations, generation model, reasoning setting, and worker processes. The prose list should describe only the factor varied. Audit submitted configurations and logs before retaining the current mixed-model identity and 100-iteration claims.

**Exact changes:**
`chapters/05-experiments.tex`: added Table~`tab:surface-variant-configurations`
for domains, iterations, fitness, inspirations, generation setting, and workers;
the prose now describes factors rather than repeating budgets. The retained
mixed-model snapshot names Gemma and GLM-5.2, but cannot be linked to a specific
final-test run, so the table does not claim a more specific identity.

## 24
**Comment:** "tutaj warto by też potem zaraportować wyniki dla 100 iteracji, dla lepszego porównania."

**Involved section and involved text:** Section 5.2.2, Evolution variants: "A 500-iteration Gemma~4 31B run in which every program-generation call uses high-reasoning generation."

**Proposition:** Recover the 100-iteration checkpoints or completed outputs for high-reasoning Gemma and evaluate them with the same held-out final-test protocol. Add the resulting 100-iteration comparison only after those results are available.

**Exact changes:**
No 100-iteration fully high-reasoning Gemma checkpoint, best program, or
final-test output is retained in the repository. No comparison was added, and
the zero-filled high-reasoning result table was removed rather than reported.

## 25
**Comment:** "nie wstawiałbym linii po każdym datasecie + wcześniejsza uwaga o jednolitym rozmiarze czcionek"

**Involved section and involved text:** Section 5.2.3, Evolution results: the row macro "\newcommand{\surfacetail}[6]{#1 & #2 & #3 & #4 & #5 & #6 \\\hline}" and the surface-realization result-table formatting.

**Proposition:** Remove `\hline` from the data-row macros and keep rules only after headers, before averages, and at table ends. Apply the chosen consistent table font and avoid combining `\tiny` with `\resizebox` where possible.

**Exact changes:**
`chapters/05-experiments.tex`: removed row-level `\hline` commands from surface
result macros, retained section rules, used `\scriptsize` consistently in these
dense tables, and removed the zero-filled configured-result tables.

## 26
**Comment:** "rozumiem że tutaj jeszcze do uzupełnienia"

**Involved section and involved text:** Section 5.2.3, Evolution results: the first result table's trailing zero-valued descriptive-statistic fields, for example "\surfacerow{Airport}{...}{0}{0}{0}{0}".

**Proposition:** Remove the incomplete columns in Initial BLEU-based evolution variant with one inspiration.

**Exact changes:**
`chapters/05-experiments.tex`: hid the incomplete descriptive-statistic columns
from the initial evolution table instead of displaying placeholder zeroes.

## 27
**Comment:** "znów masz pustą stronę praktycznie. Te wszystkie tabelki musza miec odniesienie w tekscie i krotki opis"

**Involved section and involved text:** Section 5.2.4, Baseline systems: "The average is calculated over the available domain results for each baseline," followed by the baseline table.

**Proposition:** Add a textual introduction, table reference, and short interpretation for the baseline results. Correct the swapped word-count and character-count values for BART and the LLM prompt in both baseline tables; the corrected word counts are the smaller values and character counts the larger values.

**Exact changes:**
`chapters/05-experiments.tex`: added a table reference and interpretation for
the baseline results; corrected the swapped BART and LLM-prompt word and
character counts in both baseline tables.

## 28
**Comment:** "to wydaje się słabym argumentem, bo w sumie to są statystyki które ty liczysz. CHyba bym wywalił to zdanie i nie uzasadniał"

**Involved section and involved text:** Section 5.2.5, Three-domain comparison: "The all-domain initial variant is omitted because descriptive statistics were not reported for that run."

**Proposition:** Delete the weak justification for omitting the all-domain variant. State only the scope of the final three-domain comparison and include only complete, comparable variants; add further variants only after their final-test results are recovered.

**Exact changes:**
`chapters/05-experiments.tex`: removed the descriptive-statistics justification;
the three-domain comparison now states only its scope and completeness criterion.

## 29
**Comment:** "dodałbym (See Sec. XX)"

**Involved section and involved text:** Section 5.3.1, Data construction: "The raw instances in both collections are processed with the \emph{regularized capacity} fine-tuned Gemma~4 model from the preceding fine-tuning experiments."

**Proposition:** Add a cross-reference to the fine-tuning configuration and regularized-capacity result table. Describe this model as a fixed upstream choice for the planned whole-system protocol, not as the best configuration on every reported metric.

**Exact changes:**
Superseded by the whole-system revision: no fixed upstream model is claimed for
an experiment that was not performed. The stage-level regularized-capacity result
remains available in Table~`tab:finetune-results`.

## 30
**Comment:** "trzeba napisać które"

**Involved section and involved text:** Section 5.3.2, Evolution and evaluation protocol: "For each domain, the selected best-working OpenEvolve variant is run using the $S_3$ collection."

**Proposition:** Remove the unperformed whole-system result table and replace the completed-experiment wording with a clearly labelled planned protocol. State that no best-working variant or domain-specific program was selected, and present the planned configuration grid only if it remains useful. Reconcile this section with Chapters 6 and 7, which state that the experiment was not performed.

**Exact changes:**
`chapters/05-experiments.tex`: replaced completed-experiment wording and the
zero-filled whole-system table with a clearly labelled statement that the
evaluation was not performed and that no collections, variant selection,
programs, or scores are reported. This now agrees with Chapters 6 and 7.

## 31
**Comment:** Empty annotation artifact; the PDF contains no reviewer text.

**Involved section and involved text:** Section 5.3.2, Evolution and evaluation protocol: no text is selected by this zero-area PDF annotation.

**Proposition:** No action is proposed because this is a zero-area PDF annotation with no reviewer comment or selected text. During the later whole-system revision, also verify the claimed $S_4$ instance counts before reporting them.

**Exact changes:**
No change; the annotation has no text or selected content. The unperformed
whole-system revision removes the unsupported $S_4$ count claim.
