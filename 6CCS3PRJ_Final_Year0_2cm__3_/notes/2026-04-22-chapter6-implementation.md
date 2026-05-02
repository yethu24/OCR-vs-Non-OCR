# Chapter 6 (Implementation) changelog

Date: 2026-04-22

## Delivered

- Added `Chapters/Implementation.tex` with `\label{chap:impl}` and section labels: `sec:impl-bridge`, `sec:impl-layout`, `sec:impl-schema`, `sec:impl-loader`, `sec:impl-provider`, `sec:impl-pipeline`, `sec:impl-normalisation`, `sec:impl-evaldiag`, `sec:impl-deviations`, `sec:impl-testing`, `sec:impl-running`, `sec:impl-maintenance`, `sec:impl-summary`.
- Fourteen figure slots use locked filenames `fig-6-1-project-tree.png` through `fig-6-14-run-cli.png` under `Chapters/figures/`. Each figure uses `\IfFileExists` via macro `\implscreenshot{path}{placeholder text}` so `pdflatex` succeeds before PNGs exist; replacing placeholders is a drop-in file add only.
- `Chapters/Design.tex`: Expected-deviations paragraph now ends with `Chapter~\ref{chap:impl}~\S\ref{sec:impl-deviations}` (plan-specified one-line tighten).
- Cross-reference hygiene (flow review): `\label{chap:evaluation}` in `Chapters/Evaluation.tex`, `\label{chap:lsesp}` in `Chapters/ProfessionalIssues.tex`, `\label{chap:intro}` and `\label{sec:intro-rqs}` plus a short Research questions section in `report.tex`.

## Word count

- `wc -w Chapters/Implementation.tex` (includes LaTeX commands): approximately **2300** tokens; prose target (~2400 words) is met in order of magnitude once boilerplate commands are discounted.

## Evidence map (design rows D-5 .. D-10 and spec hooks)

- **D-5 / modality branch / ER1**: `sec:impl-pipeline`, figures `fig-6-8`, `fig-6-9`; summary ties ER1 to shared path.
- **D-6 / provider asymmetry**: `sec:impl-provider`, figures `fig-6-4` through `fig-6-7`.
- **D-7 / JSON hardening**: `sec:impl-pipeline`, figure `fig-6-9`.
- **D-8 / normalisation**: `sec:impl-normalisation`, figure `fig-6-10`.
- **D-9 / null-aware metrics**: `sec:impl-evaldiag`, figure `fig-6-11`.
- **D-10 / diagnosis**: `sec:impl-evaldiag`, figure `fig-6-12`; text links ER5 and FR6.
- **ER4 + NFR1/NFR3**: `run_pipeline` snapshot and error isolation, `sec:impl-pipeline` and summary traceability.
- **Tests / CLI**: `sec:impl-testing`, `sec:impl-running`, figures `fig-6-13`, `fig-6-14`.

## Humanizer

- Grep for banned tokens (`leverage`, `robust`, `holistic`, `comprehensive`, `seamless`, `crucial`, `vital`, `delve`, `utilise`, `facilitate`, `furthermore`, `moreover`, `essentially`, `fundamentally`, `indeed`, `in order to`) and em-dash (`---`) on `Implementation.tex`: **no hits** in body text (comment separators use `% ----` only).

## Outstanding / user

- Add the fourteen PNG captures to `Chapters/figures/` with the exact locked names (see figure captions in `Implementation.tex`). No `fig-6-*.png` files were present at changelog time.
- Local environment had **no `pdflatex` on PATH** in the agent shell; compile on a machine with TeX installed to confirm `informatics-report` class and all includes.

## ER numbering correction (in-session)

- Aligned ER1/ER4/ER5 wording with `Chapters/figures/generate-fig-4-tables.py` (ER1 modality isolation, ER4 reproducibility, ER5 failure attribution). Earlier draft incorrectly mapped ER1/ER4; corrected before handoff.

## 2026-04-23: Tight crops + appendix pointers

- `Chapters/Implementation.tex`: added `\apxref{...}` stub macro; each code-heavy section ends with `\apxref{C.1}`--`\apxref{C.12}`; `sec:impl-layout` ends with Appendix B.1 inventory sentence + `\apxref{B.1}`.
- Figure placeholders and captions now specify **tight line ranges** (see placeholders under each `\implscreenshot`). Re-capture **fig-6-2** through **fig-6-13** as short editor crops; **fig-6-1** (tree) and **fig-6-14** (CLI) unchanged.
- Diagnosis prose fixed to match `ground_truth is None or _value_in_text` logic; test class name corrected to `TestMissingColumnsShouldRaise`.
- When appendices exist, replace the **body** of `\newcommand{\apxref}[1]{...}` once so all pointers render as real cross-refs (or switch to `\hyperref`).
