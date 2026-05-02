# 2026-04-29 — Reverification of Chapters 2 to 7

Append-only log of every fix applied during the cross-chapter
reverification pass that accompanied drafting Chapter 7
(Evaluation). Updates rather than duplicates the prior
`verification.md` (literature review audit, 2026-04 earlier).

---

## Scope

- Chapters 2 (Background), 3 (LiteratureReview), 4 (Specification),
  5 (Design), 6 (Implementation), 7 (Evaluation, newly drafted).
- Phases run: data-fact reconciliation, Trait 5 traceability, A++
  Trait 1-5 audit, humanizer-style sweep, word-count budget.
- Phases out of scope for this pass: Trait 6 (Conclusion) and
  Trait 7 (LSESP) because both chapters are still stubs.

---

## Phase 1: Data-fact reconciliation

### Fixed

- **Test count.** Implementation.tex stated "more than 400 test
  functions" in three places (`sec:impl-layout` summary, `sec:impl-testing`
  body, `sec:impl-summary` forward bridge).
  `pytest --collect-only -q tests/` reports `531 tests collected`.
  Updated all three sites to `\texttt{531}`. The "twelve files"
  count was already correct (`ls tests/test_*.py | wc -l = 12`).
- **`pandas` dependency.** Implementation.tex listed `pandas` in the
  runtime dependency recap but `requirements.txt` did not include
  it; `src/reporting.py` does `import pandas as pd`. Added `pandas`
  to `requirements.txt` between `seaborn` and `click` to match what
  the report claims and what the code actually imports.
- **`chap:conclusion` label.** Evaluation.tex references
  `Chapter~\ref{chap:conclusion}` from `\S\ref{sec:eval-rq2-cost}`
  and `\S\ref{sec:eval-synthesis}`; Conclusion.tex had no `\label`.
  Added `\label{chap:conclusion}` directly under the chapter
  heading.

### Verified consistent (no fix needed)

- Document count is uniformly 40 across Specification, Design,
  Implementation, Evaluation. The `5 verified` wording in
  `CONTEXT.md` and `SPEC.md` (project notes, not the report) did
  not propagate into the dissertation chapters.
- Two-page vision cap is consistently described in Design
  (`\S\ref{sec:design-pipeline}` modality branch) and Evaluation
  (`\S\ref{sec:eval-procedure}`, `\S\ref{sec:eval-rq2-cost}`,
  `\S\ref{sec:eval-failures-modality}`,
  `\S\ref{sec:eval-alternatives-allpages}`,
  `\S\ref{sec:eval-validity-internal}`,
  `\S\ref{sec:eval-limitations}`). Source of truth verified at
  `src/pipeline.py:147` (`vision_images = images[:2]`).
- Diagnosis heuristic is correctly described as substring-only in
  Specification (`\S\ref{sec:spec-evaluation}`), Design
  (`\S\ref{sec:design-evalframework-diagnosis}`), Implementation
  (`\texttt{evaluation.py}` references), and Evaluation
  (`\S\ref{sec:eval-failures-critique}`).
- H1, H2, H3 wording in Specification's `\S\ref{sec:spec-objectives}`
  is consistent with the falsification clauses asserted in
  Evaluation `\S\ref{sec:eval-rq1-aggregate}`,
  `\S\ref{sec:eval-rq2-cost}`, and `\S\ref{sec:eval-rq3-interaction}`.
- Diagnosis-heuristic counts (16/18 for Sonnet/OCR; 29/27 for
  GPT-4o/OCR) computed by summing `failure_type` across each run's
  `documents/*/diagnosis.json`. The 34/56 totals match
  `null_analysis` math: total = denominator x (1 - accuracy).

### Known residual (out of scope here)

- `google-generativeai` is in `requirements.txt` but is not used by
  any module under `src/`. Gemini appears only as related work in
  the literature review, not as an experimental provider. Treating
  this as project hygiene rather than a report claim; either remove
  the line from `requirements.txt` or add a Gemini provider stub
  before submission. Recommendation: remove, since shipping unused
  optional dependencies inflates install footprint.
- `verification.md` (prior pass) lists five orphan `references.bib`
  entries (`gemini2024gemini15`, `levenshtein1966`, `liu2024ocrbench`,
  `tam2024format`, `unstructured2026parsing`). Pruning is a
  pre-submission task, not a content correction.

---

## Phase 2: Trait 5 traceability

