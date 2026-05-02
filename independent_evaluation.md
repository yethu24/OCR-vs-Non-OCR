# Independent Evaluation of the Four-Way OCR vs Vision Experiment

This report is an artefact-driven re-analysis of the four-way (Sonnet 4.5 vs GPT-4o, OCR-text vs vision) extraction experiment recorded under
[`results/runs/`](results/runs/) and summarised in
[`results/reports/four_way_20260429/`](results/reports/four_way_20260429/).
Every number is recomputed from the per-document `evaluation.json`,
`metadata.json`, `timings.json`, `extraction.json`, `raw_llm_output.txt`,
and `ocr_text.txt` files by
[`scripts/analysis/independent_evaluation.py`](scripts/analysis/independent_evaluation.py),
which writes intermediate CSVs to
[`results/reports/four_way_20260429/derived/`](results/reports/four_way_20260429/derived/).

The corpus is 40 documents, all `digital_native=True` (no scanned bills),
distributed as 20 English / 12 German / 7 Italian / 1 French; 27 electricity /
7 water / 6 gas; page counts 1–8 (mean 3.9). The same prompt
([`prompts/extraction_v1.txt`](prompts/extraction_v1.txt)) is used in all four
conditions; the only varied factors are LLM provider (Anthropic Claude
Sonnet 4.5 vs OpenAI GPT-4o) and input modality (OCR-text vs vision).

Throughout the report, "n" refers to the number of independent observations
the figure aggregates over (typically a number of fields, where 12 fields x
40 docs = 480 cells per condition, less the `both_null` cells which the spec
excludes from the denominator).

---

## 1. Headline numbers

All four runs completed cleanly (`processed=40`, `skipped=0`, `failed=0` in
each `summary.json`). The independently recomputed metrics are identical to
those in [`comparison.json`](results/reports/four_way_20260429/comparison.json)
to the rounding precision stored there (the script verifies this and reports
no inconsistencies).

| Condition | n_eval | Overall acc. | Doc-level acc. | Hallucinations | Omissions | Both-null | Mean total ms | Mean OCR ms | Mean LLM ms | Total cost USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Sonnet 4.5 / OCR-text | 454 | 89.65% | 45.0% (18/40) | 8 | 9 | 26 | 16 349 | 8 860 | 3 711 | 0.4756 |
| Sonnet 4.5 / Vision | 458 | 87.55% | 37.5% (15/40) | 12 | 11 | 22 | 12 163 | 0 | 8 601 | 0.6126 |
| GPT-4o / OCR-text | 447 | 86.35% | 30.0% (12/40) | 1 | 17 | 33 | 14 444 | 8 705 | 2 143 | 0.3313 |
| GPT-4o / Vision | 450 | 85.33% | 22.5% (9/40) | 4 | 15 | 30 | 9 649 | 0 | 6 189 | 0.3750 |

All numbers were verified against
[`comparison.json`](results/reports/four_way_20260429/comparison.json) and
[`summary.txt`](results/reports/four_way_20260429/summary.txt) by the
analysis script. There are **no inconsistencies** between the two sources.

The ranking is `Sonnet OCR > Sonnet Vision > GPT-4o OCR > GPT-4o Vision`. The
spread between best and worst is 4.32 percentage points at the field level
and 22.5 percentage points at the document level. With n=40 documents and
~450 evaluated fields per cell, a 1-percentage-point gap corresponds to
about 4–5 fields; a 2-percentage-point gap corresponds to ~9 fields.

---

## 2. RQ1: modality effect

### 2.1 Aggregate

Within-provider modality gap (vision minus OCR-text), in field-level
accuracy points:

| Provider | OCR-text | Vision | Gap (V − O) |
|---|---:|---:|---:|
| Sonnet 4.5 | 89.65% | 87.55% | −2.10 pp |
| GPT-4o | 86.35% | 85.33% | −1.02 pp |

OCR-text wins on aggregate for both providers. The effect is small at this
sample size: a 2-pp Sonnet gap corresponds to roughly 9 differently-classified
fields out of 458; a 1-pp GPT-4o gap corresponds to 4–5 fields. **Pre-registered
hypothesis H1 ("vision will match or exceed OCR within provider") is not
supported in aggregate; vision is slightly worse, especially for Sonnet.**

### 2.2 Stratification

Slice tables are written to
[`results/reports/four_way_20260429/derived/`](results/reports/four_way_20260429/derived/)
(`modality_gap_by_*.csv`).

**By language** (`modality_gap_by_language.csv`), n is the number of documents
in each slice:

| Language | n | Sonnet OCR | Sonnet Vision | Sonnet gap | GPT-4o OCR | GPT-4o Vision | GPT-4o gap |
|---|---:|---:|---:|---:|---:|---:|---:|
| en | 20 | 92.31% | 88.89% | −3.42 pp | 87.67% | 85.52% | −2.15 pp |
| de | 12 | 91.43% | 89.29% | −2.14 pp | 87.50% | 86.03% | −1.47 pp |
| it | 7 | 79.01% | 79.01% | 0 pp | 80.00% | 82.72% | +2.72 pp |
| fr | 1 | 91.67% | 100.00% | +8.33 pp | 91.67% | 91.67% | 0 pp |

The aggregate "vision worse" reading is driven entirely by English and German
documents. Italian shows no gap for Sonnet and a small *vision advantage* for
GPT-4o. French (n=1) is statistically meaningless. This contradicts the
H1-implied direction of the gap "widening on non-Latin-script and low-frequency
layouts": all four languages here use Latin script, but Italian — where layouts
are typically densest and fields most ambiguous — does not punish vision and
in fact rewards it for one provider.

**By utility type** (`modality_gap_by_utility_type.csv`):

| Utility | n | Sonnet OCR | Sonnet Vision | Sonnet gap | GPT-4o OCR | GPT-4o Vision | GPT-4o gap |
|---|---:|---:|---:|---:|---:|---:|---:|
| electricity | 27 | 88.89% | 85.71% | −3.18 pp | 84.28% | 85.43% | +1.15 pp |
| gas | 6 | 91.30% | 92.75% | +1.45 pp | 89.86% | 82.86% | −7.00 pp |
| water | 7 | 91.14% | 90.12% | −1.02 pp | 91.14% | 87.18% | −3.96 pp |

