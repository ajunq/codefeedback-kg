# CodeFeedback-KG

A canonical, openly-licensed **Educational Knowledge Graph** for introductory Python (OWL 2 RL +
SHACL + SPARQL, linked to Wikidata) and a **GraphRAG** feedback pipeline with a QLoRA-fine-tuned
Spanish feedback generator. This is the public, independently-engineered release of the artifact;
the accompanying paper studies the criterion validity of an LLM judge against a human panel.

Author: **Adrián Bueno Junquero**.

- Ontology (TBox + ABox, serialisations, SHACL shapes, SPARQL queries): `ontologia/`
- Fine-tuned adapter (CFKG-Coder-Adapter-v1): `modelos/cfkg-coder-adapter/`
- Paper sources: `paper/`
- Persistent namespace: `https://w3id.org/codefeedback-kg/` (prefixes `cfkg:` schema, `cfr:` instances)

## License

CodeFeedback-KG uses a split license stack (code vs data vs paper):

| artifact | license | permits | requires | forbids | notice files | dossier |
|----------|---------|---------|----------|---------|--------------|---------|
| Repository code | **Apache-2.0** | use/modify/distribute/sublicense/patent/commercial | preserve LICENSE+NOTICE, state significant changes, keep notices | removing notices, using trademarks | `LICENSE`, `NOTICE` | [D07][D13] |
| Ontology (TBox+ABox) | **CC BY 4.0** | use/share/adapt/commercial | attribution, indicate changes, keep license URI | extra restrictions/DRM | `LICENSE-DATA` | [D10][D22] |
| Dataset | **CC BY 4.0** | use/share/adapt/commercial | attribution, indicate changes | extra restrictions | `LICENSE-DATA` | [D10][D09] |
| Fine-tuned adapter | **Apache-2.0** | use/modify/distribute/commercial/patent | preserve NOTICE incl. upstream Qwen attribution, ship Model Card, state changes | implying Qwen endorsement | `modelos/cfkg-coder-adapter/{LICENSE,NOTICE,MODEL-CARD.md}` | [D07][D08][D30] |
| Baselines A/C (Llama 3.1 8B, inference only) | Llama 3.1 Community License (not redistributed) | local inference baseline | courtesy attribution in NOTICE/README | shipping a Llama-derived model without the "Llama" name prefix + "Built with Llama" | `NOTICE` | [D05][D06] |
| Journal paper | **CC BY-NC** (SWJ/SAGE default) | read/share/non-commercial reuse w/ attribution | attribution, non-commercial, supply DOI for preprint | commercial reuse w/o permission | paper front-matter | [D01][D02] |

> Note: the exact paper copyright/license is subject to confirmation with the journal's editorial
> office before camera-ready. This is a pre-release working copy.