Five major design decisions spot-checked end to end. The chain
required is: literature gap → numbered requirement → design choice
with named alternative → implementation site → test → evaluation
result.

| Decision | LR gap | Requirement | Design | Implementation | Test | Evaluation |
|----------|--------|-------------|--------|----------------|------|------------|
| LLM-mediated extraction over per-issuer templates | `\S\ref{sec:lr-gap}` synthesis insight | ER1, FR5 | `\S\ref{sec:design-decisions}` modality boundary; `\S\ref{sec:design-pipeline-preproc}` | `src/pipeline.py` LLM dispatch | `tests/test_pipeline.py` | `\S\ref{sec:eval-alternatives-templates}` |
| Two providers via registry abstraction | `\S\ref{sec:lr-textmode}` provider asymmetry | ER7 | `\S\ref{sec:design-components-llm}` ABC + registry | `src/llm/registry.py`, `openai_provider.py`, `anthropic_provider.py` | `tests/test_llm.py` | `\S\ref{sec:eval-rq3}` |
| Two-page vision baseline | scope `\S\ref{sec:spec-scope}` cost framing | scope decision | `\S\ref{sec:design-pipeline}` modality branch | `src/pipeline.py:147` | `tests/test_pipeline.py` vision branch | `\S\ref{sec:eval-rq2-cost}`, `\S\ref{sec:eval-failures-modality}`, `\S\ref{sec:eval-alternatives-allpages}` |
| Null-aware four-class taxonomy | `\S\ref{sec:lr-eval}` null-handling gap | ER6 | `\S\ref{sec:design-evalframework}` | `src/evaluation.py` `compare_field` | `tests/test_evaluation.py` | `\S\ref{sec:eval-headline}`, `\S\ref{sec:eval-rq3-orthogonal}` |
| Disk-mediated decoupling for resume + audit | reproducibility | NFR4 | `\S\ref{sec:design-execution}` | `src/pipeline.py` per-doc persistence; `cli.py` resume | `tests/test_pipeline.py` resume tests | `\S\ref{sec:eval-procedure}`, `\S\ref{sec:eval-traceability}` |

All five chains intact. ER1-ER7 propagate across all chapters; the
requirements-traceability table at `\S\ref{sec:eval-traceability}`
closes the chain to evidence in this evaluation.

---

## Phase 3: A++ Trait audit (Traits 1-5)