The provider-by-utility interaction is striking. GPT-4o is slightly *better*
on vision for electricity but loses 7 pp on gas; Sonnet is the opposite.
With n=6 gas documents, a 7-pp gap is on the order of 5 fields, well within
sampling noise.

**By page count bucket** (`modality_gap_by_page_bucket.csv`):

| Pages | n | Sonnet OCR | Sonnet Vision | Sonnet gap | GPT-4o OCR | GPT-4o Vision | GPT-4o gap |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1–2 | 11 | 94.44% | 94.53% | +0.09 pp | 88.89% | 88.28% | −0.61 pp |
| 3–4 | 17 | 90.21% | 87.18% | −3.03 pp | 87.89% | 84.21% | −3.68 pp |
| 5+ | 12 | 84.33% | 81.48% | −2.85 pp | 81.68% | 84.09% | +2.41 pp |

Both pipelines are bounded to the first 2 pages (see Section 6), so accuracy
deteriorates with page count for the same reason both pipelines suffer:
later-page content (e.g. consumption tables on detail pages) is never seen.
The modality gap is essentially zero on 1–2 page bills (where both pipelines
see the whole document) and opens up on longer bills, but not in a clean
direction — GPT-4o vision actually rebounds on 5+ page bills while Sonnet
vision stays behind.

**By digital_native**: every document in the corpus has `digital_native=True`,
so this slice has no contrast (`modality_gap_by_digital_native.csv` has a
single row). This is a corpus-design limitation discussed in Section 9.

**By issuer** (`modality_gap_by_issuer.csv`): the modality gap is dominated
by a handful of issuers. The largest negative-for-vision gaps are
`Affinity Water` (Sonnet −7.6 pp, GPT-4o −14.0 pp), `Con Edison`
(both −13–14 pp), `Lupatotina Gas e Luce SRL` (Sonnet −12.5 pp on the
electricity bill). The largest positive-for-vision gaps are
`EDISON` (+25 pp both providers), `Eni gas e luce` (+11 pp Sonnet,
+26 pp GPT-4o), `EINHORN-ENERGIE` (+8 pp both). With 1–4 documents per
issuer, single-document outliers dominate this view.

### 2.3 Field-level matrix (where the modality matters)

From [`field_matrix.csv`](results/reports/four_way_20260429/derived/field_matrix.csv).
Each cell is "n_correct / n_eval" (i.e. excluding `both_null`). A field's
modality gap is calculated within provider.

| Field | Sonnet OCR | Sonnet Vision | Δ Sonnet | GPT-4o OCR | GPT-4o Vision | Δ GPT-4o |
|---|---:|---:|---:|---:|---:|---:|
| provider_name | 34/40 (85.0%) | 30/40 (75.0%) | **−10.0 pp** | 33/40 (82.5%) | 26/40 (65.0%) | **−17.5 pp** |
| utility_type | 39/40 | 39/40 | 0 | 39/40 | 39/40 | 0 |
| bill_number | 20/29 (69.0%) | 21/32 (65.6%) | −3.4 pp | 17/25 (68.0%) | 19/26 (73.1%) | +5.1 pp |
| bill_date | 35/37 (94.6%) | 36/37 (97.3%) | +2.7 pp | 35/37 | 36/37 | +2.7 pp |
| billing_period_start | 36/40 | 34/40 | −5.0 pp | 36/40 | 34/40 | −5.0 pp |
| billing_period_end | 36/40 | 36/40 | 0 | 36/40 | 36/40 | 0 |
| due_date | 31/34 (91.2%) | 31/34 | 0 | 29/32 (90.6%) | 29/33 (87.9%) | −2.7 pp |
| total_amount_due | 35/40 (87.5%) | 38/40 (95.0%) | **+7.5 pp** | 34/40 | 34/40 | 0 |
| currency | 40/40 | 40/40 | 0 | 36/40 (90.0%) | 36/40 (90.0%) | 0 |
| account_number | 27/36 (75.0%) | 28/37 (75.7%) | +0.7 pp | 17/35 (48.6%) | 27/36 (75.0%) | **+26.4 pp** |
| consumption_amount | 36/39 (92.3%) | 33/39 (84.6%) | −7.7 pp | 36/39 | 32/39 (82.0%) | −10.3 pp |
| consumption_unit | 38/39 (97.4%) | 35/39 (89.7%) | −7.7 pp | 38/39 | 36/39 (92.3%) | −5.1 pp |

The aggregate −1 to −2 pp modality gap masks much larger field-level swings:

- **Vision is dramatically worse than OCR on `provider_name`** (−10 pp Sonnet,
  −17.5 pp GPT-4o) and **slightly worse on `consumption_amount`/
  `consumption_unit`** (−5 to −10 pp).
- **Vision is dramatically better than OCR on `account_number` for GPT-4o
  only** (+26.4 pp; +0.7 pp for Sonnet).
- **Vision wins on `total_amount_due` for Sonnet only** (+7.5 pp).
- `utility_type`, `currency`, `bill_date`, `due_date`, `billing_period_end`
  are essentially modality-independent.

The two big effects (provider_name and account_number) point in opposite
directions, so headline aggregation hides the structure. Mechanisms below.

---

## 3. RQ2: cost, latency, operational complexity

### 3.1 Cost (40-document run)

From `metadata.json` per doc, summed over the run:

| Condition | Total USD | Mean USD/doc | Input tokens | Output tokens |
|---|---:|---:|---:|---:|
| GPT-4o / OCR-text | 0.3313 | 0.0083 | 117 100 | 3 859 |
| GPT-4o / Vision | 0.3750 | 0.0094 | 134 505 | 3 875 |
| Sonnet 4.5 / OCR-text | 0.4756 | 0.0119 | 124 889 | 6 731 |
| Sonnet 4.5 / Vision | 0.6126 | 0.0153 | 170 642 | 6 713 |

Vision is more expensive than OCR for both providers (+13% for GPT-4o,
+29% for Sonnet) because vision input pushes the input-token count up by
the image-payload tokens. Sonnet vision is the most expensive cell at
$0.015/document, twice GPT-4o OCR.

### 3.2 Latency (mean per document, ms)

