# CodeFeedback-KG — Grafo de Conocimiento Educativo de Programación en Python

Grafo de conocimiento educativo (TBox + ABox) del proyecto **CodeFeedback-KG**, que
modela el dominio de la programación en Python para anclar la generación de
retroalimentación formativa mediante una arquitectura GraphRAG + LLM.

- **Autor:** Adrián Bueno Junquero

El grafo modela el dominio de la programación en Python (conceptos,
prerrequisitos, contrastes, temas, ejercicios, errores conceptuales,
recursos y perfiles de estudiante) y está diseñado para cumplir un doble
papel: ser un entregable autónomo de Web Semántica y, a la vez, el grafo que
la arquitectura RAG consultará para anclar la generación de
retroalimentación.

## Pila tecnológica

RDF 1.1 (Turtle) · RDFS · OWL 2 RL · SPARQL 1.1 (SELECT/CONSTRUCT) · SHACL ·
SKOS, Dublin Core, FOAF, schema.org · enlace a Wikidata (`skos:exactMatch`).
Herramientas: `rdflib`, `owlrl` (inferencia RDFS/OWL-RL), `pyshacl`
(validación). Cargable en **GraphDB**, **RDFShape** y **RDFPlayground**.

## Estructura

```
Entregable-Grafo-EKG/
├── ontologia/
│   ├── codefeedback-kg.ttl         # Grafo v2.0 (TBox + ABox), artefacto principal: 222 conceptos.
│   ├── codefeedback-kg-150.ttl     # Grafo canónico v1.0 congelado: 157 conceptos.
│   ├── codefeedback-kg-base.ttl    # Grafo BASE didáctico (539 triples), punto de partida del constructor.
│   ├── shapes-ekg.ttl         # Formas SHACL (validación de forma del grafo).
│   └── ejemplo-invalido.ttl   # Datos con violaciones deliberadas (demo SHACL).
├── consultas/                 # 10 consultas SPARQL (.rq)
│   ├── 01_conceptos_por_tema.rq
│   ├── 02_inferencia_conceptos.rq      # contraste NONE vs RDFS
│   ├── 03_prerrequisitos_transitivos.rq # property path +
│   ├── 04_ruta_aprendizaje.rq
│   ├── 05_errores_por_concepto.rq
│   ├── 06_construct_prereq_directos.rq # CONSTRUCT
│   ├── 07_diagnostico_envio.rq         # caso de uso RAG
│   ├── 08_federada_wikidata.rq         # consulta federada (requiere red)
│   ├── 09_update_depuracion.rq         # administración: UPDATE/INSERT/DELETE (no la corre consultar.py)
│   └── 10_jerarquia_skos_estrella.rq   # property path * (cierre transitivo reflexivo)
├── scripts/
│   ├── inferir.py             # cierre OWL-RL y export del grafo inferido
│   ├── validar.py             # validación SHACL (grafo válido e inválido)
│   ├── consultar.py           # ejecuta las consultas (con/sin inferencia)
│   └── exportar.py            # Turtle -> JSON-LD / N-Triples / RDF-XML
├── salidas/                   # resultados generados (informes, exports)
└── README.md
```

## Cómo ejecutarlo

Requiere Python 3.12 y las librerías (ya instaladas en el equipo):

```bash
pip install rdflib pyshacl owlrl
```

Desde la carpeta `Entregable-Grafo-EKG/`:

```bash
python scripts/inferir.py      # grafo canónico codefeedback-kg-150.ttl: 1772 triples afirmados -> 4786 tras OWL-RL
python scripts/validar.py      # grafo principal CONFORME; ejemplo inválido: 6 violaciones
python scripts/consultar.py                    # consultas con inferencia
python scripts/consultar.py --sin-inferencia   # consultas sin inferencia (contraste)
python scripts/exportar.py     # genera JSON-LD, N-Triples y RDF/XML en salidas/
```

### Resultados verificados

El repositorio incluye tres grafos Turtle, todos cargables y reproducibles:

- **`codefeedback-kg.ttl`** — **artefacto principal, v2.0** (`owl:versionIRI`
  `…/schema/2.0.0`): **222 conceptos**, **48 enlaces `skos:exactMatch`** a Wikidata
  y **62 `skos:closeMatch`** a DBpedia; **3291 triples afirmados** → **8957 tras el
  cierre OWL-RL**. Validación SHACL (18 formas): **conforme** (0 violaciones); el
  ejemplo inválido produce **9 violaciones**. Se regenera de forma determinista con
  `scripts/construir_v2.py` (detalle en `docs/REQUIREMENTS-LOT.md` y
  `docs/FAIR-5STAR-MAINTENANCE.md`).
- **`codefeedback-kg-150.ttl`** — **grafo canónico v1.0 (congelado)**, **157 conceptos**:
  **1772 triples afirmados** y **4786 tras el cierre OWL-RL**, con **30 enlaces
  `skos:exactMatch`** a Wikidata.
- **`codefeedback-kg-base.ttl`** — **grafo BASE didáctico**, punto de partida del
  constructor v2.0.

La tabla siguiente recoge la comprobación reproducible sobre el grafo **BASE**
(`codefeedback-kg-base.ttl`):