| Trait | Status | Notes |
|-------|--------|-------|
| 1: Introduction wider-to-specific | **Open** | Introduction body in `report.tex` is the placeholder boilerplate (`"This is one of the most important components of the report. It should begin..."`). Needs writing. The Trait-1 arc (informatics → document understanding → multilingual extraction → modality choice → this dissertation's contribution) is not yet on the page. Until it is, A++ Trait 1 is unmet. |
| 2: LR synthesis insight | **Met** | `\S\ref{sec:lr-gap}` states "no published study simultaneously isolates the reasoning engine, varies the LLM provider factorially, reports per-stage cost and latency, and applies a null-aware evaluation taxonomy on a multilingual out-of-distribution document class. This synthesis insight is stated by no single paper cited above". |
| 3: Ambitious + executed | **Met** | 2,700 lines runtime Python, 531 tests across 12 files, 4 conditions x 40 documents = 160 extractions, 4 languages, 2 providers, full reproducibility artefacts, four-bucket failure-attribution refinement. |
| 4: Evaluation covers alternative designs | **Met** | Chapter 7 `\S\ref{sec:eval-alternatives}` has five subsections, one per alternative rejected in `\S\ref{sec:design-decisions}` (templates, fine-tuned encoder-decoder, ensemble, single-modality, full-page vision), each with empirical evidence rather than intuition. |
| 5: Traceability | **Met** | Phase 2 above. |

Traits 6 (Conclusion learnings + predictions) and 7 (LSESP all
dimensions + domain-specific) are not in scope here because
ProfessionalIssues.tex (77 words, stub) and Conclusion.tex (128
words, stub) are not yet drafted. Both must be written before
submission. The Evaluation chapter's `\S\ref{sec:eval-synthesis}`
already lists five transferable findings the Conclusion can
promote into Trait 6 statements.

---

## Phase 4: Humanizer-style sweep (Chapters 2 to 7)

Patterns scanned: emojis, AI vocabulary (`testament`, `showcasing`,
`nestled`, `at its core`, `delve`, `leverage`, `myriad`, `plethora`,
`comprehensive`, `tapestry`, `vibrant`, `journey`, `realm`),
`-ing` analytical chains, "It's not just X, it's Y", filler phrases
(`in order to`, `due to the fact`, `it is worth noting`, `going
forward`), generic conclusions (`the future looks bright`),
chatbot artefacts (`hope this helps`, `let's dive`), and overused
emphasis (`underscores`, `elevates`, `seamless`, `robust`,
`enhance`).

- **Chapter 7 (Evaluation):** zero hits across all patterns. The
  three em-dashes in the chapter are all in section headings
  (`\section{RQ1 --- modality effect}`, etc.), matching the
  existing convention in Specification (`\paragraph{RQ1 ---
  Modality effect.}`). No body-prose em-dash overuse.
- **Chapters 2 to 6:** zero hits across all patterns. Bold use is
  paragraph-leadin only, never inline emphasis. No Title Case
  Headings in body content.

No content edits required by the style sweep.

---

## Phase 5: Word-count budget

`notes/count_words.py` strips LaTeX commands and comments and
counts alphabetic word tokens.

| Chapter | Words |
|---------|------:|
| Background | 1,548 |
| LiteratureReview | 2,579 |
| Specification | 2,143 |
| Design | 3,215 |
| Implementation | 2,684 |
| Evaluation | 5,576 |
| ProfessionalIssues (stub) | 77 |
| Conclusion (stub) | 128 |
| **TOTAL** | **17,950** |

Hard cap is 25,000. Headroom of 7,050 words covers writing the
Introduction body, ProfessionalIssues, and Conclusion. No chapter
above is overweight; Evaluation is the largest at 5,576 because it
carries the requirements-traceability table, the validity-threats
analysis, and the alternative-design comparison that Trait 4
mandates. No trim required.

---

## Phase 6: Outstanding work before submission

1. Draft Chapter 1 (Introduction) following the wider-Informatics
   arc demanded by Trait 1: document understanding (broad) →
   structured extraction → multilingual utility bills → OCR vs.
   vision modality choice → this dissertation's contribution →
   chapter pointers. Currently `\chapter{Introduction}` is the
   template placeholder body.
2. Draft Chapter 8 (LSESP). The Evaluation chapter `\S\ref{sec:eval-dataset-provenance}`
   already cites GDPR Article 4(1) and `\S\ref{sec:eval-validity-construct}`
   names construct-level data choices that the LSESP chapter should
   pick up under data sovereignty and consent. Trait 7 demands all
   of: public well-being, security, environment/sustainability,
   economic/commercial, IP, software trustworthiness; each must be
   project-specific, not generic.
3. Draft Chapter 9 (Conclusion). Trait 6 demands transferable
   intellectual findings plus forward predictions for new domains.
   Evaluation `\S\ref{sec:eval-synthesis}` lists the five findings
   ready to promote; the alternative-design comparison
   `\S\ref{sec:eval-alternatives-allpages}` already names the
   leading future-work item (full-document vision baseline).
4. Capture the fourteen Implementation chapter screenshots
   (fig-6-1 through fig-6-14). Implementation.tex uses
   `\IfFileExists` placeholders; PNGs need to be produced by
   IDE/terminal capture before final compile.
5. Decide on `google-generativeai` in `requirements.txt`: remove or
   add a Gemini provider stub.
6. Prune orphan bib entries flagged in `verification.md`
   (`gemini2024gemini15`, `levenshtein1966`, `liu2024ocrbench`,
   `tam2024format`, `unstructured2026parsing`) before final
   submission.

---

## Files touched in this pass

- `Chapters/Evaluation.tex` — full draft (5,576 words; new content).
- `Chapters/Implementation.tex` — three test-count corrections
  (400 -> 531).
- `Chapters/Conclusion.tex` — added `\label{chap:conclusion}`.
- `Chapters/figures/fig-7-1-overall-accuracy.png` -
  `fig-7-6-timing-breakdown.png` — copied from
  `results/reports/four_way_20260428/figures/`.
- `Chapters/figures/fig-7-7-dataset-composition.png` -
  `fig-7-10-failure-attribution.png` — generated.
- `Chapters/figures/generate-fig-7-7.py` -
  `generate-fig-7-10.py` — new generator scripts (matching the
  existing `generate-fig-N-M.py` pattern).
- `notes/count_words.py` — new helper for budget tracking.
- `requirements.txt` (project repo) — added `pandas` to match the
  Implementation chapter's dependency recap.