| Condition | Total | PDF→image | OCR | LLM call | Parse |
|---|---:|---:|---:|---:|---:|
| Sonnet 4.5 / OCR-text | 16 349 | 3 778 | 8 860 | 3 711 | 0.3 |
| Sonnet 4.5 / Vision | 12 163 | 3 562 | 0 | 8 601 | 0.3 |
| GPT-4o / OCR-text | 14 444 | 3 595 | 8 705 | 2 143 | 0.3 |
| GPT-4o / Vision | 9 649 | 3 460 | 0 | 6 189 | 0.3 |

Vision is **faster wall-clock**, even though its LLM call takes longer,
because OCR (~8.7 s on average) is replaced by zero. Net: vision saves
~4–5 s per document. The PDF-to-image stage takes ~3.5 s in every condition
(it processes the entire PDF before either pipeline picks the first 2 pages
— see Section 6).

### 3.3 Robustness to page-count distribution

From [`timings_by_pages.csv`](results/reports/four_way_20260429/derived/timings_by_pages.csv):

OCR-text time (`ocr_ms`) does not scale with page count (Tesseract only sees
2 pages):

| Pages | n | Sonnet OCR ms | GPT-4o OCR ms |
|---|---:|---:|---:|
| 1–2 | 11 | 8 400 | 8 323 |
| 3–4 | 17 | 8 763 | 8 511 |
| 5+ | 12 | 9 419 | 9 329 |

But PDF-to-image time *does* (it converts every page):

| Pages | mean PDF ms (Sonnet OCR) |
|---|---:|
| 1 | 595 |
| 2 | 1 368 |
| 3 | 1 463 |
| 4 | 8 294 |
| 5 | 4 253 |
| 6 | 2 728 |
| 7 | 8 202 |
| 8 | 5 040 |

The PDF-to-image scaling is noisy because Poppler's per-page time depends on
embedded fonts, images, and DPI. On a corpus of longer bills the
PDF-to-image stage would dominate every condition equally, leaving the
cost/latency *gap* between OCR and vision essentially unchanged. **The
operational comparison is robust to the page-count distribution because the
LLM and OCR stages already do not scale with page count under the current
2-page bound.** It would not be robust if an "all-pages" version were used
(see Section 7).

### 3.4 Operational complexity

OCR-text pipeline depends on:
- Poppler binary (PDF rasterisation, also used by vision)
- Tesseract binary, with language packs `eng`, `deu`, `fra`, `ita`
- Per-document language tag in the manifest, used to choose Tesseract's
  language pack
([`src/ocr/tesseract.py:LANGUAGE_MAP`](src/ocr/tesseract.py))

Vision pipeline depends on:
- Poppler binary only

The vision pipeline removes Tesseract, language-pack management, and the
need for the manifest to carry an accurate language tag. This is a real but
modest operational simplification, especially for ad-hoc or
unknown-language inputs. **H2 is supported**: vision costs 13–29% more per
document while removing Tesseract from the deployment surface.

---

## 4. RQ3: provider effects

### 4.1 Provider-level effects orthogonal to modality

Per-field comparison (averaging the two modalities):

| Field | Sonnet avg | GPT-4o avg | Sonnet − GPT-4o |
|---|---:|---:|---:|
| account_number | 75.4% | 61.8% | +13.6 pp |
| currency | 100.0% | 90.0% | +10.0 pp |
| consumption_amount | 88.5% | 87.2% | +1.3 pp |
| provider_name | 80.0% | 73.8% | +6.2 pp |
| (others) | within ±2 pp | | |

Sonnet outperforms GPT-4o by ~3 pp on the overall average and dominates on
two specific fields:
- **`currency`**: Sonnet 100% in both modalities, GPT-4o 90% in both modalities.
  GPT-4o misses the same 4 documents in both modalities — these are
  Australian/Canadian bills where GPT-4o returns `null` for currency despite
  the symbol being on the bill (verified by inspecting
  [`results/runs/.../gpt4o_ocr/documents/au_electricity_agl_001/extraction.json`](results/runs/20260429_210332_openai_gpt4o_ocr_text/documents/au_electricity_agl_001/extraction.json)
  and the corresponding vision run). This is a pure provider-level effect
  — modality does not change it.
- **`account_number` in OCR mode only**: GPT-4o OCR sits at 48.6% (n=35),
  while every other cell is ≥75%. The mechanism (Section 5) is that GPT-4o
  in text mode strips internal whitespace from the candidate string, so
  account numbers like `0 0000 000` (BC Hydro) come back as `000000000`.
  Sonnet, given the same OCR text, preserves the spaces. Vision rescues
  GPT-4o because the model sees the spacing visually.

### 4.2 Hallucination/omission profile

| Condition | Hallucinations | Omissions | H/O ratio |
|---|---:|---:|---:|
| Sonnet 4.5 / OCR-text | 8 | 9 | 0.89 |
| Sonnet 4.5 / Vision | 12 | 11 | 1.09 |
| GPT-4o / OCR-text | 1 | 17 | 0.06 |
| GPT-4o / Vision | 4 | 15 | 0.27 |

GPT-4o is markedly more conservative: it omits when uncertain rather than
hallucinating. Sonnet has roughly balanced H/O. Vision shifts both providers
toward more hallucinations. This is a provider-level effect that should
inform deployment: if a downstream pipeline is more tolerant of missing data
than of fabricated data, GPT-4o is the safer choice; if missing data has a
high cost, Sonnet is.

### 4.3 Cross-provider agreement

From [`agreement_summary.csv`](results/reports/four_way_20260429/derived/agreement_summary.csv):

| Modality | n_evaluated | Agreement rate | Disagreements where one is right | Disagreements where both wrong |
|---|---:|---:|---:|---:|
| OCR-text | 454 | 90.5% (411) | 29 (25 Sonnet, 4 GPT-4o) | 14 |
| Vision | 460 | 87.2% (401) | 41 (29 Sonnet, 12 GPT-4o) | 18 |

When the two providers agree, they are correct 87–88% of the time. When
they disagree, Sonnet is right 6× more often than GPT-4o in OCR mode and
~2.4× more often in vision mode. **Naive majority voting on two providers
provides no benefit (it cannot break ties); a "default to Sonnet on
disagreement" rule with the OCR pipeline matches Sonnet OCR's accuracy
(89.65%) and gives no headroom**. The interesting upper bound — *oracle
ensembling* in which we always pick whichever provider is right — is
90.53% (OCR) and 89.78% (vision). This is the ceiling for any single-
modality, two-provider ensemble.

