# Verification Report (Claim-Level Re-verification Pass)

## Summary
- Total citations re-verified: 83 audit entries across 83 bibliography citations (cross-section duplicates for Nazeem ICON 2024 audited twice, once per section)
- verified_unchanged: 58
- corrected: 19
- claim_stripped: 6 (5 unique clauses removed across 6 citations)
- flagged_for_human_review: 0

Per-agent totals: RV1 (19), RV2 (12), RV3 (12), RV4A (9), RV4B (5), RV4C (7), RV5 (8), RV6 (11). Raw sum = 83.

## Date-quota re-check (R4)
- 2023+ overall: 46/83 (55.4%)
- L5 2024-2026: 7/7
- L6 2024-2026: 7/8

## Corrections applied (per citation)
- [RV1] L1 / CloudScan2017-L1 / `ref`
    - before: Palm et al. (2017). CloudScan. arXiv:1708.07403.
    - after:  Palm, Winther, and Laws (2017). CloudScan - A configuration-free invoice analysis system using recurrent neural networks. arXiv:1708.07403.
    - evidence: https://arxiv.org/abs/1708.07403
- [RV1] L1 / Chargrid2018-L1 / `summary`
    - before: Encodes pages as 2D character grids to preserve layout and demonstrates invoice extraction where purely sequential text loses spatial cues critical for fields and tables.
    - after:  Encodes pages as 2D character grids to preserve layout and demonstrates invoice information extraction; the abstract states their approach significantly outperforms methods based on sequential text or...
    - evidence: https://aclanthology.org/D18-1476/
- [RV2] B4 / Nazeem2024-ICON-B4 / `ref`
    - before: Nazeem, Anitha R, Navaneeth S, and Rajeev R. R. (2024). Open-Source OCR Libraries: A Comprehensive Study for Low Resource Language. Proceedings of the 21st International Conference on Natural Language...
    - after:  Meharuniza Nazeem, Anitha R, Navaneeth S, and Rajeev R. R. (2024). Open-Source OCR Libraries: A Comprehensive Study for Low Resource Language. Proceedings of the 21st International Conference on Natur...
    - evidence: https://aclanthology.org/2024.icon-1.48/
- [RV2] L2 / ReceiptSense2024-L2 / `ref`
    - before: Abdallah et al. (2024). ReceiptSense. arXiv:2406.04493.
    - after:  Abdallah, A., Mounis, M., Abdalla, M., Kasem, M. S., Mahmoud, M., Abdelhalim, I., Elkasaby, M., Elbendary, Y., and Jatowt, A. (2024). ReceiptSense: Beyond Traditional OCR -- A Dataset for Receipt Unde...
    - evidence: https://arxiv.org/abs/2406.04493, https://arxiv.org/html/2406.04493v2
- [RV2] L2 / Gupte2021-LightsCamera / `ref`
    - before: Gupte, A., Romanov, A., Mantha, S., Agarwal, V., Gandhi, A., Ginzburg, V., Kasargod, S., and Srinivasan, S. (2021). Lights, Camera, Action! A Framework to Improve NLP Accuracy over OCR documents. arXi...
    - after:  Gupte, A., Romanov, A., Mantravadi, S., Banda, D., Liu, J., Khan, R., Meenal, L. R., Han, B., and Srinivasan, S. (2021). Lights, Camera, Action! A Framework to Improve NLP Accuracy over OCR documents....
    - evidence: https://arxiv.org/abs/2108.02899, https://export.arxiv.org/api/query?id_list=2108.02899
- [RV2] L2 / Nazeem2024-ICON-L2 / `ref`
    - before: Nazeem, Anitha R, Navaneeth S, and Rajeev R. R. (2024). Open-Source OCR Libraries: A Comprehensive Study for Low Resource Language. ICON 2024, pp. 416-421.
    - after:  Meharuniza Nazeem, Anitha R, Navaneeth S, and Rajeev R. R. (2024). Open-Source OCR Libraries: A Comprehensive Study for Low Resource Language. ICON 2024, pp. 416-421.
    - evidence: https://aclanthology.org/2024.icon-1.48/
- [RV3] L4 / Berghaus2025-Invoice / `ref`
    - before: Berghaus et al. (2025). Multi-Modal Vision vs. Text-Based Parsing: Benchmarking LLM Strategies for Invoice Processing. arXiv:2509.04469.
    - after:  Berghaus, D., Berger, A., Hillebrand, L., Cvejoski, K., and Sifa, R. (2025). Multi-Modal Vision vs. Text-Based Parsing: Benchmarking LLM Strategies for Invoice Processing. arXiv:2509.04469.
    - evidence: https://arxiv.org/abs/2509.04469, https://arxiv.org/html/2509.04469v1
