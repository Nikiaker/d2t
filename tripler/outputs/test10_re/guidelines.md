Give an integer score from 1 (worst) to 5 (best) for each criterion. Judge only
the relationship between the source and the output. Do not use external
knowledge. Paraphrasing is acceptable when it preserves the source meaning.

# Summary
Evaluate whether the natural-language text is a concise, coherent summary of the original structured data instance. It
should avoid repeating the same concept with different words, be significantly
shorter than a detailed or repetitive structured data when possible, preserve the core
message, and function as a summary rather than a rewritten essay or a
disjointed list of facts.

- 5: The natural-language text is a clear and coherent summary. It
preserves the original structured data's core message without redundant restatement and does not
read like an essay or a disconnected list.
- 4: The natural-language text is a good summary and preserves the core message, but has minor
redundancy, slight unnecessary length, or a small organizational weakness.
- 3: The natural-language text is recognizably a summary, but is noticeably repetitive, too
verbose, list-like, or weakly organized; its main message remains usable.
- 2: The natural-language text is a poor summary: it substantially repeats or rewrites the
original structured data, is very verbose or disjointed, and represents the core message only
partly.
- 1: The natural-language text does not function as a summary. It is mostly irrelevant,
repetitive, disjointed, or fails to communicate the original structured data's core message.

# Faithfulness
Evaluate whether every claim in the natural-language text is directly supported by the
the original structured data instance and whether entities, relationships, values, qualifiers, and their
meaning are represented accurately. Penalize hallucinations, fabrications,
contradictions, and misinterpretations. Do not penalize information that is
merely omitted.

- 5: Every claim is grounded in the original structured data instance, and all represented facts preserve
the source's meaning. There are no hallucinations, contradictions, or
material distortions.
- 4: The natural-language text is fully usable and essentially faithful, with at most a minor
imprecision that does not change the meaning and no material unsupported
claim.
- 3: Most claims are grounded, but there is one material error or distortion,
or several minor unsupported or inaccurate claims.
- 2: There are multiple material errors, hallucinations, contradictions, or a
substantial misinterpretation of the original structured data.
- 1: the natural-language text is mostly ungrounded or contradicts the original structured data, so it cannot be
considered a reliable representation.

# Completeness
Evaluate whether the semantic triples include all main points, critical facts,
constraints, context, entities, relationships, values, and conclusions
from the output text and have no additional information that were not existent in the output text.
Judge coverage, not whether the semantic triples contain unsupported information.

- 5: Every main point and every critical fact, constraint, context element, and
conclusion needed to understand the natural-language reference text is represented in the semantic triples. No
important gap remains.
- 4: All main points and critical context are present, but one or a few
secondary, non-critical details are missing.
- 3: Most main points are present, but at least one important fact or context
element, or several secondary details, are missing.
- 2: Multiple main points or a critical constraint, context element, or
conclusion is missing, so the semantic triples give a substantially incomplete account.
- 1: Little relevant source information is represented, or the natural-language reference text's main
message is largely absent.

# Omissions
Evaluate what the semantic triples leave out. Lower the score when omissions remove critical
context, change the meaning, hide a major conclusion or constraint, or create
a misleading imbalance or bias.

- 5: Only redundant material is omitted.
No omission changes the meaning, hides important context, or introduces a
meaningful bias.
- 4: One or a few minor omissions exist, but the meaning and conclusions remain
intact and the selection of included information is not meaningfully biased.
- 3: An important but non-central detail, or enough supporting context to create
a mild imbalance, is omitted; the overall message remains understandable.
- 2: A critical context element, major conclusion, important constraint, or
representative point is omitted, changing the meaning or creating clear bias.
- 1: Extensive omissions distort the core message or make the output triples
misleading or one-sided; most important source information is absent.