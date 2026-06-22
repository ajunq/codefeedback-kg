# Journal article (WS-4) — Semantic Web Journal (Sage)

Preprint of the CodeFeedback-KG journal article, targeted at the **Semantic Web
Journal** (*Semantic Web — Interoperability, Usability, Applicability*; IOS Press,
now published by Sage; ISSN 1570-0844). Article type: **Original Research Article**.

## Files

| File | Purpose |
|---|---|
| `main.tex` | The article. Class `\documentclass[sageh]{sagej}`, full IMRaD skeleton plus the SWJ-mandated **Statements and Declarations** section. |
| `references.bib` | 64 references, BibTeX, coherent keys. Every entry is cited at least once in `main.tex`. |
| `README.md` | This file. |

## How to compile (Overleaf)

The compiled PDF is included (`main.pdf`). To recompile or edit the source, use
Overleaf, where the `sagej` class is available out of the box:

1. Open the official Sage template on Overleaf:
   *"A demonstration of the LaTeX2e class file for SAGE Publications"*
   <https://www.overleaf.com/latex/templates/a-demonstration-of-the-latex2e-class-file-for-sage-publications/jcdyknyjrkzb>
2. Replace the template's `.tex` with `main.tex` and add `references.bib`.
   (The `sagej` class, `SageV.bst` and required style files ship with that template.)
3. Set the compiler to **pdfLaTeX** and run the standard sequence:
   `pdflatex → bibtex → pdflatex → pdflatex` (Overleaf's "Recompile" does this when
   "Bibliography: BibTeX" is selected, or use the menu to force a BibTeX pass).

Alternatively, with a local TeX Live/MiKTeX install that has the Sage template
files on the path, the same `pdflatex/bibtex/pdflatex/pdflatex` sequence applies.

## Reference / citation style

**Sage Vancouver** (numbered) — the style the SWJ submission guide specifies.
It is selected via `\bibliographystyle{SageV}` together with the `sageh` class
option. The `sagej` class can also do Sage Harvard (author–year) and APA, but the
SWJ guide says Vancouver, so that is what `main.tex` uses.

## Section structure (as required by the SWJ / Sage guide)

Title · structured Abstract (~200 words: Background/Methods/Results/Conclusions) ·
Keywords · 1 Introduction · 2 Related Work · 3 Background · 4 Approach ·
5 Experimental Setup · 6 Results · 7 Discussion · 8 Limitations · 9 Conclusion ·
Acknowledgments · **Statements and Declarations** (Ethical Considerations, Consent
to Participate, Consent for Publication, Declaration of Conflicting Interest,
Funding, Data Availability) · References.

No length limit applies to original research articles at the SWJ.

## References

`references.bib` holds **64 BibTeX references** (16 `@article`, 36 `@misc`,
6 `@techreport`, 4 `@inproceedings`, 2 `@book`), all cited in `main.tex`.