- [RV3] L4 / Geng2025-JSONSchemaBench / `ref`
    - before: Geng et al. (2025). JSONSchemaBench: A Rigorous Benchmark of Structured Outputs for Language Models. arXiv:2501.10868.
    - after:  Geng, S., Cooper, H., Moskal, M., Jenkins, S., Berman, J., Ranchin, N., West, R., Horvitz, E., and Nori, H. (2025). JSONSchemaBench: A Rigorous Benchmark of Structured Outputs for Language Models. arX...
    - evidence: https://arxiv.org/abs/2501.10868, https://arxiv.org/html/2501.10868v3
- [RV4B] L3 / Pix2Struct-L3 / `ref`
    - before: Lee et al. (2023). Pix2Struct. ICML 2023. arXiv:2210.03347.
    - after:  Lee, Joshi, Turc, Hu, Liu, Eisenschlos, Khandelwal, Shaw, Chang, and Toutanova (2023). Pix2Struct: Screenshot Parsing as Pretraining for Visual Language Understanding. ICML 2023. arXiv:2210.03347.
    - evidence: https://arxiv.org/html/2210.03347v2
- [RV4B] L3 / Pix2Struct-L3 / `key_claims`
    - before: 80M screenshot/HTML pairs; warmup 30K steps; Base: +270K pretrain steps, batch 2048, 64 TPUs; Large: +170K pretrain steps, batch 1024, 128 TPUs; DocVQA finetune 10,000 steps batch 256.
    - after:  80M screenshot/HTML pairs; warmup 30K steps; Base: +270K pretrain steps, batch 2048, 64 TPUs; Large: +170K pretrain steps, batch 1024, 128 TPUs; DocVQA finetune 10,000 steps with batch 256 (Base) or 1...
    - evidence: https://arxiv.org/html/2210.03347v2
- [RV4B] L3 / Chen2024-InternVL15-L3 / `ref`
    - before: Chen, Z., et al. (2024). How Far Are We to GPT-4V? Closing the Gap to Commercial Multimodal Models with Open-Source Suites. arXiv:2404.16821.
    - after:  Chen, Z., Wang, W., Tian, H., Ye, S., Gao, Z., Cui, E., Tong, W., Hu, K., Luo, J., Ma, Z., Ma, J., Wang, J., Dong, X., Yan, H., Guo, H., He, C., Shi, B., Jin, Z., Xu, C., Wang, B., Wei, X., Li, W., Zh...
    - evidence: https://arxiv.org/html/2404.16821v2
- [RV4B] L3 / Borchmann2021-DUE-L3 / `ref`
    - before: Borchmann, L., et al. (2021). DUE: End-to-End Document Understanding Benchmark. NeurIPS Datasets and Benchmarks Track 2021.
    - after:  Borchmann, L., Pietruszka, M., Stanislawek, T., Jurkiewicz, D., Turski, M., Szyndler, K., and Gralinski, F. (2021). DUE: End-to-End Document Understanding Benchmark. NeurIPS Datasets and Benchmarks Tr...
    - evidence: https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/hash/069059b7ef840f0c74a814ec9237b6ec-Abstract.html
- [RV4C] L5 / InternVL15-L5 / `ref`
    - before: Chen, Z., et al. (2024). InternVL 1.5 / How Far Are We to GPT-4V. arXiv:2404.16821.
    - after:  Chen, Z., Wang, W., Tian, H., Ye, S., Gao, Z., Cui, E., Tong, W., Hu, K., Luo, J., Ma, Z., Ma, J., Wang, J., Dong, X., Yan, H., Guo, H., He, C., Shi, B., Jin, Z., Xu, C., Wang, B., Wei, X., Li, W., Zh...
    - evidence: https://arxiv.org/html/2404.16821v2
- [RV4C] L5 / Yu2024-MMVetV2 / `ref`
    - before: Yu, W., et al. (2024). MM-Vet v2: A Challenging Benchmark to Evaluate Large Multimodal Models for Integrated Capabilities. arXiv:2408.00765.
    - after:  Yu, W., Yang, Z., Ren, L., Li, L., Wang, J., Lin, K., Lin, C.-C., Liu, Z., Wang, L., and Wang, X. (2024). MM-Vet v2: A Challenging Benchmark to Evaluate Large Multimodal Models for Integrated Capabili...
    - evidence: https://arxiv.org/abs/2408.00765, https://arxiv.org/html/2408.00765v2
- [RV4C] L5 / Fu2024-OCRBenchV2 / `ref`
    - before: Fu, L., et al. (2024/2025). OCRBench v2: An Improved Benchmark for Evaluating Large Multimodal Models on Visual Text Localization and Reasoning. arXiv:2501.00321.
    - after:  Fu, L., Kuang, Z., Song, J., Huang, M., Yang, B., Li, Y., Zhu, L., Luo, Q., Wang, X., Lu, H., Li, Z., Tang, G., Shan, B., Lin, C., Liu, Q., Wu, B., Feng, H., Liu, H., Huang, C., Tang, J., Chen, W., Ji...
    - evidence: https://arxiv.org/abs/2501.00321
