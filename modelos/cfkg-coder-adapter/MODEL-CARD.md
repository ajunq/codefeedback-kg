# Model Card — CFKG-Coder-Adapter-v1

A QLoRA fine-tuning adapter that specialises a code LLM to produce structured, Spanish, formative
feedback on introductory-Python student code. Released as part of CodeFeedback-KG. Follows the
Model Cards framework (Mitchell et al., 2019).

## Model details
- **Type:** LoRA/QLoRA adapter (4-bit NF4 base, low-rank update matrices; NEFTune during instruction tuning).
- **Base model:** Qwen2.5-Coder-7B-Instruct (Apache-2.0). The adapter is not a standalone model.
- **Determinism:** fixed random seed **11**. Hardware: a single NVIDIA RTX 5090 (32 GB), Python 3.12, Ollama local.
- **License:** Apache-2.0 (see LICENSE, NOTICE). Author: Adrián Bueno Junquero.

## Intended use
- Generating Spanish pedagogical feedback for introductory Python exercises: a five-part diagnosis
  (error type, concept, lay explanation, technical explanation, suggestion).
- It is a research prototype for formative feedback, not a deployed grading or high-stakes assessment system.

## Training data
- The CodeFeedback-KG Spanish code-feedback dataset (v2): **2625 records across 35 skeletons**
  (train 2100 / val 525, with 0 held-out overlap). Numbers re-derived from source and reconciled
  against the project metrics; see the repository data card.

## Evaluation (both-sided)
- **In distribution** (synthetic held-out, n=50, judge `qwen2.5:32b`, seed 11): the hybrid system D
  leads on the objective axes (category 0.76, concept 0.54); all augmented systems beat the base, but
  the D-vs-B advantage is **not statistically significant** at n=50 (Holm p≈0.18).
- **Out of distribution** (real student code, Dublin DCU CS1, n=60/54): the objective fix-relevance
  ranking **inverts** — A 0.802 > C 0.733 > B 0.433 > D 0.323 (Friedman χ²=68.69, p=8.1×10⁻¹⁵). This
  is reported as **template over-fitting**.

## Limitations
- **Template over-fitting:** the synthetic training targets are highly homogeneous (intra-skeleton
  cosine 0.962), so the fine-tuned advantage does **not transfer** to real, out-of-distribution code.
- The objective fix-relevance metric rewards literal token overlap, which partly penalises the
  conceptual Spanish feedback the adapter is trained to produce; read it as a lower bound on usefulness.
- Scope is introductory Python feedback in Spanish from a 7B-class local model; other languages,
  domains and scales are untested.

## License & citation
Apache-2.0. Cite CodeFeedback-KG (see the repository `CITATION.cff`) and the base model
Qwen2.5-Coder-7B-Instruct.
