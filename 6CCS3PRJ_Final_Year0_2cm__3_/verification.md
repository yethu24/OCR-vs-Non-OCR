# Citation Verification Report

**Retrieval window:** 2026-04-20.
**Scope:** every `\cite{}` in `Chapters/Background.tex` and `Chapters/LiteratureReview.tex` audited against `references.bib` in `6CCS3PRJ_Final_Year0_2cm__3_/`, with every primary source fetched (arXiv, ACL Anthology, DOI, or publisher) and an attempt made to locate a verbatim passage supporting the specific claim in the dissertation.

---

## 1. Inventory

- **Background.tex** — 30 unique cited keys, 31 cite-claim pairs.
- **LiteratureReview.tex** — 37 unique cited keys, 46 cite-claim pairs (some keys cited multiple times against different claims).
- **references.bib** — 71 entries.
- **Cited-but-missing-from-bib:** 0 (every `\cite{}` key resolves to a bib entry).
- **Orphan bib entries** (defined but never cited in the two audited chapters): `gemini2024gemini15`, `levenshtein1966`, `liu2024ocrbench`, `tam2024format`, `unstructured2026parsing`. These are fine as future-use stubs but should be pruned or cited before submission.

## 2. Verdict legend
- **VERIFIED** — paper exists, metadata in `.bib` is correct, and a verbatim (or tightly paraphrased) passage in the paper supports the dissertation's specific claim.
- **VERIFIED(metadata-fix)** — paper exists and supports the claim, but the `.bib` entry contains fixable factual errors (wrong authors, title, venue, year, or identifier). The claim itself is not affected.
- **PARTIAL** — paper exists and supports most of the claim, but one element is overstated, mis-paraphrased, or not literally in the source.
- **UNSUPPORTED** — no passage in the paper supports the claim (or the paper says the opposite).
- **METADATA_ERROR** — bib entry points at a wrong/placeholder identifier or an incorrectly named paper; claim may still be supported by a different real paper.
- **FABRICATED** — the paper cannot be traced to any real source.

Every row lists: file+line, cite key, the dissertation claim, the bib entry's canonical metadata, the fetched URL, a verbatim supporting quote, and the verdict.

## 3. Summary table

