# CodeFeedback-KG v2.0 — FAIR, 5★ Open Data y política de mantenimiento

**Ontología:** CodeFeedback-KG 2.0.0 · **Licencia:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
**IRI de esquema:** `https://w3id.org/codefeedback-kg/schema#` · **versionIRI:** `…/schema/2.0.0`

Este documento mapea cada **principio FAIR** y cada **nivel 5★** a un artefacto concreto del repositorio, y fija la política de mantenimiento/versionado (fase de *Maintenance* de LOT).

---

## 1. Principios FAIR → artefacto

### Findable (localizable)
| Principio | Implementación | Artefacto |
|---|---|---|
| **F1** Identificadores únicos y persistentes | IRIs `w3id.org` para esquema (`cfkg:`) e individuos (`cfr:`); `owl:versionIRI` SemVer | `ontologia/codefeedback-kg.ttl` (cabecera `owl:Ontology`) |
| **F2** Metadatos ricos | `dcterms:title/description/creator/contributor/created/issued/modified/license`, `vann:preferredNamespace*` | cabecera `owl:Ontology` |
| **F3** Los metadatos incluyen el identificador del dato | El `owl:Ontology` se identifica con el IRI del namespace y referencia su `versionIRI` | cabecera |
| **F4** Indexables/consultables | Serialización Turtle + RDF/XML + JSON-LD + N-Triples; documentación HTML navegable | `salidas/codefeedback-kg.{rdf,jsonld,nt}`, `docs/pylode/index.html`, `ontologia/void.ttl` |

### Accessible (accesible)
| Principio | Implementación | Artefacto |
|---|---|---|
| **A1** Protocolo abierto/estándar | HTTP(S) sobre `w3id.org`; formatos RDF estándar recuperables | TTL/RDF/JSON-LD/NT |
| **A1.2** Autenticación cuando proceda | No requiere autenticación (datos abiertos) | — |
| **A2** Persistencia de los metadatos | Los snapshots versionados se conservan (`codefeedback-kg-150.ttl` = v1.0 congelada; copias `*.bak-*`) | `ontologia/` |

### Interoperable (interoperable)
| Principio | Implementación | Artefacto |
|---|---|---|
| **I1** Lenguaje formal de representación | RDF/OWL 2 RL + SKOS + SHACL | `codefeedback-kg.ttl`, `shapes-codefeedback-kg.ttl` |
| **I2** Vocabularios FAIR | Reutiliza SKOS, schema.org, DC Terms, FOAF, VANN, CC | prefijos del TTL |
| **I3** Referencias cruzadas cualificadas | `skos:exactMatch` (Wikidata, 48), `skos:closeMatch` (DBpedia, 62); **nunca `owl:sameAs`** | enlaces en el TTL |

### Reusable (reutilizable)
| Principio | Implementación | Artefacto |
|---|---|---|
| **R1** Atributos plurales y precisos | Etiquetas `@es`/`@en`, `skos:definition`+`scopeNote`+`example` en los 222 conceptos | TTL |
| **R1.1** Licencia clara | `dcterms:license` y `cc:license` = CC BY 4.0 | cabecera |
| **R1.2** Procedencia | Reificación de procedencia (`rdf:Statement` + `dcterms:source`), referencia Keuning et al. 2019 | `cfr:stmt_offbyone`, `cfr:ref_keuning2019` |
| **R1.3** Estándares de la comunidad | OWL 2 RL, SKOS, SHACL; metodología LOT | `docs/REQUIREMENTS-LOT.md` |

---

## 2. Niveles **5★ Open Data** (Tim Berners-Lee)

| Nivel | Criterio | Cumplimiento |
|---|---|---|
| ★ | Disponible en la web con licencia abierta | CC BY 4.0 declarada en la cabecera |
| ★★ | Datos estructurados legibles por máquina | Turtle (no PDF/imagen) |
| ★★★ | Formato no propietario | Turtle, RDF/XML, JSON-LD, N-Triples (W3C) |
| ★★★★ | Uso de URIs para identificar cosas | IRIs `w3id.org` dereferenciables para clases, propiedades e individuos |
| ★★★★★ | Enlaces a otros datos (Linked Data) | `skos:exactMatch`→Wikidata, `skos:closeMatch`→DBpedia; alineamiento de clases con schema.org y FOAF |

**Resultado: 5★** (Linked Open Data).

---

## 3. Política de mantenimiento y versionado (LOT · *Maintenance*)

### 3.1 Versionado semántico (SemVer) del esquema
- **MAJOR** — cambios incompatibles (borrado/renombrado de clases o propiedades, cambios de dominio/rango que invaliden datos). Ej.: 1.0.0 → 2.0.0 (este release: nuevas clases, restricciones, disjunciones; **siempre aditivo**, sin borrar v1.0).
- **MINOR** — adiciones retrocompatibles (nuevos conceptos, alineamientos, formas SHACL).
- **PATCH** — correcciones (p. ej. corrección de un QID erróneo, erratas en definiciones).
- Cada release fija `owl:versionInfo` y `owl:versionIRI` (`…/schema/MAJOR.MINOR.PATCH`).

### 3.2 Snapshots y reproducibilidad
- La **v1.0 congelada** (`codefeedback-kg-150.ttl`) se conserva inmutable porque respalda el estudio con humanos (N8); **nunca se edita**.
- Antes de cada edición se crea una copia `*.bak-YYYYMMDD-HHMM`.
- El grafo v2.0 se regenera de forma **determinista** con `scripts/construir_v2.py` a partir de la base; el constructor verifica el cierre OWL-RL (consistencia) antes de serializar.

### 3.3 Aseguramiento de la calidad (CI manual)
Antes de publicar un release deben pasar:
1. `python scripts/construir_v2.py` — construcción + verificación de consistencia OWL-RL.
2. `python scripts/verificar_v2.py` — parse, cierre OWL-RL, SHACL `Conforms:True` en el grafo válido y `violaciones>0` sobre `ejemplo-invalido.ttl`.
3. `python scripts/reporte_v2.py` — re-derivación de las dimensiones §10 (todas PASS).
4. `python scripts/cq_lot.py` — preguntas de competencia LOT.
5. `python -m pylode ontologia/codefeedback-kg.ttl -o docs/pylode/index.html` — documentación.

### 3.4 Política de enlaces externos
- Los alineamientos externos se expresan con `skos:exactMatch` (QID de Wikidata) y `skos:closeMatch` (recursos de DBpedia), enlazando cada concepto con la entidad equivalente del vocabulario de destino y registrando el enlace en el grafo Turtle.
- Los enlaces de identidad usan `skos:exactMatch`/`closeMatch`; **`owl:sameAs` se mantiene en 0** para no propagar identidad lógica entre vocabularios heterogéneos bajo OWL-RL.

### 3.5 Gobernanza y contacto
- **Responsable:** Adrián Bueno Junquero.
- Incidencias y propuestas de nuevos conceptos/alineamientos: vía el repositorio del proyecto.

---

## 4. Documentación y herramientas
- **pyLODE** `docs/pylode/index.html` — documentación HTML del vocabulario (generada de forma reproducible).
- **WIDOCO** — *no disponible en este entorno* (no hay `widoco.jar` ni runtime Java instalado; `java -version` → *command not found*). La ausencia queda documentada y se recurre a pyLODE. Para regenerar con WIDOCO cuando haya Java: `java -jar widoco.jar -ontFile ontologia/codefeedback-kg.ttl -outFolder docs/widoco -rewriteAll -getOntologyMetadata -lang es-en`.