| Comprobación (grafo BASE, `codefeedback-kg-base.ttl`) | Resultado |
|---|---|
| Parseo de la ontología | 539 triples afirmados |
| Cierre OWL-RL | +965 triples inferidos (1504 totales) |
| Validación SHACL del grafo principal | **Conforme** (0 violaciones) |
| Validación del ejemplo inválido | 6 violaciones detectadas |
| Consulta 02 (`?x a cfkg:Concepto`) sin inferencia | **0 filas** |
| Consulta 02 con inferencia RDFS | **26 filas** |
| Round-trip JSON-LD / N-Triples / RDF-XML | 539 triples íntegros |

El contraste 0 → 26 de la consulta 02 es la evidencia de la inferencia RDFS:
ningún individuo se tipa a mano como `cfkg:Concepto`; la pertenencia se deduce
de `rdfs:subClassOf` al activar el razonador.

## Decisiones de modelado (mapa con el material docente)

- **Clasificación e inferencia** (*Clasificación de entidades en RDF*,
  *Sobre el uso de la clasificación*): los individuos se tipan por su
  subcategoría (`cfr:bucle_for a cfkg:EstructuraDeControl`) y la pertenencia
  a `cfkg:Concepto`/`skos:Concept` se obtiene por `rdfs:subClassOf`, no se
  afirma a mano.
- **Relaciones y jerarquías** (*Declaración de relaciones*): propiedades con
  `rdfs:domain`/`rdfs:range` cuidados (sin el error de reusar un predicado de
  «nombre» entre clases incompatibles: se usa siempre `rdfs:label`), y
  `rdfs:subPropertyOf` (`esPrerrequisitoDe`, `contrastaCon` ⊑
  `relacionadoConceptualmenteCon`).
- **Atributos textuales** (*Asignación de atributos textuales*): literales solo
  en objeto, tipados (`xsd:integer`, `xsd:date`, `xsd:gYear`, `xsd:decimal`) y
  con idioma (`@es`/`@en`); etiquetado estándar con `rdfs:label`/`skos:prefLabel`.
- **Mejoras de expresividad** (*Mejoras sobre la expresividad*): relación
  N-aria con nodo intermedio (`cfkg:EvaluacionDeConcepto`) y reificación
  estilo Wikidata (`rdf:Statement` + `dcterms:source`) para la procedencia
  bibliográfica de los errores conceptuales.
- **Capa OWL (ampliación):** `owl:TransitiveProperty` (prerrequisitos),
  `owl:inverseOf` (`esPrerrequisitoDe`/`requierePrerrequisito`),
  `owl:SymmetricProperty` (`contrastaCon`), `owl:AllDisjointClasses` y
  `owl:FunctionalProperty`. Perfil **OWL 2 RL** (compatible con GraphDB y con
  `owlrl`).
- **Reutilización de vocabularios y enlazado:** SKOS, Dublin Core, FOAF,
  schema.org y `skos:exactMatch` a Wikidata para alinear conceptos del grafo con
  sus entidades equivalentes sin colapsar identidades.

## Cómo lo prueba el profesor

### Opción A — GraphDB (recomendada)

1. Instalar **GraphDB Desktop** (incluye Java; no requiere instalación aparte).
2. Crear un repositorio con *ruleset* **OWL2-RL** (o *RDFS-Plus (Optimized)*).
3. *Import → Upload RDF files* → `ontologia/codefeedback-kg.ttl`.
4. En *SPARQL*, pegar cualquier consulta de `consultas/` y ejecutarla. GraphDB
   materializa la inferencia al importar, por lo que la consulta 02 devuelve los
   222 conceptos directamente.
5. (Opcional) Validación SHACL: cargar `ontologia/shapes-ekg.ttl` como grafo de
   formas en un repositorio con SHACL activado.

### Opción B — RDFShape / RDFPlayground (en línea, sin instalación)

1. Abrir [RDFShape](https://rdfshape.weso.es) o
   [RDFPlayground](https://rdfplayground.dcc.uchile.cl). Ambas son complementarias:
   **RDFPlayground** *razona* (infiere con OWL-RL y RDFS) y ejecuta SPARQL, por lo
   que reproduce el contraste de inferencia de la consulta 02; **RDFShape** se centra
   en la *validación de formas* (SHACL y ShEx) del grafo. Para el cierre OWL-RL/RDFS
   y las consultas conviene RDFPlayground; para validar las formas, RDFShape.
2. Pegar el contenido de `codefeedback-kg.ttl` como grafo de datos.
3. *RDF::Analysis & Visualization* para validar sintaxis y visualizar el grafo.
4. *SPARQL query* para ejecutar las consultas; conmutar **inferencia NONE/RDFS**
   para reproducir el contraste de la consulta 02.

## Cobertura de los Resultados de Aprendizaje

- **RA1 (modelar un dominio):** ontología RDFS/OWL del dominio Python en Turtle.
- **RA2 (razonadores: inferencia y depuración):** cierre OWL-RL (`inferir.py`)
  y validación SHACL (`validar.py`).
- **RA3 (enlazar, consultar e integrar):** consultas SPARQL y consulta federada
  a Wikidata (`08_federada_wikidata.rq`), enlace `skos:exactMatch`.
- **RA4 (tecnología y casos):** pila estándar de la Web Semántica aplicada a un
  caso real (evaluación formativa de programación).

## Licencia

Grafo y ontología bajo **CC BY 4.0**; código bajo **Apache-2.0**. Los espacios de
nombres del proyecto (`w3id.org/codefeedback-kg/...`) son provisionales
y repuntables a su publicación definitiva.
