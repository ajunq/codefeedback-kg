# CodeFeedback-KG v2.0 — Informe de objetivos (§10)

Generado: 2026-06-21 · versionInfo: **2.0.0** · PASS **28/28** dimensiones.

Re-derivado sobre el grafo final con rdflib/SPARQL, el cierre OWL-RL y SHACL (pyshacl, inferencia RDFS). v1.0 = `codefeedback-kg-150.ttl` (congelado); v2.0 = `codefeedback-kg.ttl`.

## Cierre OWL-RL y SHACL

- Triples afirmados v2.0: **3291** · cierre OWL-RL: **8957** (inferidos 5666).
- cfkg:Concepto inferidos: **222** · owl:Nothing: **0** · owl:sameAs no reflexivo: **0** -> **CONSISTENTE: True**.
- SHACL formas: **18** · Conforms (grafo valido): **True** (violaciones 0) · violaciones en ejemplo-invalido: **9**.

## Tabla de dimensiones

| dimension | v1.0 | v2.0 | objetivo | PASS/FAIL | re-derivacion |
|---|---|---|---|---|---|
| cfkg:Concepto (inferido OWL-RL) | 157 | 222 | >=210 | **PASS** | owlrl DeductiveClosure; |{?s a cfkg:Concepto}| |
| triples afirmados | 1772 | 3291 | >=2500 | **PASS** | len(Graph) tras parse rdflib |
| owl:Class | 20 | 28 | >=28 | **PASS** | |{?s a owl:Class}| |
| owl:ObjectProperty | 21 | 26 | >=26 | **PASS** | |{?s a owl:ObjectProperty}| |
| owl:DatatypeProperty | 7 | 11 | >=10 | **PASS** | |{?s a owl:DatatypeProperty}| |
| rdfs:subClassOf | 20 | 42 | >=30 | **PASS** | |{?s rdfs:subClassOf ?o}| |
| owl:TransitiveProperty | 2 | 5 | >=4 | **PASS** | |{?s a owl:TransitiveProperty}| |
| owl:SymmetricProperty | 1 | 2 | >=1 | **PASS** | |{?s a owl:SymmetricProperty}| |
| owl:FunctionalProperty | 1 | 2 | >=2 | **PASS** | |{?s a owl:FunctionalProperty}| |
| owl:inverseOf (pares) | 2 | 4 | >=4 | **PASS** | |{?s owl:inverseOf ?o}| |
| owl:disjointWith | 0 | 10 | >=6 | **PASS** | |{?s owl:disjointWith ?o}| |
| owl:Restriction | 0 | 12 | >=10 | **PASS** | |{?s a owl:Restriction}| |
| propiedades sin dominio | 2 | 0 | ==0 | **PASS** | props sin rdfs:domain |
| propiedades sin rango | 0 | 0 | ==0 | **PASS** | props sin rdfs:range |
| owl:Ontology header completo | parcial | completo | completo | **PASS** | title/creator/license/description/versionInfo/versionIRI presentes |
| versionInfo | 1.0.0 | 2.0.0 | 2.0.0 | **PASS** | owl:versionInfo del owl:Ontology |
| Formas SHACL | 10 | 18 | >=16 | **PASS** | |{?s a sh:NodeShape}| en shapes-codefeedback-kg.ttl |
| skos:broader | 19 | 38 | >=30 | **PASS** | |{?s skos:broader ?o}| |
| skos:narrower | 19 | 38 | >=20 | **PASS** | |{?s skos:narrower ?o}| |
| skos:related | 16 | 70 | >=20 | **PASS** | |{?s skos:related ?o}| |
| cobertura def+scopeNote+example | 0/157 | 222/222 | ==conceptos | **PASS** | cada cfkg:Concepto con skos:definition+scopeNote+example |
| skos:exactMatch Wikidata | 30 | 48 | >=40 | **PASS** | exactMatch a wikidata.org (QIDs via API) |
| vocabularios externos alineados | 4 | 5 (DBpedia, DCTerms, FOAF, Wikidata, schema.org) | >=4 | **PASS** | Wikidata+DBpedia+schema.org+DCTerms(+FOAF) |
| owl:sameAs | 0 | 0 | ==0 | **PASS** | |{?s owl:sameAs ?o}| afirmados |
| OWL-RL consistencia (owl:Nothing) | n/d | 0 | ==0 | **PASS** | miembros de owl:Nothing en el cierre |
| OWL-RL sin fusion (sameAs no reflex.) | n/d | 0 | ==0 | **PASS** | owl:sameAs x!=y en el cierre |
| SHACL Conforms (grafo valido) | True | True | True | **PASS** | pyshacl rdfs; violaciones=0 |
| SHACL viola en ejemplo-invalido | n/d | 9 | >0 | **PASS** | pyshacl sobre grafo + ejemplo-invalido.ttl |