If we ensemble across both providers and both modalities (4 conditions),
the oracle ceiling jumps to 95.88% (442 of 461 evaluated fields are correct
in at least one of the four cells). The gap between the best single condition
(89.65%) and this 4-way ceiling (95.88%) is 6.2 pp.

The within-provider modality oracle (whichever modality is right per field)
is 93.60% for Sonnet and 92.60% for GPT-4o — a ~4 pp lift over each
provider's best single-modality cell. So a *router* that picks the modality
per field would help more than ensembling across providers. This is a
counterfactual prediction (Section 7), not an actually-implemented system.

---

## 5. Failure-mode taxonomy

The modality flips and per-field swings have specific causal mechanisms.
For each, at least one named document with file paths is given; the full
flip table is at
[`flip_table.csv`](results/reports/four_way_20260429/derived/flip_table.csv).

### M1. Brand wordmark vs legal name (vision worse on `provider_name`)

The bill displays a large brand wordmark (e.g. "PG&E", "ConEdison",
"Origin", "PG E") prominently and the canonical legal name only in fine
print (footer disclaimer). Vision picks the visually salient wordmark; OCR
text contains both, and the LLM prefers the legal name (which matches GT).

**Evidence** (PG&E case, ground truth `pacific gas and electric`):
- OCR text contains "*"PG&E" refers to Pacific Gas and Electric Company, a
  subsidiary of PG&E Corporation*"
  ([`results/runs/20260429_204310_anthropic_claudesonnet4520250929_ocr_text/documents/us_electricity_pge_001/ocr_text.txt`](results/runs/20260429_204310_anthropic_claudesonnet4520250929_ocr_text/documents/us_electricity_pge_001/ocr_text.txt)).
- OCR-text Sonnet returns `pacific gas and electric` (correct);
  Vision Sonnet returns `pg e`
  ([`results/runs/20260429_205453_anthropic_claudesonnet4520250929_vision/documents/us_electricity_pge_001/extraction.json`](results/runs/20260429_205453_anthropic_claudesonnet4520250929_vision/documents/us_electricity_pge_001/extraction.json)).

Other instances (all in the OCR-only-correct column of `flip_table.csv`):
`au_electricity_originenergy_001` (OCR `origin energy`, vision `origin`),
`de_electricity_vattenfalleuropesale_001/002` (OCR `vattenfall europe sales`,
vision `vattenfall`),
`gb_electricity_eonenergysolutions_001` (OCR `e on energy solutions`,
vision `e on`),
`it_electricity_enigaseluce_001` (OCR `eni gas e luce`, vision `eni`),
`us_electricity_conedison_001/002` (OCR `con edison`, vision `conedison`),
`gb_water_affinitywater_001` (GPT-4o OCR `affinity water`, GPT-4o vision
`affinitywater`).

There are nine such cases for GPT-4o and six for Sonnet, accounting for
~80% of the provider_name modality gap.

### M2. LLM whitespace coercion in account numbers (GPT-4o OCR specific)

OCR text correctly captures account numbers with internal spaces
(e.g. BC Hydro shows "0 0000 000" in the OCR output — verified by grep on
[`ca_electricity_bchydro_001/ocr_text.txt`](results/runs/20260429_210332_openai_gpt4o_ocr_text/documents/ca_electricity_bchydro_001/ocr_text.txt)),
but GPT-4o in text mode collapses them to "000000000". Sonnet, given the
identical OCR text, returns "0 0000 000" with the spaces preserved. The
mechanism is a model-specific prior: GPT-4o normalises numeric strings on
extraction; Sonnet does not. Vision rescues GPT-4o because the visual
representation of the account number forces the model to treat the spaces
as content, not formatting.

Affected documents include all four BC Hydro bills, `au_electricity_agl_001`
(OCR loses trailing `x`), `de_electricity_enbwostwrttembergdon_001`
(OCR `520730` vs vision `vk600312`),
`de_electricity_vattenfalleuropesale_002` (OCR `836000000000`, vision
`836 000 000 000`), `gb_water_affinitywater_001`,
`it_electricity_lupatotina_001`, and `it_gas_edison_001` — eleven cases
total (the `vision_only_correct` column in the GPT-4o flip summary).

### M3. Locale-formatting confusion under vision (German thousands separators)

German bills print numbers as `305.852` for "three hundred five thousand
eight hundred fifty-two". The prompt explicitly tells the model to detect
the convention from the document context. OCR-text mode sees the same
convention repeated across many lines and the model parses correctly;
vision mode, with the same prompt, occasionally interprets a single "."
as a decimal point.

**Evidence**:
[`de_gas_greenplanetenergy_001`](results/runs/20260429_211339_openai_gpt4o_vision/documents/de_gas_greenplanetenergy_001/raw_llm_output.txt):
ground truth `consumption_amount=305852` (kWh). GPT-4o OCR returns
`305852`; GPT-4o vision returns `305.852` (which is normalised to 305.85).
Same number parsed differently because the model in vision mode picked up
on the dot-as-decimal alternative reading.
[`de_water_einhornenergie_001`](results/runs/20260429_211339_openai_gpt4o_vision/documents/de_water_einhornenergie_001/extraction.json)
shows a similar pattern (138 vs 165 m³ depending on which figure the model
locks onto). This is a small contributor to the consumption_amount gap.

### M4. Field disambiguation when multiple plausible candidates appear

Bills routinely show several values that look like the target field. The
LLM picks one; OCR vs vision picks differently because the visual
saliency profile differs from text-frequency saliency.

**Evidence (total_amount_due)**:
[`gb_water_affinitywater_001`](results/runs/20260429_204310_anthropic_claudesonnet4520250929_ocr_text/documents/gb_water_affinitywater_001/extraction.json):
ground truth £46.00. Sonnet OCR predicts £235.14 (a different total on the
bill, likely the year-to-date or annualised figure). Sonnet vision predicts
£46.00. The relevant value is in the OCR text; the LLM disambiguated
incorrectly.

