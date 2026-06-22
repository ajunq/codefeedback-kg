# CodeFeedback-KG v2.0 — Especificación de requisitos (metodología LOT)

**Ontología:** CodeFeedback-KG · *A Semantic Knowledge Graph of Python Concepts for Pedagogical Code Feedback*
**Versión:** 2.0.0 · **Fecha:** 2026-06-21 · **Autor:** Adrián Bueno Junquero
**Espacios de nombres:** `cfkg:` = `https://w3id.org/codefeedback-kg/schema#` (esquema) · `cfr:` = `https://w3id.org/codefeedback-kg/id/` (individuos)
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)

Este documento sigue la metodología **LOT (Linked Open Terms)** — *Requisitos → Implementación → Publicación → Mantenimiento* — y registra los requisitos de la ontología, los recursos reutilizados y las **preguntas de competencia (CQ)** con su prueba SPARQL ejecutable.

---

## 1. Fase de especificación de requisitos (LOT · *Ontology Requirements Specification*)

### 1.1 Propósito
Modelar el dominio de la **programación en Python** (conceptos, prerrequisitos, contrastes, temas, ejercicios, errores conceptuales/*misconceptions*, recursos y perfiles de estudiante) para **anclar la generación automática de retroalimentación formativa** en una arquitectura EKG + RAG + LLM. El grafo aporta el conocimiento de dominio verificable que el LLM no debe alucinar.

### 1.2 Alcance
Python como lenguaje de enseñanza: fundamentos, control de flujo, estructuras de datos, tipos, funciones, POO, programación funcional, módulos/empaquetado, ficheros, excepciones, concurrencia, recursión, algoritmos y complejidad, tipado estático y pruebas.

### 1.3 Lenguaje de implementación y perfil
- **OWL 2 RL** (perfil orientado a reglas, razonamiento en tiempo polinómico, cierre completo y consistente vía *materialización*). Todas las construcciones son seguras en OWL 2 RL: las restricciones se usan en posición de superclase con `owl:allValuesFrom` (universal) y `owl:maxQualifiedCardinality` ≤ 1 (cardinalidad máxima cualificada), formas admitidas por el perfil RL.
- **SKOS** para la red conceptual (`skos:broader`/`narrower`/`related`, `skos:definition`/`scopeNote`/`example`) y los alineamientos externos (`skos:exactMatch`/`closeMatch`). `cfkg:Concepto rdfs:subClassOf skos:Concept` y `skos:broader rdfs:subPropertyOf skos:broaderTransitive`.
- **SHACL** (18 formas) para la validación de forma del grafo de datos.

### 1.4 Requisitos NO funcionales (NFR)
- **NFR1** — La ontología debe permanecer **consistente** bajo cierre OWL-RL (sin miembros de `owl:Nothing`).
- **NFR2** — Los enlaces externos usan `skos:exactMatch`/`closeMatch`, **nunca `owl:sameAs`** (que debe ser 0).
- **NFR3** — Etiquetas bilingües (`@es`/`@en`) en clases, propiedades e individuos.
- **NFR4** — Toda propiedad de objeto y de datos declara `rdfs:domain` y `rdfs:range`.
- **NFR5** — Cada `cfkg:Concepto` tiene `skos:definition` + `skos:scopeNote` + `skos:example` (pedagogía Python genuina y correcta).
- **NFR6** — Alineamiento con **≥ 4 vocabularios externos**: Wikidata, DBpedia, schema.org, DC Terms (y FOAF).
- **NFR7** — Publicación **FAIR** y **5★ Open Data**; licencia **CC BY 4.0**; versionado SemVer con `owl:versionIRI`.

### 1.5 Requisitos funcionales (FR) — resumen
- **FR1** — Representar conceptos clasificados por categoría (tipo de dato, estructura de datos, estructura de control, función integrada, módulo, paradigma, principio transversal, operador, algoritmo, concepto de tipado/concurrencia, etc.).
- **FR2** — Representar relaciones de **prerrequisito** (transitivas) y de **contraste** (simétrica) entre conceptos.
- **FR3** — Asociar conceptos a **temas** curriculares y a **niveles de dominio**.
- **FR4** — Representar **errores conceptuales** y vincularlos al concepto subyacente.
- **FR5** — Representar **ejercicios**, **envíos** de estudiantes y **evaluaciones**.
- **FR6** — Soportar consultas de **ruta de aprendizaje** (cadena de prerrequisitos) por inferencia.

---

## 2. Reutilización de vocabularios (LOT · *Ontological Resource Reuse*)

| Prefijo | Vocabulario | Uso |
|---|---|---|
| `skos:` | SKOS | Red conceptual, definiciones/notas/ejemplos, alineamientos |
| `schema:` | schema.org | `cfkg:Recurso ⊑ schema:LearningResource`, `schema:url` |
| `dcterms:` | DC Terms | Metadatos (título, autoría, licencia, fechas, fuente) |
| `foaf:` | FOAF | `cfkg:Estudiante ⊑ foaf:Person`, `foaf:name` |
| `wd:` | Wikidata | `skos:exactMatch` a entidades (48 enlaces) |
| `dbr:` | DBpedia | `skos:closeMatch` a recursos (62 enlaces) |
| `vann:`, `cc:`, `owl:`, `rdfs:`, `xsd:` | VANN / CC / OWL / RDFS / XSD | Metadatos del vocabulario y axiomática |


---

## 3. Preguntas de competencia (CQ) y prueba SPARQL

Las 14 CQ se ejecutan con `scripts/cq_lot.py`; las marcadas *[OWL-RL]* se evalúan sobre el cierre OWL-RL (transitividad / subpropiedades). Entre paréntesis, las filas obtenidas en la v2.0.

Prefijos comunes:
```sparql
PREFIX cfkg: <https://w3id.org/codefeedback-kg/schema#>
PREFIX cfr:  <https://w3id.org/codefeedback-kg/id/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
```

**CQ1.** ¿Qué conceptos son prerrequisito (directo o indirecto) de la recursión? *[OWL-RL]* — (1)
```sparql
SELECT DISTINCT ?prereq WHERE { cfr:recursion cfkg:requierePrerrequisito+ ?prereq . }
```

**CQ2.** ¿Qué conceptos pertenecen al tema de POO? — (29)
```sparql
SELECT ?c WHERE { ?c cfkg:perteneceATema cfr:T_poo . }
```

**CQ3.** ¿Qué errores conceptuales recaen sobre conceptos de nivel avanzado? — (7)
```sparql
SELECT ?err ?c WHERE { ?err cfkg:errorSobreConcepto ?c . ?c cfkg:aNivelDominio cfr:avanzado . }
```

**CQ4.** ¿Qué conceptos están alineados con Wikidata? — (48)
```sparql
SELECT ?c ?qid WHERE { ?c skos:exactMatch ?qid .
  FILTER(STRSTARTS(STR(?qid), "http://www.wikidata.org/")) }
```

**CQ5.** ¿Hay algún concepto sin ejemplo de código? (debe ser 0) *[OWL-RL]* — (0)
```sparql
SELECT ?c WHERE { ?c a cfkg:Concepto . FILTER NOT EXISTS { ?c skos:example ?e } }
```

**CQ6.** ¿Qué conceptos acumulan más prerrequisitos directos? — (10)
```sparql
SELECT ?c (COUNT(?p) AS ?n) WHERE { ?c cfkg:requierePrerrequisito ?p . }
GROUP BY ?c ORDER BY DESC(?n) LIMIT 10
```

**CQ7.** ¿Qué pares de conceptos conviene explicar por contraste (confusiones)? — (8)
```sparql
SELECT ?a ?b WHERE { ?a cfkg:contrastaCon ?b . FILTER(STR(?a) < STR(?b)) }
```

**CQ8.** ¿Qué ejercicios cubren la búsqueda binaria y con qué dificultad? — (1)
```sparql
SELECT ?ej ?dif WHERE { ?ej cfkg:cubreConcepto cfr:busqueda_binaria ; cfkg:tieneDificultad ?dif . }
```

**CQ9.** ¿Qué recursos ilustran algún concepto? — (2)
```sparql
SELECT ?rec ?c WHERE { ?rec cfkg:ilustraConcepto ?c . }
```

**CQ10.** ¿Qué conceptos se introdujeron en Python 3.10? — (2)
```sparql
SELECT ?c ?v WHERE { ?c cfkg:introducidoEnVersion ?v . FILTER(?v = "3.10") }
```

**CQ11.** ¿Qué conceptos tienen complejidad temporal logarítmica? — (6)
```sparql
SELECT ?c ?o WHERE { ?c cfkg:tieneComplejidadTemporal ?o . FILTER(CONTAINS(?o, "log")) }
```

**CQ12.** ¿Qué conceptos son especialización (vía `skos:broaderTransitive`) de la comprensión de listas? *[OWL-RL]* — (3)
```sparql
SELECT ?sub WHERE { ?sub skos:broaderTransitive cfr:comprension_listas . }
```

**CQ13.** ¿Qué envíos manifiestan un error y sobre qué concepto? — (2)
```sparql
SELECT ?env ?err ?c WHERE { ?env cfkg:manifiestaError ?err . ?err cfkg:errorSobreConcepto ?c . }
```

**CQ14.** ¿Qué conceptos avanzados pertenecen al tema de concurrencia? — (12)
```sparql
SELECT ?c WHERE { ?c cfkg:perteneceATema cfr:T_concurrencia ; cfkg:aNivelDominio cfr:avanzado . }
```

*(≥ 12 requeridas; se aportan 14, todas con resultado no vacío salvo CQ5, cuyo resultado vacío es la respuesta correcta deseada.)*

---

## 4. Trazabilidad requisito → artefacto

| Requisito | Verificación |
|---|---|
| NFR1 consistencia | `scripts/verificar_v2.py` (0 `owl:Nothing`) · `salidas/v2-target-report.json` |
| NFR2 sin `owl:sameAs` | `reporte_v2.py` → `owl:sameAs == 0` |
| NFR4 dominio+rango | `reporte_v2.py` → *propiedades sin dominio/rango == 0* |
| NFR5 cobertura SKOS | forma SHACL `cfkg:ConceptoSkosShape` (222/222) |
| NFR6 ≥4 vocabularios | `reporte_v2.py` → 5 vocabularios |
| FR1–FR6 | preguntas de competencia CQ1–CQ14 (`cq_lot.py`) |

---

## 5. Fase de implementación, publicación y mantenimiento (LOT)
- **Implementación:** constructor determinista `scripts/construir_v2.py` (rdflib) — carga la base, añade axiomas/conceptos, verifica cierre OWL-RL y serializa solo triples afirmados.
- **Publicación:** documentación HTML con **pyLODE** (`docs/pylode/index.html`); ver `docs/FAIR-5STAR-MAINTENANCE.md`.
- **Mantenimiento:** política de versionado y curación documentada en `docs/FAIR-5STAR-MAINTENANCE.md`.

## 6. Referencias normativas
- W3C **OWL 2 RL** Profile (OWL 2 Web Ontology Language Profiles).
- W3C **SKOS** Simple Knowledge Organization System Reference.
- W3C **SHACL** Shapes Constraint Language.
- **FAIR** Guiding Principles (Wilkinson et al., 2016); **5★ Open Data** (T. Berners-Lee).
- **LOT** — Linked Open Terms methodology (Poveda-Villalón et al.).
- Keuning, Jeuring & Heeren (2019), *A systematic literature review of automated feedback generation for programming exercises* (DOI 10.1145/3231711).
- Licencia de los datos y del esquema: **CC BY 4.0**.