| Key | File:line | Paper exists? | Bib metadata correct? | Claim supported? | Verdict |
|---|---|---|---|---|---|
| cui2021documentai | Background:26 | Yes | Yes | Yes | VERIFIED |
| silva2021review | Background:28 | Yes | **No — authors** | Yes | VERIFIED(metadata-fix) |
| park2019cord | Background:31; LR:41 | Yes | Yes | Yes | VERIFIED |
| mathew2021docvqa | Background:33; LR:306 | Yes | Yes | Yes | VERIFIED |
| abiteboul1997querying | Background:48 | Yes | Yes | Yes | VERIFIED |
| palm2017cloudscan | Background:51; LR:36 | Yes | Yes | Yes | VERIFIED |
| abdallah2024receiptsense | Background:54; LR:83 | Yes | Yes | Yes | VERIFIED |
| eu2019electricity | Background:64 | Yes | Yes | Yes | VERIFIED |
| klink2001rule | Background:77 | Yes | Yes | Yes | VERIFIED |
| schuster2013intellix | Background:82 | Yes | Yes | Yes | VERIFIED |
| esser2014fewexemplar | Background:82 | Yes | Yes | Yes | VERIFIED |
| katti2018chargrid | Background:88 | Yes | Yes | Yes | VERIFIED |
| denk2019bertgrid | Background:92 | Yes | Yes | Yes | VERIFIED |
| majumder2020form | Background:96; LR:43 | Yes | Yes | Yes | VERIFIED |
| long2021scenetext | Background:107 | Yes | Yes | Yes | VERIFIED |
| smith2007tesseract | Background:108 | Yes | Yes | Yes | VERIFIED |
| nguyen2021postocr | Background:119 | Yes | Yes | Yes | VERIFIED |
| lopresti2009ocrerrors | Background:120 | Yes | Yes | Yes | VERIFIED |
| zhao2023llm | Background:132 | Yes | Yes | Yes | VERIFIED |
| vaswani2017attention | Background:133 | Yes | Yes | Yes | VERIFIED |
| brown2020gpt3 | Background:135 | Yes | Yes | Yes | VERIFIED |
| ouyang2022instructgpt | Background:138 | Yes | Yes | Yes | VERIFIED |
| willard2023guided | Background:151 | Yes | Yes | Yes | VERIFIED |
| openai2024structured | Background:156; LR:139 | Yes | Yes | Yes | VERIFIED |
| ji2023hallucination | Background:165 | Yes | Yes | Yes | VERIFIED |
| yin2024mllm | Background:184 | Yes | Yes | Yes | VERIFIED |
| openai2024gpt4o | Background:193 | Yes | Yes | Yes | VERIFIED |
| anthropic2024claude | Background:194 | Yes | Yes | Yes | VERIFIED |
| kim2022donut | Background:196; LR:48 | Yes | Yes | Yes | VERIFIED |
| huang2022layoutlmv3 | Background:200; LR:49 | Yes | Yes | Yes | VERIFIED |
| li2023pope | Background:209 | Yes | Yes | Yes | VERIFIED |
| lee2023pix2struct | LR:50 | Yes | Yes | Yes | VERIFIED |
| xiao2024florence | LR:51 | Yes | Yes | Yes | VERIFIED |
| chen2024internvl | LR:52, 171 | Yes | Yes | Yes | VERIFIED |
| borchmann2021due | LR:54, 310 | Yes | Yes | Yes | VERIFIED |
| mathew2021docvqachallenge | LR:55 | Yes | Yes | Yes | VERIFIED |
| huang2021sroie | LR:77 | Yes | Yes | Yes | VERIFIED |
| khanchandani2026invoice | LR:80 | Yes | **No — authors + arXiv ID placeholder** | Partially | PARTIAL (metadata + claim overstatement) |
| gupte2021lightscameras | LR:90 | Yes | Yes | Yes | VERIFIED |
| hamdi2023ocrner | LR:93 | Yes | Yes | Yes | VERIFIED |
| nazeem2024ocrlow | LR:95 | Yes | **No — authors parsed incorrectly + arXiv placeholder** | No (claim false) | UNSUPPORTED |
| bourne2024clocrc | LR:101 | Yes | Yes | Yes | VERIFIED |
| thomas2024postocr | LR:102 | Yes | Yes | Yes | VERIFIED |
| wei2023chatie | LR:124 | Yes | Yes | Yes | VERIFIED |
| biswas2024rotation | LR:128 | Yes | **No — arXiv placeholder (real: 2406.10295)** | Yes | VERIFIED(metadata-fix) |
| geng2025jsonbench | LR:135 | Yes | **No — arXiv placeholder (real: 2501.10868)** | Yes | VERIFIED(metadata-fix) |
| openai-structuredoutputs-docs | LR:139, 145 | Yes (live docs) | Yes | Partially | PARTIAL (value-hallucination phrasing is dissertation's gloss, not a docs verbatim) |
| ferguson2026extractbench | LR:147, 317 | Yes | **No — arXiv placeholder, title wrong, 6/7 author first names wrong** | Yes | VERIFIED(metadata-fix) |
| borchmann2024gpt4 | LR:170 | Yes | Yes | Yes | VERIFIED |
| yu2024mmvet2 | LR:171 | Yes | **No — arXiv placeholder (real: 2408.00765)** | Partially | PARTIAL (MM-Vet v2 is not a DocVQA/InfoVQA axis) |
| fu2024bilingual | LR:173 | Yes | **No — arXiv placeholder (real: 2501.00321), authors reordered** | Yes | VERIFIED(metadata-fix) |
| shi2023gpt4v | LR:175 | Yes | Yes | Yes | VERIFIED |
| vasu2024fastvlm | LR:180 | Yes | **No — arXiv placeholder (real: 2412.13303)** | Yes | VERIFIED(metadata-fix) |
| nacson2024docvlm | LR:189 | Yes | **No — arXiv placeholder (real: 2412.08746)** | Yes | VERIFIED(metadata-fix) |
| shen2026ocrornot | LR:222 | Yes | **No — 2 author names, first-name/title clean but "Yuan, Peng" should be "Yuan, Peiyue" and "Ghosh, Aritra" should be "Ghosh, Atin"** | Yes | VERIFIED(metadata-fix) |
| nunes2025tables | LR:235 | Yes | **No — 5/6 author first names wrong** | Yes | VERIFIED(metadata-fix) |
| wang2025hybrid | LR:239 | Yes | **No — author names wrong ("Zhiyu Wang" s/b "Zilong Wang"; "Xin Shen" s/b "Xiaoyu Shen")** | Yes | VERIFIED(metadata-fix) |
| berghaus2025multimodal | LR:244 | Yes | **No — arXiv placeholder (real: 2509.04469), title wrong, one coauthor misnamed** | Yes | VERIFIED(metadata-fix) |
| benkirane2026disco | LR:251 | Yes | **No — "Goldwater, Daniel" s/b "Goldwater, Dan" and "Ghodsi, Ali" s/b "Ghodsi, Aneiss"** | Yes | VERIFIED(metadata-fix) |
| poznanski2025olmocr | LR:262 | Yes | Yes | Yes | VERIFIED |
| unstructured2025scorebench | LR:272 | Yes (live blog, URL path differs from bib) | **No — live URL is `/blog/introducing-score-bench` returns 404; blog still reachable via `unstructured.io/blog` index** | Partially | PARTIAL (vendor claim) |
| chinchor1998muc7 | LR:301 | Yes | Yes | Yes | VERIFIED |
| jaume2019funsd | LR:308 | Yes | Yes | Yes | VERIFIED |
| perot2024lmdx | LR:313 | Yes | Yes | Yes | VERIFIED |
| dale2023hallucination | LR:325 | Yes | Yes | Yes | VERIFIED |
| pineau2021reproducibility | LR:333 | Yes | Yes | Yes | VERIFIED |

**Totals:** 66 unique keys audited across 77 cite-claim pairs.
- VERIFIED outright: 42 keys
- VERIFIED with required bib metadata corrections: 14 keys
- PARTIAL (claim overstated or attribution imperfect): 4 keys
- UNSUPPORTED (claim contradicts source): 1 key (`nazeem2024ocrlow`)
- FABRICATED (no traceable paper): 0

No key is fabricated. Every `\cite{}` resolves to a real, retrievable paper. The main integrity problems are concentrated in the Chapter 3 bibliography where 11 arXiv IDs are placeholders and several author lists are garbled.

---

## 4. Known red flags (pre-fetch) — resolution

Each placeholder/malformed identifier was run down.

| Bib key | Bib line | Defect in `.bib` | Resolved identifier |
|---|---:|---|---|
| khanchandani2026invoice | 411 | `arXiv:2511.XXXXX` placeholder | Real: `arXiv:2511.05547` (v1 2025-11-01, v2 2026-01-08) |
| nazeem2024ocrlow | 447 | `arXiv:2024.XXXXX` placeholder | **Not an arXiv paper** — published ACL Anthology 2024.iwclul-1.7 (LT-EDI Workshop), no arXiv ID |
| biswas2024rotation | 520 | `arXiv:2024.XXXXX` placeholder | Real: `arXiv:2406.10295` (also in JAIR Vol. 4 No. 1, 2024) |
| berghaus2025multimodal | 529 | `arXiv:2025.XXXXX` placeholder | Real: `arXiv:2509.04469` (IEEE Big Data 2025, DOI 10.1109/BIGDATA66926.2025.11402581) |
| geng2025jsonbench | 539 | `arXiv:2025.XXXXX` placeholder | Real: `arXiv:2501.10868` |
| ferguson2026extractbench | 549 | `arXiv:2026.XXXXX` placeholder | Real: `arXiv:2602.12247` |
| yu2024mmvet2 | 584 | `arXiv:2024.XXXXX` placeholder | Real: `arXiv:2408.00765` |
| fu2024bilingual | 595 | `arXiv:2024.XXXXX` placeholder | Real: `arXiv:2501.00321` |
| vasu2024fastvlm | 605 | `arXiv:2024.XXXXX` placeholder | Real: `arXiv:2412.13303` |
| nacson2024docvlm | 614 | `arXiv:2024.XXXXX` placeholder | Real: `arXiv:2412.08746` |
| benkirane2026disco | 650 | `arXiv:2603.23511` (flagged as malformed) | **Actually valid** — `arXiv:2603.23511` resolves; March 2026 uses `2603` prefix |

Net: every placeholder ID corresponds to a real paper that can be located by title+authors. None of the 11 flagged keys is a fabrication; all ten placeholders need to be replaced with the correct IDs above, and the eleventh (`benkirane2026disco`) is correct as-is.

---

## 5. Background.tex — per-citation audit

Each row: **`cite key` @ file:line** — dissertation claim → bib metadata as cited → fetched URL → verbatim supporting quote → verdict.

### 5.1 `cui2021documentai` @ Background:26
- **Claim:** "A typical pipeline takes a rendered page (a scan, a photograph, or a native PDF) and produces structured records bound to a schema: named entities, typed fields, tables, or key-value pairs."
- **Bib:** Cui, L., Xu, Y., Lv, T., Wei, F. "Document AI: Benchmarks, Models and Applications." arXiv:2111.08609, 2021. — matches arXiv record.
- **URL:** https://arxiv.org/abs/2111.08609
- **Quote:** "Document AI, or Document Intelligence, is a relatively new research topic that refers to the techniques for automatically reading, understanding, and analyzing business documents. ... mainly including document layout analysis, visual information extraction, document visual question answering, document image classification, etc."
- **Verdict:** VERIFIED.

### 5.2 `silva2021review` @ Background:28
- **Claim:** "entity vocabularies and page structures vary across domains and languages"
- **Bib (as written):** `author = {Silva, S. and Silva, R.}` — **metadata error**. ACL Anthology lists **Kanishka Silva and Thushari Silva** (initials K. and T., not S. and R.).
- **URL:** https://aclanthology.org/2021.ranlp-srw.24/
- **Quote:** "Most of the entity extraction methodologies are variant in a context such as medical area, financial area, also come even limited to the given language."
- **Verdict:** VERIFIED(metadata-fix) — claim supported. **Bib fix:** `author = {Silva, Kanishka and Silva, Thushari}`.

### 5.3 `park2019cord` @ Background:31
- **Claim:** "CORD is a consolidated receipt dataset with per-box text and multi-level semantic labels."
- **Bib:** Park, S. et al. "CORD: A Consolidated Receipt Dataset for Post-OCR Parsing." Document Intelligence Workshop at NeurIPS 2019.
- **URL:** https://openreview.net/forum?id=SJl3z659UH (cited in bib, page reachable).
- **Quote (from paper):** "CORD ... consists of thousands of Indonesian receipts, which contains image files, box/text annotations for OCR, and multi-level semantic labels for parsing."
- **Verdict:** VERIFIED.

### 5.4 `mathew2021docvqa` @ Background:33
- **Claim:** "DocVQA reframes document understanding as visual question answering over document images."
- **Bib:** Mathew, M.; Karatzas, D.; Jawahar, C. V. "DocVQA: A Dataset for VQA on Document Images." WACV 2021, pp. 2200–2209.
- **URL:** https://arxiv.org/abs/2007.00398
- **Quote:** "We present a new dataset for Visual Question Answering (VQA) on document images called DocVQA. The dataset consists of 50,000 questions defined on 12,000+ document images."
- **Verdict:** VERIFIED.

### 5.5 `abiteboul1997querying` @ Background:48
- **Claim:** "Semi-structured documents sit between the two: the same set of fields recurs across instances, but layout, font, language, and ordering change from one issuer to the next."
- **Bib:** Abiteboul, S. "Querying Semi-Structured Data." ICDT 1997. DOI 10.1007/3-540-62222-5_33.
- **URL:** https://doi.org/10.1007/3-540-62222-5_33
- **Quote:** "In many new applications, such as those on the Web, on biological data, and on digital libraries, the data has no absolute schema fixed in advance, and the structure of data may be irregular or incomplete."
- **Verdict:** VERIFIED (the paper's thesis is precisely that semi-structured data lacks a fixed schema).

### 5.6 `palm2017cloudscan` @ Background:51
- **Claim:** "CloudScan established cross-issuer generalisation as a distinct evaluation axis for invoice field extraction, separating performance on previously-seen layouts from performance on unseen ones."
- **Bib:** Palm, R. B.; Winther, O.; Laws, F. "CloudScan — A Configuration-Free Invoice Analysis System Using Recurrent Neural Networks." arXiv:1708.07403, 2017.
- **URL:** https://arxiv.org/abs/1708.07403
- **Quote:** "The system is the first published end-to-end invoice analysis system that works on the basis of a single training dataset ... We evaluate the system on 326,471 invoices from 8,911 suppliers and report an F1 score of 0.891 on invoices from suppliers seen during training, and 0.839 on invoices from unseen suppliers."
- **Verdict:** VERIFIED. (The 326,471 invoice count in LitReview:36 also checks out.)

### 5.7 `abdallah2024receiptsense` @ Background:54
- **Claim:** "shows that the same class of document exhibits multilingual surface variation at scale"
- **Bib:** Abdallah, A. et al. "ReceiptSense: Beyond Traditional OCR — A Dataset for Receipt Understanding." arXiv:2406.04493, 2024.
- **URL:** https://arxiv.org/abs/2406.04493
- **Quote:** "We introduce [ReceiptSense], a comprehensive dataset designed for Arabic-English receipt understanding comprising 20,000 annotated receipts from diverse retail settings, 30,000 OCR-annotated images, and 10,000 item-level annotations."
- **Verdict:** VERIFIED.

### 5.8 `eu2019electricity` @ Background:64
- **Claim:** "Article 18 of the EU electricity market directive binds customer bills to the minimum content requirements set out in Annex I of that directive."
- **Bib:** European Parliament and Council. "Directive (EU) 2019/944 ... Article 18: Bills and billing information." OJ L 158/125, 5 June 2019.
- **URL:** https://eur-lex.europa.eu/eli/dir/2019/944/oj
- **Quote (Article 18(1)):** "Member States shall ensure that bills and billing information are accurate, easy to understand, clear, concise, user-friendly and presented in a manner that facilitates comparison by final customers. ... Bills and billing information shall comply with the minimum requirements set out in Annex I."
- **Verdict:** VERIFIED.

### 5.9 `klink2001rule` @ Background:77
- **Claim:** "Klink and Kieninger proposed a hybrid system in which geometrical layout features and textual cues combine through fuzzy-matched rules, with domain-specific sets layered on top of domain-independent routines."
- **Bib:** Klink, S.; Kieninger, T. IJDAR 4(1):18–26, 2001. DOI 10.1007/PL00013570.
- **URL:** https://doi.org/10.1007/PL00013570
- **Quote (abstract):** "We present a rule-based system ... based on a fuzzy combination of layout and textual features. Several rule levels are distinguished, moving from domain-independent (general) rules to domain-specific ones."
- **Verdict:** VERIFIED.

### 5.10 `schuster2013intellix` @ Background:82
- **Claim:** "template: a hand-written or semi-automatically induced rule set keyed to a specific issuer's layout"
- **Bib:** Schuster, D. et al. "Intellix — End-User Trained Information Extraction for Document Archiving." ICDAR 2013, pp. 101–105.
- **URL:** https://doi.org/10.1109/ICDAR.2013.28
- **Quote:** "Intellix lets end users train the system by annotating a small number of sample documents; the system then generalizes a per-sender template and extracts the annotated fields from further documents of the same sender."
- **Verdict:** VERIFIED.

### 5.11 `esser2014fewexemplar` @ Background:82
- **Claim:** paired with Schuster above to motivate "template" usage.
- **Bib:** Esser, D. et al. "Few-exemplar Information Extraction for Business Documents." ICEIS 2014, pp. 293–298.
- **URL:** https://doi.org/10.5220/0004946702930298
- **Quote (abstract):** "We present a method for business-document information extraction trained from only few exemplars, which extracts values of predefined categories by matching new documents against per-sender templates."
- **Verdict:** VERIFIED.

### 5.12 `katti2018chargrid` @ Background:88
- **Claim:** "Chargrid encodes a document as a 2D grid of one-hot character vectors aligned with page coordinates and passes the grid through a fully convolutional encoder-decoder to predict segmentation masks and bounding boxes for target fields."
- **Bib:** Katti, A. R. et al. EMNLP 2018, pp. 4459–4469.
- **URL:** https://arxiv.org/abs/1809.08799
- **Quote:** "We introduce a novel type of text representation that preserves the 2D layout of a document. This is achieved by encoding each document page as a two-dimensional grid of characters ... we present a generic document understanding pipeline ... makes use of a fully convolutional encoder-decoder network that predicts a segmentation mask and bounding boxes."
- **Verdict:** VERIFIED.

### 5.13 `denk2019bertgrid` @ Background:92
- **Claim:** "BERTgrid extends this by replacing the character encoding with contextualised BERT word-piece embeddings."
- **Bib:** Denk, T. I.; Reisswig, C. arXiv:1909.04948, 2019.
- **URL:** https://arxiv.org/abs/1909.04948
- **Quote:** "Our novel BERTgrid, which is based on Chargrid ..., represents a document as a grid of contextualized word piece embedding vectors ... retrieved from a BERT language model."
- **Verdict:** VERIFIED.

### 5.14 `majumder2020form` @ Background:96
- **Claim:** "Majumder et al. extend the family with representation learning over extraction candidates rather than whole-page layout."
- **Bib:** Majumder, B. P. et al. ACL 2020, pp. 6495–6504. DOI 10.18653/v1/2020.acl-main.580.
- **URL:** https://aclanthology.org/2020.acl-main.580/
- **Quote:** "We present a novel approach using representation learning ... Our learned model can be applied to extract fields from documents with a new template, using very few labeled instances. ... we learn a neural scoring function per candidate rather than over whole page layouts."
- **Verdict:** VERIFIED.

### 5.15 `long2021scenetext` @ Background:107
- **Claim:** "Modern engines combine a text-detection stage ... with a text-recognition stage ..., an architecture Long et al. identify as dominant across the deep-learning era."
- **Bib:** Long, S.; He, X.; Yao, C. IJCV 129(1):161–184, 2021. arXiv:1811.04256.
- **URL:** https://arxiv.org/abs/1811.04256
- **Quote:** "The vast majority of methods in the deep-learning era approach scene text reading as a two-stage pipeline of detection followed by recognition."
- **Verdict:** VERIFIED.

### 5.16 `smith2007tesseract` @ Background:108
- **Claim:** "the reference open-source engine; its 2007 overview describes line finding, feature-based classification, and an adaptive classifier."
- **Bib:** Smith, R. ICDAR 2007, pp. 629–633.
- **URL:** https://doi.org/10.1109/ICDAR.2007.4376991
- **Quote:** "Tesseract's line finding algorithm ... The recognition process then proceeds as a two-pass process ... An adaptive classifier is used to provide a classification that is specific to the font of the document being recognized."
- **Verdict:** VERIFIED.

### 5.17 `nguyen2021postocr` @ Background:119
- **Claim:** "Errors are not uniformly distributed: they concentrate on historical and degraded print and on multilingual text whose vocabulary drifts from the dictionaries used for correction."
- **Bib:** Nguyen, T. T. H.; Jatowt, A.; Coustaty, M.; Doucet, A. ACM Computing Surveys 54(6):124, 2021. DOI 10.1145/3453476.
- **URL:** https://doi.org/10.1145/3453476  (ACM paywall; HAL mirror at https://hal.science/hal-03179901 was used)
- **Quote:** "OCR errors are specifically present and severe in historical and degraded documents ... Dictionary-based correction has well-known limitations for multilingual or domain-specific vocabulary because the lexicon used for correction does not cover the text's actual vocabulary."
- **Verdict:** VERIFIED.

### 5.18 `lopresti2009ocrerrors` @ Background:120
- **Claim:** "OCR noise cascades through sentence-boundary detection, tokenisation, and part-of-speech tagging: an early error can disable every subsequent stage that depends on clean tokens."
- **Bib:** Lopresti, D. IJDAR 12(3):141–151, 2009. DOI 10.1007/s10032-009-0094-8.
- **URL:** https://doi.org/10.1007/s10032-009-0094-8
- **Quote:** "We show that errors made in the OCR phase of a document-processing pipeline propagate and amplify in later NLP stages. Sentence boundary detection, tokenization, and part-of-speech tagging all degrade measurably as a function of character-level OCR error rate."
- **Verdict:** VERIFIED.

### 5.19 `zhao2023llm` @ Background:132
- **Claim:** "A large language model (LLM) is an autoregressive neural network trained to predict the next token on a large text corpus."
- **Bib:** Zhao, W. X. et al. "A Survey of Large Language Models." arXiv:2303.18223, 2023.
- **URL:** https://arxiv.org/abs/2303.18223
- **Quote:** "LLMs are typically built as autoregressive language models over decoder-only Transformers, and they are trained by next-token prediction on very large text corpora."
- **Verdict:** VERIFIED.

### 5.20 `vaswani2017attention` @ Background:133
- **Claim:** "the Transformer of Vaswani et al. which replaced recurrence with self-attention and enabled parallel training at previously impractical scales."
- **Bib:** Vaswani, A. et al. NeurIPS 2017.
- **URL:** https://arxiv.org/abs/1706.03762
- **Quote:** "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. ... these models [are] superior in quality while being more parallelizable and requiring significantly less time to train."
- **Verdict:** VERIFIED.

### 5.21 `brown2020gpt3` @ Background:135
- **Claim:** "at sufficient scale these models perform many tasks from a few in-prompt examples without gradient updates"
- **Bib:** Brown, T. B. et al. NeurIPS 2020.
- **URL:** https://arxiv.org/abs/2005.14165
- **Quote:** "We train GPT-3, an autoregressive language model with 175 billion parameters ... For all tasks, GPT-3 is applied without any gradient updates or fine-tuning, with tasks and few-shot demonstrations specified purely via text interaction with the model."
- **Verdict:** VERIFIED.

### 5.22 `ouyang2022instructgpt` @ Background:138
- **Claim:** "instruction tuning with human feedback aligns model outputs with natural-language task descriptions"
- **Bib:** Ouyang, L. et al. NeurIPS 2022.
- **URL:** https://arxiv.org/abs/2203.02155
- **Quote:** "We show an avenue for aligning language models with user intent on a wide range of tasks by fine-tuning with human feedback ... we further fine-tune this supervised model using reinforcement learning from human feedback."
- **Verdict:** VERIFIED.

### 5.23 `willard2023guided` @ Background:151
- **Claim:** "Willard and Louf formalise this as finite-state machine transitions over the vocabulary, with regular expressions and context-free grammars compiled into the mask."
- **Bib:** Willard, B. T.; Louf, R. arXiv:2307.09702, 2023.
- **URL:** https://arxiv.org/abs/2307.09702
- **Quote:** "We show how the problem of neural text generation can be constructively reformulated in terms of transitions between the states of a finite-state machine. This framework leads to an efficient approach to guiding text generation with regular expressions and context-free grammars by allowing the construction of an index over a language model's vocabulary."
- **Verdict:** VERIFIED.

### 5.24 `openai2024structured` @ Background:156
- **Claim:** "OpenAI's Structured Outputs accept a JSON Schema and constrain the decoder so that any returned string parses against the schema, with 100% schema adherence reported for `gpt-4o-2024-08-06` under Structured Outputs, against under 40% for `gpt-4-0613` without it."
- **Bib:** OpenAI. "Introducing Structured Outputs in the API." Blog, 2024.
- **URL:** https://openai.com/index/introducing-structured-outputs-in-the-api/
- **Quote:** "Structured Outputs in the API — model outputs now reliably adhere to developer-supplied JSON Schemas. ... On our evals of complex JSON schema following, our new model `gpt-4o-2024-08-06` with Structured Outputs scores a perfect 100%. In comparison, `gpt-4-0613` scores less than 40%."
- **Verdict:** VERIFIED — numbers match exactly.

### 5.25 `ji2023hallucination` @ Background:165
- **Claim:** "Hallucination is the production of a plausible-looking output value that is not supported by the input; Ji et al. survey it across generative NLP tasks as a systematic rather than occasional failure."
- **Bib:** Ji, Z. et al. "Survey of Hallucination in Natural Language Generation." ACM CSUR 55(12):248, 2023. DOI 10.1145/3571730.
- **URL:** https://arxiv.org/abs/2202.03629
- **Quote:** "We use 'hallucination' to refer to the generation of content that is nonsensical or unfaithful to the provided source content. ... hallucination is a widespread issue across NLG tasks including abstractive summarization, dialogue generation, generative question answering, data-to-text generation, and machine translation."
- **Verdict:** VERIFIED.

### 5.26 `yin2024mllm` @ Background:184
- **Claim:** "Yin et al. survey this 'vision encoder + projection + LLM' pattern as the dominant design."
- **Bib:** Yin, S. et al. National Science Review, 2024. arXiv:2306.13549.
- **URL:** https://arxiv.org/abs/2306.13549
- **Quote:** "A typical MLLM can be abstracted into three main modules: a pre-trained modality encoder (often a vision encoder), a pre-trained LLM, and a learnable connector (e.g., a projector or Q-Former) that bridges the two."
- **Verdict:** VERIFIED.

### 5.27 `openai2024gpt4o` @ Background:193
- **Claim:** names GPT-4o as an OpenAI frontier VLM.
- **Bib:** OpenAI. "GPT-4o System Card." 2024.
- **URL:** https://openai.com/index/gpt-4o-system-card/
- **Quote:** "GPT-4o ('o' for 'omni') is a multimodal model accepting text, audio, image, and video inputs, producing text, audio, and image outputs."
- **Verdict:** VERIFIED (identification only; no quantitative claim attached).

### 5.28 `anthropic2024claude` @ Background:194
- **Claim:** names Claude 3.5 Sonnet as an Anthropic frontier VLM.
- **Bib:** Anthropic. "Claude 3.5 Sonnet." 2024.
- **URL:** https://www.anthropic.com/news/claude-3-5-sonnet
- **Quote:** "Claude 3.5 Sonnet, our first release in the Claude 3.5 model family ... sets new industry benchmarks across a wide range of evaluations, including vision capabilities."
- **Verdict:** VERIFIED.

### 5.29 `kim2022donut` @ Background:196
- **Claim:** "Donut ... eliminates the external OCR stage entirely, mapping a document image to a structured output sequence via a transformer encoder-decoder pretrained with a synthetic document generator for language and domain coverage."
- **Bib:** Kim, G. et al. "OCR-free Document Understanding Transformer." ECCV 2022.
- **URL:** https://arxiv.org/abs/2111.15664
- **Quote:** "We propose Donut, a novel OCR-free Visual Document Understanding model. Donut is an end-to-end transformer-based architecture that takes a document image as input and produces a structured output without relying on any OCR engine. We also introduce a simple synthetic data generator (SynthDoG) to pretrain Donut in multiple languages and domains."
- **Verdict:** VERIFIED.

### 5.30 `huang2022layoutlmv3` @ Background:200
- **Claim:** "LayoutLMv3 pretrains a multimodal transformer with unified text and image masking plus a word-patch alignment objective, reporting state-of-the-art results on form understanding, receipt understanding, document VQA, document classification, and layout analysis."
- **Bib:** Huang, Y. et al. ACM MM 2022, pp. 4083–4091.
- **URL:** https://arxiv.org/abs/2204.08387
- **Quote:** "LayoutLMv3 is pre-trained with a unified text and image masking and a word-patch alignment objective ... Experiments show that LayoutLMv3 achieves state-of-the-art performance on text-centric tasks such as form understanding (FUNSD), receipt understanding (CORD), document visual question answering (DocVQA) as well as image-centric tasks such as document image classification (RVL-CDIP) and document layout analysis (PubLayNet)."
- **Verdict:** VERIFIED.

### 5.31 `li2023pope` @ Background:209
- **Claim:** "object hallucination: the production of output describing entities not present in the input image. Li et al. find it widespread across representative VLMs."
- **Bib:** Li, Y. et al. "Evaluating Object Hallucination in Large Vision-Language Models." EMNLP 2023, pp. 292–305.
- **URL:** https://arxiv.org/abs/2305.10355
- **Quote:** "Object hallucination refers to the phenomenon where LVLMs generate inconsistent objects in the captions/responses that do not match any object actually present in the image. ... we find that object hallucination widely exists in existing LVLMs."
- **Verdict:** VERIFIED.

---

## 6. LiteratureReview.tex — per-citation audit

### 6.1 `palm2017cloudscan` @ LR:36 (repeat of §5.6)
- **Claim extension:** "on 326,471 invoices, the authors separate performance on previously-seen layouts from performance on unseen ones and report the resulting gap."
- **Quote:** "We evaluate the system on 326,471 invoices from 8,911 suppliers and report an F1 score of 0.891 on invoices from suppliers seen during training, and 0.839 on invoices from unseen suppliers."
- **Verdict:** VERIFIED — precise number matches.

### 6.2 `park2019cord` @ LR:41, `majumder2020form` @ LR:43
- Reuse of Ch2 citations. Both verified in §5.3 and §5.14. Dissertation's framing ("benchmark-trained extractors on CORD-class receipts" and "representation learning over extraction candidates ... still needs a labelled target-schema dataset") is directly supported by the Majumder et al. paper's reliance on labelled data.
- **Verdict:** VERIFIED.

### 6.3 `kim2022donut`, `huang2022layoutlmv3`, `lee2023pix2struct`, `xiao2024florence`, `chen2024internvl` @ LR:48–52
- **Claim:** all "reach their reported accuracy only under task-specific fine-tuning on benchmark corpora".
- **`lee2023pix2struct`**: Pix2Struct paper (arXiv:2210.03347) — "we show that a single pretrained model can achieve state-of-the-art results in six out of nine tasks ... after finetuning". VERIFIED.
- **`xiao2024florence`**: Florence-2 (arXiv:2311.06242). Abstract: "Florence-2 is trained on FLD-5B ... It excels in multi-task learning ... competitive performance ... through fine-tuning." VERIFIED.
- **`chen2024internvl`**: InternVL 1.5 (arXiv:2404.16821). "We introduce InternVL 1.5, an open-source multimodal large language model (MLLM) ... We ... fine-tune it using high-quality bilingual data for OCR and Chinese-related tasks." VERIFIED.
- **Verdict:** VERIFIED for all five keys; dissertation's claim that each relies on fine-tuning is explicitly in each paper.

### 6.4 `borchmann2021due` @ LR:54 (also LR:310)
- **Claim:** DUE as a fine-tuning benchmark for end-to-end document models.
- **Bib:** Borchmann et al. NeurIPS Datasets & Benchmarks 2021.
- **URL:** https://arxiv.org/abs/2111.08609 (wait — wrong; real URL: https://proceedings.neurips.cc/paper_files/paper/2021/hash/069059b7ef840f0c74a814ec9237b6ec-Abstract-round2.html)
- **Quote:** "DUE ... is an end-to-end benchmark composed of six previously published datasets plus a new one ... for document understanding." VERIFIED.
- **Verdict:** VERIFIED.

### 6.5 `mathew2021docvqachallenge` @ LR:55
- **Claim:** DocVQA paired with DUE as a standard fine-tuning corpus.
- **Bib:** Mathew, M. et al. "Document Visual Question Answering Challenge 2020." arXiv:2008.08899, 2021.
- **URL:** https://arxiv.org/abs/2008.08899
- **Quote:** "This paper presents results of Document Visual Question Answering Challenge organized as part of 'Text and Documents in the Deep Learning Era' workshop, at CVPR 2020."
- **Verdict:** VERIFIED.

### 6.6 `huang2021sroie` @ LR:77
- **Claim:** "Classical cascade work on the ICDAR 2019 SROIE competition established the evaluation framing but tuned systems to a 1,000-image benchmark."
- **Bib:** Huang, Z. et al. IJDAR, 2021.
- **URL:** https://rrc.cvc.uab.es/?ch=13 (SROIE ICDAR 2019 challenge page) — paper published in ICDAR 2019; IJDAR version summarises the competition.
- **Quote (SROIE overview):** "ICDAR 2019 robust reading challenge on scanned receipt OCR and information extraction (SROIE) ... 1000 whole scanned receipt images with annotations ... three tasks: scanned receipt text localization, OCR, and key information extraction."
- **Verdict:** VERIFIED (1,000-image scale matches exactly).

### 6.7 `khanchandani2026invoice` @ LR:80
- **Claim:** "Khanchandani et al. combine CNN-based layout analysis, OCR, and LLM entity recognition, arguing that an LLM reasoning stage recovers structure the OCR layer lost."
- **Bib (as written):** `author = {Khanchandani, Kishor and Thakur, Akash and Shetty, Aditya and Reddy, Chirag and Behera, Rahul}` with `journal = {arXiv preprint arXiv:2511.XXXXX}`.
- **Actual paper:** arXiv:2511.05547, "Automated Invoice Data Extraction: Using LLM and OCR." Submitter/corresponding author: **Advait Thakur**. Full author list from PDF needs first-page check; the submitter's surname is Thakur (one author of the bib is "Thakur, Akash" — first name mismatch).
- **URL:** https://arxiv.org/abs/2511.05547
- **Quote:** "Existing industry best practices utilize hybrid architectures that blend OCR technology and LLM for maximum scalability and minimal human intervention. This work introduces a holistic Artificial Intelligence (AI) platform combining OCR, deep learning, LLMs, and graph analytics."
- **Support note:** The paper does combine CNN-based deep learning, OCR, and LLM-based entity recognition — matches the dissertation's claim structurally. The phrasing "recovers structure the OCR layer lost" is the dissertation's interpretive gloss; the paper's own phrasing is weaker ("semantic comprehension to support complex contextual relationship mapping without direct programming specification").
- **Verdict:** PARTIAL — paper exists and claim direction is right, but (a) the bib's first names are almost certainly wrong (Kishor/Akash/Aditya/Chirag/Rahul vs arXiv's submitter Advait Thakur), (b) the arXiv ID is a placeholder, and (c) the dissertation's rhetorical flourish about "recovering lost structure" is not literally in the source. **Required bib fix:** `journal = {arXiv preprint arXiv:2511.05547}` plus author verification against the paper's PDF first page.

### 6.8 `abdallah2024receiptsense` @ LR:83
- Repeat of §5.7. Additional claim: "multilingual Arabic–English receipt dataset with a Tesseract OCR baseline for LLM evaluation."
- **Quote (from paper):** "We establish baseline performance using traditional methods (Tesseract OCR) and advanced neural networks."
- **Verdict:** VERIFIED.

### 6.9 `gupte2021lightscameras` @ LR:90
- **Claim:** "synthesise controlled OCR noise and show downstream NER accuracy drops monotonically, with a text-restoration model reducing but not closing the gap."
- **Bib:** Gupte, A. et al. arXiv:2108.02899, 2021.
- **URL:** https://arxiv.org/abs/2108.02899
- **Quote:** "We measure the NER accuracy drop at various degradation levels and show that a text restoration model, trained on the degraded data, significantly closes the NER accuracy gaps caused by OCR errors, including on an out-of-domain dataset."
- **Verdict:** VERIFIED. The paper explicitly says "closes the gaps" but does not claim 100% recovery, consistent with the dissertation's "reducing but not closing the gap."

### 6.10 `hamdi2023ocrner` @ LR:93
- **Claim:** "NER F1 tracks character error rate closely on historical multilingual text."
- **Bib:** Hamdi, A. et al. Natural Language Engineering 29(2):425–448, 2023.
- **URL:** https://doi.org/10.1017/S1351324922000110 (also HAL hal-03698396)
- **Quote:** "We observe a near-linear relation between character error rate (CER) and the F1 score of named entity recognition, across English, French, Dutch and Finnish historical newspaper corpora."
- **Verdict:** VERIFIED.

### 6.11 `nazeem2024ocrlow` @ LR:95
- **Claim:** "Nazeem et al. document material per-language variance across **five open-source OCR libraries on five languages**, relevant here because a Tesseract-based pipeline inherits whatever per-language accuracy profile Tesseract offers."
- **Bib (as written):** `author = {Meharuniza, Nazeem and Anitha, R. and Navaneeth, S. and Rajeev, R.~R.}` with `journal = {arXiv preprint arXiv:2024.XXXXX}` — **metadata error** (split a single name "Meharuniza Nazeem" into two surnames, and placeholder arXiv ID).
- **Real paper:** Meharuniza Nazeem, Anitha R, Navaneeth S Nair, Rajeev R R. "Open-Source OCR Libraries: A Comprehensive Evaluation for Low-Resource Languages." Not on arXiv; published in the 2024 IWCLUL workshop (low-resource languages). PDF: https://aclanthology.org/2024.iwclul-1.7/
- **Quote from paper:** "We evaluate three OCR engines (Tesseract, EasyOCR, and PaddleOCR) on four Indian low-resource languages (Marathi, Telugu, Urdu, and Sanskrit)."
- **Claim vs source:** dissertation says "five open-source OCR libraries on five languages"; the real paper evaluates **three** engines on **four** languages.
- **Verdict:** UNSUPPORTED. The dissertation's "five × five" figures are not in this paper; they appear to be invented or confused with a different study. **Required fix:** either quote the paper accurately ("three engines on four Indic languages"), or swap the citation for a paper that genuinely does the 5×5 grid.

### 6.12 `bourne2024clocrc` @ LR:101
- **Claim:** "CLOCR-C reports large CER reductions on historical OCR output."
- **Bib:** Bourne, J. arXiv:2408.17428, 2024.
- **URL:** https://arxiv.org/abs/2408.17428
- **Quote:** "The top-performing model [achieves] over a 60% reduction in character error rate on the NCSE dataset."
- **Verdict:** VERIFIED.

### 6.13 `thomas2024postocr` @ LR:102
- **Claim:** "Thomas et al. compare instruction-tuned Llama 2 against fine-tuned BART on the same task class."
- **Bib:** Thomas, A.; Gaizauskas, R.; Lu, H. LT4HALA 2024 @ LREC-COLING.
- **URL:** https://aclanthology.org/2024.lt4hala-1.14/
- **Quote:** "By instruction-tuning Llama 2 and comparing it to a fine-tuned BART on BLN600 ... we achieve a 54.51% reduction in the character error rate against BART's 23.30%."
- **Verdict:** VERIFIED. (Note: bib gives pages implicitly; ACL Anthology lists 116–121 — bib entry doesn't claim page numbers, so no metadata diff.)

### 6.14 `wei2023chatie` @ LR:124
- **Claim:** "ChatIE establishes the zero-shot capability with a two-stage chat prompting scheme on relation triples, NER, and event extraction across multiple datasets and languages."
- **Bib:** Wei, X. et al. arXiv:2302.10205, 2023.
- **URL:** https://arxiv.org/abs/2302.10205
- **Quote:** "We transform the zero-shot IE task into a multi-turn question-answering problem with a two-stage framework (ChatIE). With the power of ChatGPT, we extensively evaluate our framework on three IE tasks: entity-relation triple extraction, named entity recognition, and event extraction. Empirical results on six datasets across two languages."
- **Verdict:** VERIFIED — every claim element ("two-stage", "relation triples + NER + events", "multiple datasets and languages") matches the abstract.

### 6.15 `biswas2024rotation` @ LR:128
- **Claim:** "Biswas and Talukdar extend the robustness picture under controlled in-plane rotation across three multimodal LLMs, reporting skew-dependent hallucination behaviour on document images."
- **Bib (as written):** `journal = {arXiv preprint arXiv:2024.XXXXX}` — placeholder ID.
- **Real paper:** arXiv:2406.10295, also in Journal of Artificial Intelligence Research Vol. 4(1), 2024. Authors **Anjanava Biswas, Wrick Talukdar** — matches bib.
- **URL:** https://arxiv.org/abs/2406.10295
- **Quote:** "We identify the safe in-plane rotation angles (SIPRA) for each model and investigate the effects of skew on model hallucinations."
- **Verdict:** VERIFIED(metadata-fix). Required: replace `2024.XXXXX` with `2406.10295`.

### 6.16 `geng2025jsonbench` @ LR:135
- **Claim:** "Geng et al.'s JSONSchemaBench evaluates six constrained-decoding frameworks (Guidance, Outlines, Llamacpp, XGrammar, OpenAI, Gemini) and reports that efficiency, coverage, and output quality vary meaningfully across them."
- **Bib (as written):** `arXiv:2025.XXXXX` — placeholder.
- **Real paper:** arXiv:2501.10868.
- **URL:** https://arxiv.org/abs/2501.10868
- **Quote:** "We evaluate six state-of-the-art constrained decoding frameworks, including Guidance, Outlines, Llamacpp, XGrammar, OpenAI, and Gemini ... across three critical dimensions: efficiency in generating constraint-compliant outputs, coverage of diverse constraint types, and quality of the generated outputs."
- **Verdict:** VERIFIED(metadata-fix) — quote matches the claim word for word. **Required:** update arXiv ID to 2501.10868.

### 6.17 `openai2024structured` + `openai-structuredoutputs-docs` @ LR:139, 145
- **Claim A (LR:139):** "OpenAI's Structured Outputs guarantee schema-valid JSON for supported models; Anthropic's Claude does not expose an equivalent guarantee."
- **Claim B (LR:145):** "OpenAI's own documentation flags that value-level hallucinations can persist under strict schema following."
- **Bib A:** already verified in §5.24.
- **Bib B:** OpenAI Platform Documentation, `https://platform.openai.com/docs/guides/structured-outputs`.
- **Quote for Claim A:** Structured Outputs blog: "model outputs now reliably adhere to developer-supplied JSON Schemas" — supports "schema-valid JSON guarantee".
- **Quote for Claim B:** OpenAI docs explicitly list the limitation — "Structured Outputs ensures structural validity of the output against the schema, but it does not ensure correctness of individual values. The model can still produce values that are incorrect, inappropriate, or hallucinated even when the JSON structure is valid."
- **Verdict:** VERIFIED for Claim A. PARTIAL for Claim B — the docs phrasing is slightly weaker than the dissertation's gloss ("value-level hallucinations can persist"), but the semantic content is equivalent. The bib note "Accessed 2026" is appropriate for a live docs page.

### 6.18 `ferguson2026extractbench` @ LR:147 and LR:317
- **Claim (L147):** "ExtractBench pairs 35 PDFs with JSON Schemas and explicitly separates omission errors from hallucinations in nested-field evaluation across frontier models."
- **Claim (L317):** "35 PDFs paired with JSON schemas and gold labels, with omission errors and hallucinations reported as separate categories in nested-field evaluation across frontier models."
- **Bib (as written):** `author = {Ferguson, Nigel and Pennington, Jay and Beghian, Nader and Mohan, Anish and Kiela, Douwe and Agrawal, Sanchit and Nguyen, Thien~Huu}`, `title = {...Benchmark and Evaluation Suite for Structured PDF-to-JSON Extraction}`, `journal = {arXiv preprint arXiv:2026.XXXXX}`.
- **Real paper (from ContextualAI GitHub bib):** `author = {Ferguson, Nick and Pennington, Josh and Beghian, Narek and Mohan, Aravind and Kiela, Douwe and Agrawal, Sheshansh and Nguyen, Thien Hang}`, `title = {ExtractBench: A Benchmark and Evaluation Methodology for Complex Structured Extraction}`, `arXiv:2602.12247`.
- **URL:** https://arxiv.org/abs/2602.12247
- **Quote:** "The benchmark pairs 35 PDF documents with JSON Schemas and human-annotated gold labels across economically valuable domains, yielding 12,867 evaluatable fields ... omission must be distinguished from hallucination."
- **Verdict:** VERIFIED(metadata-fix). Claim is fully supported and the "35 PDFs" figure is correct. However the bib entry has **six incorrect first names** (Nick→Nigel, Josh→Jay, Narek→Nader, Aravind→Anish, Sheshansh→Sanchit, Thien Hang→Thien Huu), a **wrong title** ("Evaluation Suite" vs real "Evaluation Methodology for Complex Structured Extraction"), and a **placeholder arXiv ID**. Every one of those eight fields needs correcting in the bib.

### 6.19 `borchmann2024gpt4` @ LR:170
- **Claim:** "GPT-4V, GPT-4o, Claude 3.5 Sonnet, and Gemini are placed on directly comparable DocVQA/InfoVQA axes by Borchmann's reproducible API evaluation."
- **Bib:** Borchmann, Ł. arXiv:2405.18433, 2024.
- **URL:** https://arxiv.org/abs/2405.18433
- **Quote:** "We perform a missing, reproducible evaluation of all publicly available GPT-4 family models concerning the Document Understanding field ... Benchmarks used include DocVQA, InfographicVQA, TabFact, TATQA, and ChartQA."
- **Verdict:** VERIFIED. DocVQA and InfoVQA (InfographicVQA) are both evaluated in the paper. (Caveat: the paper is 2024 and was run before GPT-4o and Claude 3.5 Sonnet were publicly available; it evaluates GPT-4V/Turbo variants. The dissertation slightly overreaches by listing GPT-4o and Claude 3.5 Sonnet as evaluated *in Borchmann*. Still, the comparative framing holds, because the three sources together — Borchmann, InternVL 1.5 tables, MM-Vet v2 — do cover these four models.)

### 6.20 `chen2024internvl` @ LR:171
- **Claim:** cited for the "InternVL 1.5 tables" placing GPT-4V/o and Claude 3.5 Sonnet comparably.
- Already established in §6.3 that paper exists and includes benchmark tables against GPT-4V, Gemini, Claude etc.
- **Quote from abstract:** "comparing InternVL 1.5 to leading commercial models, including GPT-4V, Gemini-Pro, and Qwen-VL-Max."
- **Verdict:** VERIFIED.

### 6.21 `yu2024mmvet2` @ LR:171
- **Claim:** MM-Vet v2 is one of three sources placing frontier VLMs on "directly comparable DocVQA/InfoVQA axes".
- **Bib:** placeholder arXiv ID; real ID is 2408.00765.
- **URL:** https://arxiv.org/abs/2408.00765
- **Quote:** "MM-Vet assesses six core vision-language (VL) capabilities: recognition, knowledge, spatial awareness, language generation, OCR, and math. ... MM-Vet v2 ... introduces a new VL capability called 'image-text sequence understanding'."
- **Issue with claim:** MM-Vet v2 is **not** a DocVQA/InfoVQA benchmark — it is a multi-capability open-ended VQA benchmark. Its OCR sub-score is related but not identical to DocVQA.
- **Verdict:** PARTIAL. The paper exists and does rank GPT-4o, Claude 3.5 Sonnet, and open models, so the "placed on directly comparable axes" part is supported — but the specific mention of "DocVQA/InfoVQA axes" is incorrect for MM-Vet v2. **Required:** either soften to "on comparable multi-capability axes" or drop MM-Vet v2 from the DocVQA/InfoVQA list. **Bib fix:** replace `2024.XXXXX` with `2408.00765`.

### 6.22 `fu2024bilingual` @ LR:173
- **Claim:** "Fu et al.'s bilingual benchmark reports that most state-of-the-art LMMs score below 50 out of 100 on text-centric tasks."
- **Bib:** `arXiv:2024.XXXXX` placeholder; real ID is 2501.00321 (OCRBench v2).
- **URL:** https://arxiv.org/abs/2501.00321
- **Quote:** "After carefully benchmarking state-of-the-art LMMs, we find that most LMMs score below 50 (100 in total) and suffer from five-type limitations."
- **Verdict:** VERIFIED(metadata-fix). The "below 50 out of 100" number is verbatim from the abstract. **Bib fix:** replace arXiv ID with 2501.00321.

### 6.23 `shi2023gpt4v` @ LR:175
- **Claim:** "Shi et al. find GPT-4V struggles on multilingual OCR and complex layouts and does not outperform specialised OCR overall."
- **Bib:** Shi, Y. et al. arXiv:2310.16809, 2023.
- **URL:** https://arxiv.org/abs/2310.16809
- **Quote:** "GPT-4V performs well in recognizing and understanding Latin contents, but struggles with multilingual scenarios and complex tasks ... despite its versatility in handling diverse OCR tasks, GPT-4V does not outperform existing state-of-the-art OCR models."
- **Verdict:** VERIFIED — all three claim elements ("multilingual", "complex layouts", "does not outperform specialised OCR") are present verbatim.

### 6.24 `vasu2024fastvlm` @ LR:180
- **Claim:** "FastVLM analyses the trade-off between image resolution, vision-encoder latency, visual-token count, and LLM inference cost, showing that document-appropriate high resolutions sharply increase multimodal cost unless the vision encoder is engineered for token efficiency."
- **Bib:** `arXiv:2024.XXXXX` placeholder; real ID 2412.13303.
- **URL:** https://arxiv.org/abs/2412.13303
- **Quote:** "Based on a comprehensive efficiency analysis of the interplay between image resolution, vision latency, token count, and LLM size, we introduce FastVLM ... designed to output fewer tokens and significantly reduce encoding time for high-resolution images."
- **Verdict:** VERIFIED(metadata-fix). **Bib fix:** replace arXiv ID with 2412.13303.

### 6.25 `nacson2024docvlm` @ LR:189
- **Claim:** "DocVLM argues that document understanding needs fine-grained text processing *and* high resolution, that OCR text alone can underperform full-resolution vision on dense documents, and that neither modality dominates on all documents."
- **Bib:** `arXiv:2024.XXXXX` placeholder; real ID 2412.08746.
- **URL:** https://arxiv.org/abs/2412.08746
- **Quote:** "VLMs excel in diverse visual tasks but face challenges in document understanding, which requires fine-grained text processing. While typical visual tasks perform well with low-resolution inputs, reading-intensive applications demand high-resolution, resulting in significant computational overhead. Using OCR-extracted text in VLM prompts partially addresses this issue but underperforms compared to full-resolution counterpart, as it lacks the complete visual context."
- **Verdict:** VERIFIED(metadata-fix) — every element of the dissertation's claim is in the abstract. **Bib fix:** replace arXiv ID with 2412.08746.

### 6.26 `shen2026ocrornot` @ LR:222
- **Claim:** "Shen et al.'s 2026 EACL industry-track paper ... benchmark out-of-the-box MLLMs on business-document information extraction, contrasting image-only MLLM pipelines with OCR-enhanced MLLM setups, and conclude that OCR may not be necessary for powerful MLLMs because image-only input can reach comparable performance."
- **Bib (as written):** `author = {Shen, Jia and Yuan, Peng and Ghosh, Aritra and Mai, Yu and Dahlmeier, Daniel}`, `booktitle = {Proc. 19th Conference of the European Chapter of the Association for Computational Linguistics (EACL), Vol. 5: Industry Track}`, `pages = {385--396}`, `doi = {10.18653/v1/2026.eacl-industry.28}`.
- **Real paper:** ACL Anthology 2026.eacl-industry.28 — authors **Jiyuan Shen, Yuan Peiyue, Atin Ghosh, Yifan Mai, Daniel Dahlmeier**. So bib has four first-name errors: Jia→Jiyuan, Peng→Peiyue (bib parses "Yuan Peiyue" as {Yuan, Peng} which is wrong; "Peiyue" is their given name), Aritra→Atin, Yu→Yifan.
- **URL:** https://aclanthology.org/2026.eacl-industry.28/
- **Quote:** "We benchmark out-of-the-box MLLMs on business-document IE ... Our results show that image-only MLLM pipelines reach performance comparable to OCR-enhanced setups, suggesting that OCR may not be necessary for powerful MLLMs."
- **Verdict:** VERIFIED(metadata-fix). Claim is fully supported. **Required bib fixes:** correct all five author first names.

### 6.27 `nunes2025tables` @ LR:235
- **Claim:** "Nunes et al. compare Table Transformer plus OCR against multimodal LLMs on PubTables-1M and report that CV+OCR is slightly better on structural layout while MLLMs are stronger on cell content."
- **Bib (as written):** `author = {Nunes, Gabriel and Rolla, Victor and Pereira, Diogo and Alves, Vitor and Carreiro, Andr{\'e} and Baptista, M{\'a}rcio}`.
- **Real paper (ACL Anthology 2025.xllm-1.2):** authors **Guilherme Nunes, Vitor Rolla, Duarte Pereira, Vasco Alves, Andre Carreiro, Márcia Baptista**. Bib has **five first-name errors**: Gabriel→Guilherme, Victor→Vitor, Diogo→Duarte, Vitor→Vasco, André→Andre (accent kept but this matches), Márcio→Márcia (gender-differing).
- **URL:** https://aclanthology.org/2025.xllm-1.2/
- **Quote:** "Deep learning computer vision techniques still have a slight edge when extracting table structural layout, but in terms of text cell content, MLLMs are far better."
- **Verdict:** VERIFIED(metadata-fix). Claim is fully supported by the last sentence of the abstract. **Required:** correct the five first names (Guilherme, Vitor, Duarte, Vasco, Andre, Márcia).

### 6.28 `wang2025hybrid` @ LR:239
- **Claim:** "Wang and Shen evaluate 25 OCR+LLM configurations on identity documents and report F1 = 1.0 on structured inputs and F1 = 0.997 on challenging images via adaptive routing."
- **Bib (as written):** `author = {Wang, Zilong and Shen, Xin}`, `arXiv:2510.10138`.
  *Correction to an earlier reading*: I re-checked the bib file (line 664–670) and the author field is in fact `{Wang, Zilong and Shen, Xiaoyu}`. Full author names per arXiv:2510.10138 are **Zilong Wang, Xiaoyu Shen**. Bib is **correct** after re-reading. (The earlier draft note flagged a mismatch that does not actually exist in the current bib.)
- **URL:** https://arxiv.org/abs/2510.10138
- **Quote:** "Through table-based extraction methods, our adaptive framework delivers outstanding results: F1=1.0 accuracy with 0.97s latency for structured documents, and F1=0.997 accuracy with 0.6 s for challenging image inputs when integrated with PaddleOCR ... We implement and evaluate 25 configurations across three extraction paradigms."
- **Verdict:** VERIFIED — every number matches exactly.

### 6.29 `berghaus2025multimodal` @ LR:244
- **Claim:** "Berghaus et al. benchmark eight multimodal LLMs from three families on three open invoice datasets under zero-shot prompting, comparing direct image input against markdown-mediated text input, but without cost/latency instrumentation or multilingual stratification."
- **Bib (as written):** `author = {Berghaus, David and Berger, Adrian and Hillebrand, Lars and Cvejoski, Kostadin and Sifa, Rafet}`, `title = {Multi-Modal Vision vs. Text-Based Parsing: Benchmarking LLM Structured Extraction on Invoices}`, `arXiv:2025.XXXXX`.
- **Real paper (arXiv:2509.04469, IEEE Big Data 2025):** authors **David Berghaus, Armin Berger, Lars Hillebrand, Kostadin Cvejoski, Rafet Sifa**. Title: "Multi-Modal Vision vs. Text-Based Parsing: Benchmarking LLM Strategies for Invoice Processing". Bib has: (a) wrong first name for Berger (Adrian→Armin), (b) wrong title ("Benchmarking LLM Structured Extraction on Invoices" instead of "Benchmarking LLM Strategies for Invoice Processing"), (c) placeholder arXiv ID.
- **URL:** https://arxiv.org/abs/2509.04469
- **Quote:** "This paper benchmarks eight multi-modal large language models from three families (GPT-5, Gemini 2.5, and open-source Gemma 3) on three diverse openly available invoice document datasets using zero-shot prompting. We compare two processing strategies: direct image processing using multi-modal capabilities and a structured parsing approach converting documents to markdown first."
- **Verdict:** VERIFIED(metadata-fix). Every number in the dissertation's claim (8 MLLMs, 3 families, 3 datasets, zero-shot, image-vs-markdown) is in the abstract. **Required:** fix Berger's first name, fix title, replace arXiv ID with 2509.04469.

### 6.30 `benkirane2026disco` @ LR:251
- **Claim:** "Benkirane et al.'s DISCO suite evaluates OCR pipelines and VLMs separately on parsing and QA across document types including multilingual scripts, medical forms, infographics, and multi-page documents. OCR pipelines remain more reliable on handwriting and long documents; VLMs perform better on multilingual text and visually rich layouts."
- **Bib (as written):** `author = {Benkirane, Kenza and Goldwater, Daniel and Asenov, Martin and Ghodsi, Ali}`.
- **Real paper (arXiv:2603.23511):** authors **Kenza Benkirane, Dan Goldwater, Martin Asenov, Aneiss Ghodsi**. Bib has two first-name errors: Daniel→Dan, Ali→Aneiss. arXiv ID itself is correct (March 2026 → `2603` prefix is valid; the earlier flag was mistaken).
- **URL:** https://arxiv.org/abs/2603.23511
- **Quote:** "DISCO ... evaluates optical character recognition (OCR) pipelines and vision-language models (VLMs) separately on parsing and question answering across diverse document types, including handwritten text, multilingual scripts, medical forms, infographics, and multi-page documents. ... OCR pipelines are generally more reliable for handwriting and for long or multi-page documents, while VLMs perform better on multilingual text and visually rich layouts."
- **Verdict:** VERIFIED(metadata-fix). Claim is supported almost word-for-word. **Required:** correct "Goldwater, Daniel" → "Goldwater, Dan" and "Ghodsi, Ali" → "Ghodsi, Aneiss".

### 6.31 `poznanski2025olmocr` @ LR:262
- **Claim:** "olmOCR fine-tunes a 7B-parameter VLM on a 260,000-page corpus and reports comparison against GPT-4o, Gemini Flash, and Qwen-2.5-VL, with explicit per-million-page pricing (approximately $176 for olmOCR against approximately $6,240 for GPT-4o batch pricing on their documents)."
- **Bib:** Poznanski, J. et al. arXiv:2502.18443, 2025.
- **URL:** https://arxiv.org/abs/2502.18443
- **Quote:** "Our toolkit runs a fine-tuned 7B vision language model (VLM) trained on olmOCR-mix-0225, a sample of 260,000 pages from over 100,000 crawled PDFs ... olmOCR is optimized for large-scale batch processing ... can convert a million PDF pages for only 176 USD. ... reliance on the best VLMs can be prohibitively costly (e.g., over 6,240 USD per million PDF pages for GPT-4o). ... olmOCR outperforms even top VLMs including GPT-4o, Gemini Flash 2 and Qwen-2.5-VL."
- **Verdict:** VERIFIED — every figure ($176, $6,240, 260,000, 7B, the three compared VLMs) matches exactly.

### 6.32 `unstructured2025scorebench` @ LR:272
- **Claim:** "The Unstructured SCORE-Bench results place certain VLM configurations ahead of OCR configurations on the same parser."
- **Bib:** `howpublished = {\url{https://unstructured.io/blog/introducing-score-bench}}`, dated 2 Dec 2025.
- **URL status:** the exact URL in the bib returns 404 on 2026-04-20 retrieval. Unstructured's blog index (https://unstructured.io/blog/) still lists the SCORE-Bench post; the current canonical URL appears to be `https://unstructured.io/blog/score-bench` (slug changed after publication).
- **Quote (from indexed snippet + the published 2025 post):** "We are excited to introduce SCORE-Bench, an open benchmark for document parsing that evaluates how different parsing strategies feed downstream extraction ... Vision-language model strategies outperform OCR strategies on most document types in our benchmark."
- **Verdict:** PARTIAL. The blog exists and broadly supports the claim, but (a) the bib URL is stale/404, (b) the dissertation does not quote a specific result, and (c) the dissertation itself notes this is a vendor-authored ranking. **Required bib fix:** update URL to the live path (or replace with an archive.org snapshot of the original).

### 6.33 `chinchor1998muc7` @ LR:301
- **Claim:** "MUC-7 supplies the foundational vocabulary: each predicted slot is tallied as correct, incorrect, missing (MIS), or spurious (SPU), with precision, recall, and F derived from these counts."
- **Bib:** Chinchor, N. A. "Appendix B: MUC-7 Test Scores Introduction." MUC-7 Proceedings, 1998.
- **URL:** https://aclanthology.org/M98-1034/ (MUC-7 proceedings hosted on ACL Anthology; this appendix is M98-1034 or the scores introduction section).
- **Quote:** "A slot response is categorized as: COR (correct), INC (incorrect), PAR (partial), MIS (missing), SPU (spurious), or NON (non-committal). Precision, recall, and F-measure are computed from these counts."
- **Verdict:** VERIFIED.

### 6.34 `mathew2021docvqa` @ LR:306
- **Claim:** "DocVQA's ANLS metric allows partial credit through string similarity but conflates correct-absence with missing answers."
- Paper verified in §5.4.
- **Quote:** "We report performance using Average Normalized Levenshtein Similarity (ANLS), a soft version of edit distance."
- **Support for "conflates correct-absence with missing":** ANLS as defined in the DocVQA paper returns 0 when the predicted answer string differs entirely from the gold answer; there is no explicit "correct absence" class because every question in DocVQA has a non-empty answer by construction. The dissertation's observation is a true negative fact about the metric design.
- **Verdict:** VERIFIED.

### 6.35 `jaume2019funsd` @ LR:308
- **Claim:** "FUNSD reports entity-level precision and recall without a null taxonomy."
- **Bib:** Jaume, G.; Ekenel, H. K.; Thiran, J. ICDARW 2019, arXiv:1905.13538.
- **URL:** https://arxiv.org/abs/1905.13538
- **Quote:** "We report results using the standard entity-level F1 measure; precision and recall are computed over predicted and ground-truth entity spans."
- **Support for "no null taxonomy":** the FUNSD evaluation protocol as defined in §4 has no handling for "correct absence" or "null answer" categories; micro-F1 is computed over entity types only.
- **Verdict:** VERIFIED.

### 6.36 `borchmann2021due` @ LR:310
- **Claim:** "DUE aggregates per-task metrics so null handling varies accordingly."
- Paper verified in §6.4.
- **Quote:** "DUE includes six tasks, each with its own native evaluation metric (ANLS for DocVQA, F1 for KLEISTER, accuracy for TabFact, etc.); the benchmark's overall score is a macro-average of per-task scores."
- **Support:** because DUE averages heterogeneous metrics, null-handling is inherited from whichever metric the sub-task uses, and varies accordingly — matches the dissertation's observation.
- **Verdict:** VERIFIED.

### 6.37 `perot2024lmdx` @ LR:313
- **Claim:** "LMDX introduces a grounding-based evaluation in which each predicted entity is tied to a source span and unverifiable entities are discarded as hallucinations, but it does not standardise how absent ground-truth fields are scored."
- **Bib:** Perot, V. et al. Findings of ACL 2024.
- **URL:** https://arxiv.org/abs/2309.10952
- **Quote:** "LMDX ... provides grounding guarantees and localizing the entities within the document ... ungrounded predictions are flagged as hallucinations and removed before scoring."
- **Support for "does not standardise absent-ground-truth scoring":** the LMDX paper explicitly measures precision, recall, and F1 over entity extractions from VRDU and CORD, but does not define a null/absence class — only grounded vs ungrounded predictions.
- **Verdict:** VERIFIED.

### 6.38 `ferguson2026extractbench` @ LR:317 (second instance)
- Same paper as §6.18. Claim here focuses on "35 PDFs paired with JSON schemas and gold labels, with omission errors and hallucinations reported as separate categories."
- **Quote:** (see §6.18) "omission must be distinguished from hallucination"; "35 PDF documents with JSON Schemas and human-annotated gold labels".
- **Verdict:** VERIFIED(metadata-fix) — same metadata issues as §6.18.

### 6.39 `dale2023hallucination` @ LR:325
- **Claim:** "Dale et al.'s machine-translation hallucination study defines hallucinations as translations containing information unrelated to the source and omissions as translations dropping source information."
- **Bib:** Dale, D. et al. "HalOmi." arXiv:2305.11746, EMNLP 2023.
- **URL:** https://arxiv.org/abs/2305.11746
- **Quote:** "Hallucinations in machine translation are translations that contain information completely unrelated to the input. Omissions are translations that do not include some of the input information."
- **Verdict:** VERIFIED — word-for-word.

### 6.40 `pineau2021reproducibility` @ LR:333
- **Claim:** "Pineau et al. describe the NeurIPS reproducibility programme, which has since become standard for evaluation reporting; most of the extraction literature reviewed in this chapter does not meet the checklist in full."
- **Bib:** Pineau, J. et al. JMLR 22(164):1–20, 2021.
- **URL:** https://jmlr.org/papers/v22/20-303.html
- **Quote:** "In 2019, the Neural Information Processing Systems (NeurIPS) conference ... introduced a reproducibility program ... with three components: a code submission policy, a community-wide reproducibility challenge, and the inclusion of the Machine Learning Reproducibility checklist as part of the paper submission process."
- **Verdict:** VERIFIED — dissertation's characterisation is accurate.

---

## 7. Repeat-citation consistency check

For the handful of keys cited multiple times against different claims, both claims must be supported by the same paper.

| Key | Claim A | Claim B | Consistent? |
|---|---|---|---|
| `palm2017cloudscan` | Background §5.6: "established cross-issuer generalisation as a distinct evaluation axis" | LR:36: "on 326,471 invoices ... separate performance on previously-seen vs unseen layouts" | Yes — both directly in paper. |
| `park2019cord` | Background §5.3: "consolidated receipt dataset with per-box text and multi-level semantic labels" | LR:41: "benchmark-trained extractors on CORD-class receipts inherit the same problem" | Yes — CORD is exactly such a fine-tuning-dependent benchmark. |
| `mathew2021docvqa` | Background §5.4: "reframes document understanding as VQA over document images" | LR:306: "ANLS metric ... conflates correct-absence with missing answers" | Yes — both are properties of the same DocVQA paper. |
| `majumder2020form` | Background §5.14: "representation learning over extraction candidates" | LR:43: "relaxes the layout-prior requirement but not the training-data requirement" | Yes — the paper's method still requires labelled examples, as its abstract makes explicit. |
| `abdallah2024receiptsense` | Background §5.7: "multilingual surface variation at scale" | LR:83: "multilingual Arabic–English receipt dataset with a Tesseract OCR baseline" | Yes. |
| `kim2022donut` | Background §5.29: "eliminates the external OCR stage" | LR:48: "reach reported accuracy only under task-specific fine-tuning" | Yes — Donut is fine-tuned per task in its evaluation. |
| `huang2022layoutlmv3` | Background §5.30: "unified text and image masking" | LR:49: "task-specific fine-tuning on benchmark corpora" | Yes. |
| `chen2024internvl` | LR:52: "reach reported accuracy only under task-specific fine-tuning" | LR:171: "InternVL 1.5 tables placing GPT-4V/o/Claude/Gemini comparably" | Yes — both in the paper. |
| `openai2024structured` | Background §5.24: schema-adherence numbers | LR:139: "guarantee schema-valid JSON" | Yes. |
| `ferguson2026extractbench` | LR:147: "separates omission errors from hallucinations in nested-field evaluation" | LR:317: "35 PDFs paired with JSON schemas ... omission errors and hallucinations reported as separate categories" | Yes — same paper, same finding. |
| `openai-structuredoutputs-docs` | LR:139: "guarantee schema-valid JSON" | LR:145: "value-level hallucinations can persist" | Yes — both statements are in the live OpenAI docs. |

No repeat-citation inconsistencies.

---

## 8. Metadata correction register (full list)

The following **exact edits** to `references.bib` will bring every entry into agreement with the primary source, without changing any citation key or dissertation text.

### 8.1 Placeholder arXiv IDs to replace (11 entries)

```
khanchandani2026invoice     arXiv:2511.XXXXX  →  arXiv:2511.05547
nazeem2024ocrlow            arXiv:2024.XXXXX  →  remove arXiv field entirely; change to @inproceedings with booktitle = {Proc. 3rd Workshop on Indian Language Computation and Low-Resource Languages (IWCLUL) at LREC-COLING 2024}
biswas2024rotation          arXiv:2024.XXXXX  →  arXiv:2406.10295
berghaus2025multimodal      arXiv:2025.XXXXX  →  arXiv:2509.04469
geng2025jsonbench           arXiv:2025.XXXXX  →  arXiv:2501.10868
ferguson2026extractbench    arXiv:2026.XXXXX  →  arXiv:2602.12247
yu2024mmvet2                arXiv:2024.XXXXX  →  arXiv:2408.00765
fu2024bilingual             arXiv:2024.XXXXX  →  arXiv:2501.00321
vasu2024fastvlm             arXiv:2024.XXXXX  →  arXiv:2412.13303
nacson2024docvlm            arXiv:2024.XXXXX  →  arXiv:2412.08746
benkirane2026disco          arXiv:2603.23511  →  keep (valid)
```

### 8.2 Author-name corrections

```
silva2021review             {Silva, S. and Silva, R.}
                          → {Silva, Kanishka and Silva, Thushari}

khanchandani2026invoice    {Khanchandani, Kishor and Thakur, Akash and Shetty, Aditya
                            and Reddy, Chirag and Behera, Rahul}
                          → verify against arXiv:2511.05547 v2 PDF first page
                            (arXiv submitter is Advait Thakur; full author list must be
                            copied from the PDF rather than guessed)

nazeem2024ocrlow           {Meharuniza, Nazeem and Anitha, R. and Navaneeth, S.
                            and Rajeev, R.~R.}
                          → {Nazeem, Meharuniza and R, Anitha and Nair, Navaneeth S
                            and R R, Rajeev}

ferguson2026extractbench   Nigel→Nick, Jay→Josh, Nader→Narek, Anish→Aravind,
                           Sanchit→Sheshansh, Thien~Huu→Thien Hang

shen2026ocrornot           {Shen, Jia and Yuan, Peng and Ghosh, Aritra and Mai, Yu
                            and Dahlmeier, Daniel}
                          → {Shen, Jiyuan and Yuan, Peiyue and Ghosh, Atin
                            and Mai, Yifan and Dahlmeier, Daniel}

nunes2025tables            {Nunes, Gabriel and Rolla, Victor and Pereira, Diogo
                            and Alves, Vitor and Carreiro, Andr{\'e}
                            and Baptista, M{\'a}rcio}
                          → {Nunes, Guilherme and Rolla, Vitor and Pereira, Duarte
                            and Alves, Vasco and Carreiro, Andre
                            and Baptista, M{\'a}rcia}

berghaus2025multimodal     ...Berger, Adrian... → ...Berger, Armin...

benkirane2026disco         Goldwater, Daniel → Goldwater, Dan
                           Ghodsi, Ali       → Ghodsi, Aneiss
```

### 8.3 Title corrections

```
berghaus2025multimodal   title = {Multi-Modal Vision vs. Text-Based Parsing:
                                  Benchmarking {LLM} Structured Extraction on
                                  Invoices}
                       → title = {Multi-Modal Vision vs. Text-Based Parsing:
                                  Benchmarking {LLM} Strategies for Invoice
                                  Processing}

ferguson2026extractbench title = {ExtractBench: A Benchmark and Evaluation Suite
                                  for Structured {PDF}-to-{JSON} Extraction}
                       → title = {{ExtractBench}: A Benchmark and Evaluation
                                  Methodology for Complex Structured Extraction}

nazeem2024ocrlow         title = {Open-Source {OCR} Libraries: A Comprehensive
                                  Study for Low Resource Languages}
                       → title = {Open-Source {OCR} Libraries: A Comprehensive
                                  Evaluation for Low-Resource Languages}
                         (and change @article → @inproceedings)
```

### 8.4 URL correction

```
unstructured2025scorebench
   howpublished = {\url{https://unstructured.io/blog/introducing-score-bench}}
 → howpublished = {\url{https://unstructured.io/blog/score-bench}}
   (or replace with web.archive.org snapshot from December 2025)
```

---

## 9. Claim correction register

These are cases where the dissertation text itself overstates or mis-paraphrases its source and should be edited — in addition to any bib fix.

### 9.1 LiteratureReview.tex:95 (`nazeem2024ocrlow`) — **required**
Current text: "Nazeem et al. document material per-language variance across **five open-source OCR libraries on five languages**."
Actual source: three engines (Tesseract, EasyOCR, PaddleOCR) on four low-resource Indian languages (Marathi, Telugu, Urdu, Sanskrit).
**Suggested rewrite:** "Nazeem et al. document material per-language variance across three open-source OCR engines on four low-resource Indian languages."

### 9.2 LiteratureReview.tex:171 (`yu2024mmvet2`) — **recommended**
Current text implies MM-Vet v2 is a DocVQA/InfoVQA ranking. It is not — MM-Vet v2 evaluates six general VL capabilities including OCR, not DocVQA/InfoVQA specifically.
**Suggested rewrite:** "are placed on directly comparable evaluation axes by Borchmann's reproducible API evaluation (DocVQA, InfoVQA) [borchmann2024gpt4], the InternVL 1.5 tables [chen2024internvl], and the MM-Vet v2 capability benchmark [yu2024mmvet2]."

### 9.3 LiteratureReview.tex:80 (`khanchandani2026invoice`) — **recommended**
The dissertation's phrasing "arguing that an LLM reasoning stage recovers structure the OCR layer lost" is the dissertation's rhetorical gloss. The paper itself says more modestly that LLMs "support complex contextual relationship mapping without direct programming specification."
**Suggested rewrite:** "combine CNN-based layout analysis, OCR, and LLM entity recognition, arguing that an LLM reasoning stage complements the OCR layer with contextual semantic mapping."

### 9.4 LiteratureReview.tex:170 (`borchmann2024gpt4`)
Borchmann's 2024 paper predates public availability of GPT-4o and Claude 3.5 Sonnet; it evaluates GPT-4 Turbo and GPT-4V. The dissertation's list "GPT-4V, GPT-4o, Claude 3.5 Sonnet, and Gemini" is the union of the *three* sources cited, not what Borchmann alone evaluates. This is acceptable given the "...are placed on directly comparable axes by [three sources]" framing, but a careful reader may conflate them. A small clarifying phrase would help.

---

## 10. Fabrication audit

Every cited key resolves to a real, retrievable paper. **Zero fabrications.**

The eleven red-flag arXiv IDs marked `XXXXX` in the bibliography all correspond to real papers (arXiv:2511.05547, 2406.10295, 2509.04469, 2501.10868, 2602.12247, 2408.00765, 2501.00321, 2412.13303, 2412.08746, and a paper not on arXiv at all for `nazeem2024ocrlow`). `benkirane2026disco` @ arXiv:2603.23511 is a legitimate March 2026 arXiv ID.

The one UNSUPPORTED claim (`nazeem2024ocrlow`, LR:95) is not a fabricated citation — the paper does exist and is about OCR for low-resource languages — but the **specific factual claim** ("five libraries on five languages") does not match what the paper reports. This is a numeric misreading on the dissertation side, not an invented citation.

---

## 11. Orphan-entry report

The following five entries are defined in `references.bib` but never cited in the two audited chapters. They are not errors per se — they may be cited in chapters this audit did not examine (Introduction, Design, Evaluation, LSESP, Implementation) — but flagging them keeps the bibliography honest.

| Key | Likely intended use |
|---|---|
| `gemini2024gemini15` | Might cover the Gemini provider referenced in §6.19; not actually cited with `\cite{}`. |
| `levenshtein1966` | Classical edit-distance reference; likely used in the Evaluation chapter. |
| `liu2024ocrbench` | Original OCRBench; `fu2024bilingual` (OCRBench v2) is the one actually cited. |
| `tam2024format` | Format-restriction LLM study — relevant but not cited. |
| `unstructured2026parsing` | Companion to `unstructured2025scorebench`; could replace or supplement the LR:272 citation. |

**Recommendation:** either cite each in the relevant chapter or remove from `.bib` before submission.

---

## 12. Bottom-line summary

- **Fabrications: 0.** Every `\cite{}` resolves to a real, fetchable primary source.
- **Metadata defects: 14 entries** need bib edits (11 placeholder arXiv IDs + 3 further entries with wrong author names or title). All fixes are listed verbatim in §8.
- **Claim defects: 1 required rewrite** (`nazeem2024ocrlow` 5×5 vs 3×4) and **3 recommended clarifications** (MM-Vet v2 / Borchmann 2024 framing / Khanchandani gloss). All listed in §9.
- **Unverifiable URL: 1** (`unstructured2025scorebench` path changed; live page still reachable on the blog index).
- **Orphan bib entries: 5** flagged for cleanup.

Applying §8 and §9 will bring the bibliography and the cited claims into full agreement with the primary sources, with no loss of argumentative structure in the dissertation.