**Evidence (bill_number)**:
[`it_electricity_engie_001`](results/runs/20260429_204310_anthropic_claudesonnet4520250929_ocr_text/documents/it_electricity_engie_001/extraction.json):
ground truth `100/mm/859654`. OCR Sonnet picks `100/mm/1598996` (a
similarly-formatted alternative number on the bill). Vision Sonnet picks
`100/mm/859654` correctly. Bill_number, billing_period_*, and bill_date
all flip on this document for Sonnet.

This mechanism produces flips in **both** directions: which candidate is
visually salient vs textually frequent depends on bill layout, so the
modality gap on a given field for a given issuer is partly a function of
where on the page the various candidates sit.

### M5. Sign handling on credit/refund bills

Ground truth annotates net amounts payable as positive and net credits
(refunds) as negative; the bill prints the absolute value next to a label
like "Guthaben" / "credit balance". No condition gets the negative sign.

**Evidence**:
[`de_electricity_stwbstadtwerkebrande_001/ocr_text.txt`](results/runs/20260429_204310_anthropic_claudesonnet4520250929_ocr_text/documents/de_electricity_stwbstadtwerkebrande_001/ocr_text.txt)
contains "*Ihr Guthaben: 125,78 EUR*" (ground truth `total_amount_due=-125.78`).
All four conditions get this wrong: Sonnet OCR returns `490.22` (the gross
charge), Sonnet vision returns `125.78`, GPT-4o OCR returns null, GPT-4o
vision returns `69.0`.
Other examples: `de_gas_greenplanetenergy_002` (GT `-507.18`),
`de_water_einhornenergie_001` (GT `-36.71`),
`de_electricity_naturstromhandel_001` (GT `-40.14`).

This is a *systematic* GT/prompt construct issue, not a modality or
provider issue: the prompt nowhere instructs the model to sign-flip credit
amounts. Five of the OCR-mode failures map to this pattern (also flagged
by the diagnosis-heuristic disagreement audit, Section 5.7).

### M6. OCR character-level errors on stylised fields

Tesseract misreads stylised/dot-matrix fonts, mid-string slashes, or long
runs of repeated digits. The misread reaches the LLM as text, and either
the LLM repeats it or "smooths" it into something else.

**Evidence**:
[`it_gas_edison_001/ocr_text.txt`](results/runs/20260429_210332_openai_gpt4o_ocr_text/documents/it_gas_edison_001/ocr_text.txt)
contains "dododododo" where the bill shows "0000000000". OCR-mode Sonnet
returns `dododododo` for bill_number; vision returns `0000000000`. Edison
also shows OCR "123456/891" vs vision "1234567891" for account_number.
Affinity Water has "530968" in OCR but the bill shows "330968" (3→5
character substitution), affecting both OCR runs.

These are genuine OCR failures for which the diagnosis heuristic
correctly attributes blame.

### M7. Hallucinated bill numbers from placeholder-shaped fields

Some bills have a long alphanumeric "internal reference" string that the
GT annotates as `null` (because it is not a customer-facing bill number).
The LLM extracts it as bill_number anyway.

**Evidence**:
[`gb_water_affinitywater_001`](results/runs/20260429_204310_anthropic_claudesonnet4520250929_ocr_text/documents/gb_water_affinitywater_001/extraction.json):
GT bill_number is null. Sonnet OCR returns `000001/358/80911d42g00001`,
Sonnet vision returns `000001/558/h0911042000001`, GPT-4o OCR returns the
same OCR pattern, GPT-4o vision correctly returns null.
[`au_electricity_originenergy_001`](results/runs/20260429_205453_anthropic_claudesonnet4520250929_vision/documents/au_electricity_originenergy_001/extraction.json):
both vision conditions hallucinate a bill_number; both OCR conditions
correctly return null.

This is the dominant source of vision hallucinations (12 for Sonnet, 4 for
GPT-4o, vs 8 and 1 in OCR mode).

### M8. Page-coverage truncation on multi-page bills

Some target fields appear only on later pages. Both pipelines cap input at
the first 2 pages (Section 6), so these fields are unreachable.
[`it_electricity_lupatotina_001`](results/runs/20260429_205453_anthropic_claudesonnet4520250929_vision/documents/it_electricity_lupatotina_001/extraction.json)
is an 8-page Italian bill; the OCR-text only contains content from pages
1–2 (verified: text length 5 013 chars, similar to 2-page bills).
Account_number flips because the truncated content is incomplete in
text mode but the visible number on page 1 is enough for vision.

This is structurally not a "modality" issue: it is a pipeline-design issue
that affects both modalities equally.

### 5.7 Diagnosis-heuristic audit

The spec (`§ 12.5`) defines an attribution rule for OCR-mode failures: if
the GT value is a case-insensitive substring of the OCR text, blame the
LLM; otherwise blame OCR. Running this against all 108 OCR-mode failure
rows ([`diagnosis_audit.csv`](results/reports/four_way_20260429/derived/diagnosis_audit.csv)):

| Strict attribution | Sonnet | GPT-4o | Total |
|---|---:|---:|---:|
| `ocr_failure` | 27 | 35 | 62 |
| `llm_extraction_failure` | 20 | 26 | 46 |

By inspection of the named documents above, the strict heuristic is
**often correct in spirit but mis-attributes specific patterns**:

- **Mis-attributed to "OCR failure" when truer cause is field disambiguation**
  (M4). Example: `it_electricity_engie_001` bill_date — predicted
  `2019-05-01`, GT `2019-11-11`, both dates appear on the bill in OCR text.
  The strict rule says "GT not in OCR" because the specific date string
  isn't there, but Tesseract did capture both candidates; the LLM picked
  the wrong one.
- **Mis-attributed to "OCR failure" when truer cause is GT vs bill convention**
  (M5). Example: `de_electricity_stwbstadtwerkebrande_001` total_amount_due
  — strict heuristic finds `-125.78` not in OCR text (it isn't, because
  the bill prints `125,78`), so it attributes to OCR. But Tesseract did
  the correct thing; the failure is the GT/prompt construct.
- **Mis-attributed to "LLM failure" when GT is itself a placeholder.**
  Example: `au_electricity_agl_001` bill_number GT `xxxx xxxx xxxx xxxx xxxx`
  — the LLM correctly returned null; the heuristic finds the GT in the OCR
  text (as a placeholder) and concludes "LLM failure".
