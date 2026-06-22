# Manual de carga y prueba del CodeFeedback-KG en GraphDB

Guía paso a paso para cargar el Grafo de Conocimiento Educativo de Python
canónico (`ontologia/codefeedback-kg-150.ttl`, 157 conceptos) en **GraphDB**, activar la inferencia, ejecutar las
consultas SPARQL y validar con las formas SHACL. Pensado para que el profesor
pueda reproducir y evaluar el entregable de forma independiente.

GraphDB se construye sobre RDF4J y proporciona razonamiento conforme a estándar
para RDFS, OWL-Horst, OWL2-RL y OWL2-QL, materializando los hechos inferidos en
el momento de la importación. Para este grafo, el *ruleset* recomendado es
**OWL2-RL (optimizado)**, que cubre las características OWL empleadas
(propiedades transitivas, inversas, simétricas, disjunciones y subsunción).

## 1. Instalación

1. Descargar **GraphDB Desktop** (Ontotext) e instalarlo. La edición Desktop
   incluye su propio Java; no es necesario instalar Java por separado.
2. Arrancar la aplicación. El Workbench queda accesible en
   `http://localhost:7200`.

## 2. Crear el repositorio con inferencia

Vía interfaz (Workbench):

1. *Setup → Repositories → Create new repository → GraphDB repository*.
2. **Repository ID:** `codefeedback-kg`.
3. En *Ruleset*, seleccionar **OWL2-RL (Optimized)**.
4. Dejar el resto de valores por defecto y *Create*.

Esto crea un repositorio que, al importar datos, deduce automáticamente los
hechos implícitos (p. ej. que `cfr:bucle_for` es un `cfkg:Concepto` por
`rdfs:subClassOf`, o los prerrequisitos transitivos).

## 3. Importar la ontología y los datos

1. Seleccionar el repositorio `codefeedback-kg` (esquina superior derecha).
2. *Import → RDF → Upload RDF files*.
3. Subir `ontologia/codefeedback-kg-150.ttl`. En el diálogo de importación dejar el
   *Base IRI* por defecto y *Target graphs → default*. Pulsar *Import*.
4. (Opcional) Subir también `ontologia/shapes-ekg.ttl` a un grafo con nombre,
   p. ej. `http://codefeedback-kg/shapes`, si se va a usar la validación SHACL del
   apartado 5.

Tras la importación, en *Explore → Graphs overview* puede verse el grafo y el
número de enunciados (afirmados + inferidos).

## 4. Ejecutar las consultas SPARQL

En *SPARQL* (Query & Update), pegar el contenido de cualquier fichero de
`consultas/` y pulsar *Run*. Ejemplos destacados:

- **`02_inferencia_conceptos.rq`** — recupera todo lo que es `cfkg:Concepto`.
  Con el repositorio OWL2-RL devuelve los **157** conceptos (la pertenencia se
  infiere de `rdfs:subClassOf`). Para contrastar el comportamiento *sin*
  inferencia, puede crearse un segundo repositorio con *ruleset* **Empty** e
  importar el mismo fichero: la misma consulta devolverá **0** filas.
- **`03_prerrequisitos_transitivos.rq`** — prerrequisitos directos e indirectos
  mediante *property path* (`+`); funciona con cualquier *ruleset* porque el
  camino se resuelve en tiempo de consulta.
- **`06_construct_prereq_directos.rq`** — `CONSTRUCT` que materializa el cierre
  transitivo como triples directos.
- **`07_diagnostico_envio.rq`** — caso de uso del sistema: de un envío de
  estudiante a su error, el concepto afectado y los prerrequisitos a reforzar.
- **`08_federada_wikidata.rq`** — consulta federada (`SERVICE`) al endpoint de
  Wikidata; requiere conexión a Internet.

## 5. Validación SHACL (opcional)

GraphDB admite SHACL por repositorio. Para validar la forma del grafo:

1. Crear el repositorio con *Supports SHACL validation* activado (o usar la
   consola SHACL del Workbench si está disponible en la versión instalada).
2. Cargar `ontologia/shapes-ekg.ttl` en el grafo de formas SHACL.
3. Al insertar datos que violen las restricciones, GraphDB rechaza la
   transacción e informa de las violaciones (p. ej. un concepto sin tema o un
   ejercicio sin enunciado, como en `ontologia/ejemplo-invalido.ttl`).

Alternativamente, la validación SHACL puede ejecutarse sin GraphDB con el
script `scripts/validar.py` (usa `pyshacl`).

## 6. Carga automatizada (script)

Para evitar los pasos manuales, `scripts/cargar_graphdb.py` crea el repositorio
con el *ruleset* indicado e importa el grafo y las formas mediante la API REST
de GraphDB:

```bash
python scripts/cargar_graphdb.py --url http://localhost:7200 --repo codefeedback-kg --ruleset owl2-rl-optimized --shapes
```

El script comprueba la conexión, crea el repositorio si no existe, carga
`codefeedback-kg-150.ttl`, opcionalmente las formas SHACL, y ejecuta una consulta de
verificación que cuenta los conceptos inferidos. Requiere que GraphDB esté en
ejecución en la URL indicada.

## Resumen de comprobaciones esperadas

| Acción | Resultado esperado |
|---|---|
| Importar `codefeedback-kg-150.ttl` (OWL2-RL) | 1772 enunciados afirmados → 4786 tras inferencia |
| `02_inferencia_conceptos.rq` (OWL2-RL) | 157 conceptos |
| `02_inferencia_conceptos.rq` (Empty) | 0 conceptos |
| `03_prerrequisitos_transitivos.rq` | 5 prerrequisitos de búsqueda binaria |
| `06_construct_prereq_directos.rq` | 356 triples construidos |
| Validación SHACL de `ejemplo-invalido.ttl` | 6 violaciones |