- [RV4C] L5 / Vasu2024-FastVLM / `ref`
    - before: Vasu, P. K. A., et al. (2024). FastVLM: Efficient Vision Encoding for Vision Language Models. arXiv:2412.13303.
    - after:  Vasu, P. K. A., Faghri, F., Li, C.-L., Koc, C., True, N., Antony, A., Santhanam, G., Gabriel, J., Grasch, P., Tuzel, O., and Pouransari, H. (2024). FastVLM: Efficient Vision Encoding for Vision Langua...
    - evidence: https://arxiv.org/abs/2412.13303
- [RV4C] L5 / Nacson2024-DocVLM / `ref`
    - before: Nacson, M. S., et al. (2024). DocVLM: Make Your VLM an Efficient Reader. arXiv:2412.08746.
    - after:  Nacson, M. S., Aberdam, A., Ganz, R., Ben Avraham, E., Golts, A., Kittenplon, Y., Mazor, S., and Litman, R. (2024). DocVLM: Make Your VLM an Efficient Reader. arXiv:2412.08746.
    - evidence: https://arxiv.org/abs/2412.08746
- [RV5] L6 / Shen2026-OCRorNot / `ref`
    - before: Shen, J., Peiyue, Y., Ghosh, A., Mai, Y., and Dahlmeier, D. (2026). OCR or Not? Rethinking Document Information Extraction in the MLLMs Era with Real-World Large-Scale Datasets. EACL 2026 Industry Tra...
    - after:  Shen, J., Yuan, P., Ghosh, A., Mai, Y., and Dahlmeier, D. (2026). OCR or Not? Rethinking Document Information Extraction in the MLLMs Era with Real-World Large-Scale Datasets. Proceedings of the 19th ...
    - evidence: https://aclanthology.org/2026.eacl-industry.28/
- [RV5] L6 / Shen2026-OCRorNot / `key_claims`
    - before: Abstract: OCR may not be necessary for powerful MLLMs because image-only input can achieve comparable performance to OCR-enhanced approaches; carefully designed schema, exemplars, and instructions fur...
    - after:  Abstract: OCR may not be necessary for powerful MLLMs because image-only input can achieve comparable performance to OCR-enhanced approaches; carefully designed schema, exemplars, and instructions fur...
    - evidence: https://aclanthology.org/2026.eacl-industry.28/
- [RV5] L6 / Unstructured2025-SCOREBench / `key_claims`
    - before: Unstructured VLM Partitioner GPT-5-mini Adjusted CCT 0.883 / Tokens Added 0.036; Unstructured High-Res Refined with Claude Sonnet 4 Cell Content Accuracy 0.773 / Cell Index Accuracy 0.776; Reducto Age...
    - after:  Unstructured VLM Partitioner GPT-5-mini Adjusted CCT 0.883; Percent Tokens Added 0.036; Unstructured High-Res Refined with Claude Sonnet 4 Cell Content Accuracy 0.773; Cell Level Index Accuracy 0.776;...
    - evidence: https://unstructured.io/blog/introducing-score-bench-an-open-benchmark-for-document-parsing
- [RV6] L7 / Dale2023-HalOmi / `ref`
    - before: Dale, D., Voita, E., Lam, J., Hansanti, P., Ropers, C., Kalbassi, E., Gao, C., Barrault, L., and Costa-jussa, M. R. (2023). HalOmi: A Manually Annotated Benchmark for Multilingual Hallucination and Om...
    - after:  David Dale, Elena Voita, Janice Lam, Prangthip Hansanti, Christophe Ropers, Elahe Kalbassi, Cynthia Gao, Loic Barrault, and Marta R. Costa-jussa (2023). HalOmi: A Manually Annotated Benchmark for Mult...
    - evidence: https://aclanthology.org/2023.emnlp-main.42/

## Claims stripped (per citation)
- [RV1] B2 / FUNSD2019-B2 / `summary`
    - removed: (see before/after diff)
    - reason: 
    - before: Emphasises that scanned forms are noisy and vary widely in appearance, providing fully annotated forms for entity-centric structuring tasks. Mirrors utility bills as scanned, field-oriented documents.
    - after:  Emphasises that scanned forms are noisy and vary widely in appearance, providing fully annotated forms for entity-centric structuring tasks.
    - evidence: https://arxiv.org/abs/1905.13538