- **Strict-vs-relaxed disagreement** (5/108 cases): all five are M5
  sign-handling cases. The strict rule looks for the signed string `-125.78`
  and fails; the relaxed rule (alphanumeric-only) matches because it strips
  the minus sign. Both attribution outputs are equally non-informative for
  this mechanism.

A richer attribution scheme implied by the data (in increasing order of
manual effort): `ocr_lost`, `ocr_corrupted`, `llm_disambiguation_error`,
`llm_format_normalised`, `llm_truncated_to_wordmark`,
`llm_hallucination_from_placeholder`, `gt_placeholder_or_redacted`,
`gt_sign_vs_bill`, `page_coverage_truncation`. The current binary scheme
is adequate for headline numbers but cannot answer "what should we *do*
about each failure?". The mechanisms in M1–M8 above are the cause
categories.

---

## 6. Page-coverage finding

[`src/pipeline.py:137`](src/pipeline.py) and
[`src/pipeline.py:149`](src/pipeline.py) both slice the converted page
images with `images[:2]`. The OCR pipeline runs Tesseract on the first 2
images only, then concatenates the text; the vision pipeline sends the
first 2 images to the LLM directly. **Both modalities are equally bounded
to the first 2 pages.** This contradicts a possible reading of the spec
(`§ 3.10`) that only mentions the bound for vision.

Empirical confirmation from
[`page_coverage.csv`](results/reports/four_way_20260429/derived/page_coverage.csv):

- For the 8-page documents (`de_gas_greenplanetenergy_001/002`,
  `de_electricity_naturstromhandel_001`, `it_electricity_lupatotina_001`),
  the OCR text contains a "Seite 1 von 8" / "Pagina 1 di 8" marker but no
  later-page markers.
- OCR character count by page count: 1-page docs 2 297, 2-page docs 4 941,
  3-page docs 5 348, 4-page docs 4 663, 5-page docs 5 523, 6-page docs 3 987,
  7-page docs 2 552, 8-page docs 5 400. The text plateaus around 5 000 chars
  regardless of page count — consistent with a 2-page bound (where text
  length depends on what's on those two pages, not on the document length).
- Tesseract runtime is ~8.5–9.5 s across page-count buckets (does not scale
  with page count) — see [`timings_by_pages.csv`](results/reports/four_way_20260429/derived/timings_by_pages.csv).

Implications for the modality comparison:
- The two pipelines are on equal footing for page coverage. Neither has
  more information than the other.
- The accuracy degradation on 5+ page bills (Section 2.2) is attributable
  to fields that genuinely live on later pages, not to OCR truncation
  vs vision truncation. So the "long-tail layouts" criticism applies
  equally to both pipelines.
- The wall-clock comparison in Section 3.2 is robust to this constraint
  because it is shared. A hypothetical "OCR pipeline on all pages" would
  shift OCR's latency and cost upward, widening the gap (see Section 7).

There is a small pipeline-side wastage: `pdf_to_images()` rasterises
*every* page of the PDF before either pipeline picks the first 2. On the
8-page Lupatotina document, PDF→image takes ~5 s while only the first 2
of those 8 images are used by either pipeline.

---

## 7. Alternative-design counterfactuals

Each prediction below is anchored to specific evidence from the actual
runs. Effect sizes are field-level percentage points; confidence is low
because n=40.

### 7.1 Per-issuer templates

**Prediction**: Within-issuer accuracy would jump to 95–100% for any issuer
with ≥3 documents, but the system would lose its template-free property.

**Evidence**: Issuers with ≥3 documents in this corpus are BC Hydro (4) and
PG&E (2 — with similar layouts within issuer). BC Hydro accuracy is already
100% in Sonnet OCR/Vision (`modality_gap_by_issuer.csv`); BC Hydro accuracy
is 81–88% in GPT-4o, dragged down by the M2 whitespace-coercion failure on
account_number. A regex template that captures `\d \d{4} \d{3}` after
`Account number` would eliminate that failure deterministically. **Net
gain on this corpus: roughly +3–4 fields** (the BC Hydro account_number
flips for GPT-4o), but no help on the long tail of single-document issuers
(Affinity Water, ENGIE, Edison, Stadtwerke variants).

### 7.2 Fine-tuned encoder–decoder models (LayoutLMv3, Donut)

**Prediction**: Without fine-tuning data of comparable scale (this corpus
is 40 docs), an out-of-the-box document model would underperform LLMs on
multilingual extraction; with fine-tuning data, it would close the gap on
formatting fields (account_number, bill_number) where LLMs hallucinate.

**Evidence**: The dominant failures are M4 (field disambiguation) and M7
(placeholder hallucination). Both are reasoning failures, not layout
failures, and a layout-aware model with no domain-specific training data
has no reason to disambiguate better. **Net prediction: neutral to mildly
negative on this corpus, positive only with hundreds of labelled bills.**

### 7.3 Provider ensembling (Sonnet + GPT-4o)

**Prediction**: A naive majority vote on two providers cannot break ties
and yields no benefit. An *oracle* picker would gain ~1 pp in OCR (89.65 →
90.53%) and ~2.2 pp in vision (87.55 → 89.78%). A "Sonnet-default with
GPT-4o tiebreaker on hallucination-prone fields" rule would help marginally.

**Evidence**:
[`agreement_summary.csv`](results/reports/four_way_20260429/derived/agreement_summary.csv).
In OCR mode there are 43 disagreements; Sonnet is right in 25, GPT-4o in
4, neither in 14. A picker that always defers to Sonnet on disagreement
matches Sonnet's accuracy exactly. **Net prediction: <2 pp lift, with the
operational cost of running both providers and a tiebreaker model.**

### 7.4 Single-modality system (vision-only or OCR-only)

**Prediction**: OCR-only is uniformly better than vision-only on aggregate
(by ~2 pp Sonnet, ~1 pp GPT-4o), but loses on `total_amount_due` (Sonnet)
and `account_number` (GPT-4o). Choosing the modality at the field level
would lift Sonnet's ceiling to 93.6% and GPT-4o's to 92.6%.

**Evidence**:
[`flip_summary.csv`](results/reports/four_way_20260429/derived/flip_summary.csv).
Across all evaluated fields and both providers, OCR is uniquely correct
on 51 fields and vision is uniquely correct on 44. **Net prediction: a
field-level modality router (e.g. "use vision for `account_number` and
`provider_name`-vs-wordmark validation, OCR for everything else") would
lift Sonnet to ~93% and GPT-4o to ~93% on this corpus, but adding such a
router doubles cost and complexity.**

### 7.5 Vision pipeline on all pages

**Prediction**: Accuracy on 5+ page bills would improve modestly on fields
that live on later pages (consumption tables on detail pages). Cost and
latency would increase roughly proportionally to the page count.

**Evidence**: The 5+ page bucket has accuracy 81–84% (vs 88–95% for 1–2
page bills) — see Section 2.2. Some of that gap is field-disambiguation
failures on the cover page, but a non-trivial fraction is genuinely
"value not on first 2 pages". **Net prediction: +1 to +3 pp on the 12
documents in the 5+ bucket, ~+0.7 pp on the corpus as a whole, at the cost
of doubling-to-tripling the per-document token spend** (Sonnet vision is
already $0.015 per document on the 2-page cap; an 8-page bill would push
toward $0.05–0.06 per document).

### 7.6 OCR pipeline that processes every page

**Prediction**: Accuracy gains very similar to 7.5 (the same later-page
fields would now appear in the OCR text). No vision-style locale-formatting
errors (M3) would creep in. Cost essentially unchanged (Tesseract is local).
Latency goes up linearly: each Tesseract call is ~4–5 s/page on this
hardware (extrapolating from the 1-page = 4.5 s cell in `timings_by_pages.csv`).

**Evidence**: The same later-page values that vision-on-all-pages would see
are present in the source PDF and would be captured by Tesseract; they
are simply omitted by `pipeline.py:137` (`images[:2]`). **Net prediction:
+1 to +3 pp on 5+ page bills, +0.7 pp corpus-level, latency +30–40 s/doc
on long bills.** This is the *cheapest* path to the predicted gain in 7.5.

### 7.7 Construct-level observations

(See Section 8 for the brand-vs-legal-name issue.) Several documents have
ground-truth conventions that systematically penalise the model regardless
of modality:
- `total_amount_due` for credit balances is recorded as a negative
  number even though the bill prints the absolute value (M5). 5 documents
  out of 40 are credit-balance bills (12.5%).
- `provider_name` is recorded with the canonical brand-plus-descriptor
  string ("Pacific Gas and Electric") rather than the prominently-displayed
  wordmark ("PG&E"). Both are defensible; the GT picks one (Section 8).

---

## 8. Construct-level observations

The ground truth is the canonical reference per the user instruction.
Two cases are documented where the GT records *one of multiple defensible
answers*. These are not GT errors; they are construct-level choices that
affect the modality comparison.

### 8.1 Brand wordmark vs legal/canonical name (`provider_name`)

The GT consistently chooses the canonical text-form name over the
prominently-displayed wordmark. Examples (from M1):

| Document | Wordmark on bill | Canonical name (GT) |
|---|---|---|
| `us_electricity_pge_001` | PG&E | Pacific Gas and Electric |
| `gb_electricity_eonenergysolutions_001` | E.ON | E.ON Energy Solutions |
| `de_electricity_vattenfalleuropesale_001/002` | Vattenfall | Vattenfall Europe Sales |
| `it_electricity_enigaseluce_001` | Eni | Eni gas e luce |
| `au_electricity_originenergy_001` | Origin | Origin Energy |
| `us_electricity_conedison_001/002` | conEdison (one word) | Con Edison (two words) |

**Sensitivity analysis**: if the GT instead accepted the brand wordmark,
all six Sonnet vision and nine GPT-4o vision M1 failures would become
correct, lifting:
- Sonnet vision provider_name from 75.0% to 90.0% (+15 pp)
- GPT-4o vision provider_name from 65.0% to 87.5% (+22.5 pp)
- Sonnet vision overall from 87.55% to 88.86% (+1.3 pp)
- GPT-4o vision overall from 85.33% to 87.33% (+2.0 pp)

Under that alternative defensible answer, the Sonnet OCR vs Sonnet vision
gap closes from −2.1 pp to −0.8 pp; the GPT-4o OCR vs vision gap *flips*
from −1.0 pp to +1.0 pp. **The headline claim "vision is worse than OCR
within provider" becomes a tossup if the alternative defensible answer is
accepted.** This is the single biggest sensitivity in the headline numbers.

### 8.2 Bill_number for placeholder/internal references

Several bills (Affinity Water, AGL, several German Stadtwerke) have a long
internal-reference alphanumeric that GT records as null. Vision and OCR
both extract these alphanumerics as bill_numbers (M7). If the GT
alternatively accepted the internal reference as a valid bill_number, the
hallucination counts would shift by ~3–5 fields per condition. This would
not change the modality ranking but would soften the GPT-4o
"conservative-omitter" profile.

### 8.3 Negative amount convention (`total_amount_due`)

Five credit-balance bills have GT records like `total_amount_due=-125.78`
where the bill prints `125,78 EUR Guthaben`. Each of these costs every
condition one field. If GT instead recorded the bill-printed magnitude
with a separate `is_credit` flag (which the schema does not have), all
five would be correctable. As-is, the failure is symmetric across
conditions and does not affect the modality ranking.

---

## 9. Limitations

In approximate decreasing order of impact:

**L1. n=40, with 4–6 docs per cell for several slices.** A 1-pp gap is ~5
fields; a 2-pp gap is ~9 fields. The aggregate "Sonnet OCR wins" reading
spans 4 pp from best to worst, which is real but not large. Italian (n=7)
and gas (n=6) sub-slices are essentially case studies. French (n=1) is
not interpretable. Cause: dataset size constrained by annotation cost.
Remedy: 100–200 documents per cell would resolve the 1–2 pp gaps to
significance.

**L2. All documents are `digital_native=True`.** No scanned bills, no
photographed bills, no perspectival distortion, no handwriting. OCR and
vision both perform best on born-digital input; the gap between them on
scans would likely be larger and would favour vision. The headline
finding that "vision matches or trails OCR on born-digital input" cannot
be extrapolated to scanned bills. Cause: corpus assembled from publicly
available PDFs. Remedy: include scans or photographs.

**L3. Both pipelines truncate to 2 pages.** Section 6 establishes this is
true of OCR as well as vision, contrary to a possible reading of the spec.
This is a fairness property of the comparison but it caps achievable
accuracy on long bills. Cause:
[`src/pipeline.py:137,149`](src/pipeline.py) hardcodes `images[:2]`.
Remedy: remove the OCR-side cap (cost-free; Tesseract is local) and at
minimum make the vision-side cap configurable.

**L4. Diagnosis heuristic conflates several distinct mechanisms.** Section
5.7 enumerates four failure modes that the strict substring rule
mis-attributes. The reported "OCR failure" vs "LLM failure" split should
not be taken as a clean attribution. Cause: the heuristic is a one-line
substring check
([`src/evaluation/diagnosis.py:_value_in_text`](src/evaluation/diagnosis.py)).
Remedy: a richer category set as listed at the end of Section 5.7,
or replace with manual labelling for the failure subset.

**L5. Construct-level GT choices** (Section 8) penalise vision
disproportionately on `provider_name`. Under the alternative defensible
answer (wordmark), the vision-vs-OCR gap nearly closes. The headline
"vision is worse" is partly a function of which name the GT scribe wrote
down.

**L6. Asymmetric structured-output mechanisms.** OpenAI's Structured
Outputs (constrained decoding) and Anthropic's prompt-instructed JSON are
not the same kind of guarantee. The H7 hallucination rate could be partly
a function of this asymmetry. Cause: provider-API parity is not
achievable. Remedy: archive raw_llm_output (already done) and run a
post-hoc parsing comparison.

**L7. Single prompt template, single temperature.** Spec choice for
internal validity, but the prompt has been heavily engineered for
locale-formatting issues (per the lengthy "NUMBER PARSING" section of
[`prompts/extraction_v1.txt`](prompts/extraction_v1.txt)). M3 errors
might disappear with a better-crafted prompt; M1 errors might disappear
if the prompt explicitly preferred wordmarks vs canonical names. Cause:
prompt engineering is treated as out-of-scope. Remedy: ablate the prompt
once headline numbers are settled.

**L8. Cost numbers depend on the in-house pricing table at the time of
the run.** [`src/performance.py:_PRICING`](src/performance.py) hardcodes
$2.50/$10.00 per 1M tokens for GPT-4o and $3.00/$15.00 for Claude
Sonnet 4.5. Provider price changes after April 2026 invalidate the
absolute numbers but not the relative ratios.

**L9. No statistical significance tests.** With n=40 and most gaps in the
single-digit pp range, a McNemar's test on paired field-level outcomes
would be appropriate. The script outputs the pairwise outcomes
(`flip_table.csv`); a test was not run because most modality gaps are
already known to be of marginal practical significance.

**L10. The PG&E and BC Hydro test bills are public synthetic samples
("SPARKY JOULE", "SOLIN DOE", `0 0000 000`).** This is true of much of
the US/Canadian corpus. Real production bills have richer customer-
identifying fields and tend to have less stylised account-number layouts.
The M2 whitespace-coercion finding may be partly an artefact of synthetic
account numbers.

---

## 10. Synthesis: what this experiment establishes

The experiment is small (n=40) and the headline modality gap is small
(1–2 pp). The transferable findings are:

**S1. On born-digital multilingual bills with a small, well-engineered
prompt, OCR-text mode marginally outperforms vision mode for both
providers.** The aggregate gap is 2.1 pp (Sonnet) and 1.0 pp (GPT-4o),
mostly driven by `provider_name` failures where vision returns the brand
wordmark. The pre-registered H1 (vision matches or exceeds OCR) is not
supported, but the gap is small and partly construct-driven.

**S2. The aggregate gap conceals large field-level offsets that point in
opposite directions.** Vision is ~10–17 pp worse than OCR on
`provider_name` (M1), ~5–10 pp worse on `consumption_amount`/`unit` (M3),
but ~7 pp better on `total_amount_due` for Sonnet (M4) and 26 pp better
on `account_number` for GPT-4o (M2). The choice is not "OCR vs vision";
it is "which fields am I willing to trade off?".

**S3. Modality interacts with provider non-trivially.** GPT-4o's
`account_number` collapse in OCR mode (48.6% vs ≥75% everywhere else) is
a model-specific text-formatting bias, not a property of either pipeline.
Pre-registered H3 (the gap varies by provider) is supported, but the
direction varies field-by-field too.

**S4. Vision is faster and slightly more expensive per document.** Removing
Tesseract saves ~4–5 s per document; the larger token bill from sending
images costs +13–29% per document. H2 is supported as stated; the
operational simplification of removing Tesseract and language-pack
management is real.

**S5. The diagnosis "OCR failure vs LLM failure" attribution heuristic is
adequate for headline numbers but conflates four different mechanism
classes** (Section 5.7). A richer attribution scheme, even by manual
labelling on the ~108 failure rows, would change pipeline-improvement
priorities.

**S6. The biggest accuracy headroom is in field-level modality routing,
not in provider ensembling.** The within-provider modality oracle
(picking whichever modality is right per field) ceilings at 93.6%
(Sonnet) and 92.6% (GPT-4o), a ~4 pp lift over each provider's best
single-modality cell. Provider ensembling alone (oracle pick between
Sonnet and GPT-4o in the same modality) caps at 90.5% / 89.8%, only
~1–2 pp over the best single condition. The 4-way oracle is 95.9%, the
hard upper bound for any combination of these two providers and two
modalities.

**S7. Both pipelines are equally bounded to the first 2 pages of the PDF**
(Section 6), so the modality comparison is fair on page coverage but
neither pipeline is "complete" for long bills. The cheapest single
intervention to gain accuracy on long bills is removing the OCR-side cap
(it is local and effectively free in cost); a more expensive intervention
is sending all pages to vision (cost scales linearly with page count).

These conclusions hold for the corpus as evaluated. They should not be
extrapolated to scanned, photographed, or otherwise non-digital-native
bills, nor to per-field accuracy targets above ~95% (which require either
a richer prompt, fine-tuning, or per-issuer rules — none of which were
tested here).