- [RV2] L2 / Khanchandani2026 / `key_claims`
    - removed: K. J. Somaiya School of Engineering
    - reason: Institution not present on fetched arXiv abs or API metadata.
    - before: arXiv:2511.05547 (submitted Nov 2025, revised Jan 2026); proposes hybrid OCR+LLM industry architecture for invoice extraction; PDF confirms authors K. Khanchandani, A. Thakur, A. Shetty, C. Reddy, R. ...
    - after:  arXiv:2511.05547 (submitted Nov 2025, revised Jan 2026); proposes hybrid OCR+LLM industry architecture for invoice extraction; arXiv lists authors Khushi Khanchandani, Advait Thakur, Akshita Shetty, C...
    - evidence: https://arxiv.org/abs/2511.05547, https://export.arxiv.org/api/query?id_list=2511.05547
- [RV3] B5 / WillardLouf2023-Outlines / `key_claims`
    - removed: Scales as O(1) on average vs naive O(N)
    - reason: Complexity statement not visible on fetched arXiv abstract; secondary HTML not available.
    - before: Scales as O(1) on average vs naive O(N); claims significant speedups vs existing constrained decoding.
    - after:  Model-agnostic FSM-based guidance with little overhead; abstract states significant speedups vs existing solutions; implemented in Outlines.
    - evidence: https://arxiv.org/abs/2307.09702
- [RV4A] B6 / Kim2022-Donut / `summary`
    - removed: (see before/after diff)
    - reason: 
    - before: Proposes Donut, an OCR-free document understanding Transformer that avoids outsourcing reading to an external OCR engine, with cross-entropy pre-training and a SynthDoG synthetic generator for flexibl...
    - after:  Proposes Donut, an OCR-free document understanding Transformer that avoids outsourcing reading to an external OCR engine, with cross-entropy pre-training and a synthetic data generator for flexible pr...
    - evidence: https://arxiv.org/abs/2111.15664
- [RV4A] B6 / Kim2022-Donut / `key_claims`
    - removed: SynthDoG
    - reason: String 'SynthDoG' not present on arXiv abstract.
    - before: OCR-free end-to-end modelling with cross-entropy pre-training and SynthDoG.
    - after:  OCR-free end-to-end modelling with cross-entropy pre-training and a synthetic data generator.
    - evidence: https://arxiv.org/abs/2111.15664
- [RV5] L6 / Poznanski2025-olmOCR / `key_claims`
    - removed: olmOCR-Bench has 1,400 PDFs
    - reason: Abstract says 1,400 PDFs but full paper HTML v3 Table 10 lists 1,402/1,403 distinct PDF documents and 7,010 tests; the single '1,400' number is ambiguous across the paper.
    - before: Traditional open-source tools often lower quality than VLMs; GPT-4o conversion can cost over $6,240 USD per million PDF pages; olmOCR can convert a million PDF pages for $176 USD; olmOCR-Bench has 1,4...
    - after:  Traditional open-source tools often produce lower quality extractions than VLMs; GPT-4o batch pricing example over $6,240 USD per million PDF pages; olmOCR about $176 USD per million PDF pages; olmOCR...
    - evidence: https://arxiv.org/abs/2502.18443, https://arxiv.org/html/2502.18443v3
- [RV6] L7 / Chinchor1998-MUC7-L7 / `summary`
    - removed: NON as mutually null
    - reason: PDF defines NON as non-committal null fills aligned with the key, not 'mutually null'.
    - before: Appendix defines MIS as missing fills, SPU as spurious fills, NON as mutually null, with metrics including recall, precision, undergeneration, overgeneration, substitution, error rate, and weighted F-...
    - after:  Appendix defines MIS as missing fills and SPU as spurious fills, with metrics including recall, precision, undergeneration, overgeneration, substitution, error rate, and weighted F-measures.
    - evidence: https://aclanthology.org/M98-1024/, https://aclanthology.org/M98-1024.pdf

## L6 control-grid updates
Before/after counts of cells whose value starts with `unknown` across the 8 L6 citations (8 citations x 4 cells = 32 cells):

| Dimension | Unknown (pre) | Unknown (post) | Delta |
|---|---|---|---|
| reasoning_engine_constant | 1/8 | 1/8 | +0 |
| prompt_constant | 6/8 | 6/8 | +0 |
| multilingual | 5/8 | 5/8 | +0 |
| cost_latency_ops_reported | 6/8 | 6/8 | +0 |
| **TOTAL** | **18/32** | **18/32** | **+0** |

No L6 control_grid values changed during this re-verification pass.

## Human-review items
None.

## Empty downstream_consequence checks (L sections except L8)
All L1-L7 citations still have non-empty `downstream_consequence`.

## Primary sources that failed to load during re-verification
None of the RV agents reported fetch failures in this pass.

## Backup
Pre-patch bibliography copied to `bibliography.pre_reverification.json` at workspace root during this pass.
