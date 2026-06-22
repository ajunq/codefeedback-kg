import json
from pathlib import Path

from rdflib import Graph, Literal, Namespace, OWL, RDF, RDFS, URIRef, XSD
from rdflib.namespace import SKOS

SCHEMA = Namespace("http://schema.org/")

BASE = Path(__file__).resolve().parent.parent
ONTO = BASE / "ontologia" / "codefeedback-kg.ttl"
SALIDA = BASE / "ontologia" / "codefeedback-kg-150.ttl"

CFKG = Namespace("https://w3id.org/codefeedback-kg/schema#")
CFR = Namespace("https://w3id.org/codefeedback-kg/id/")

CAT = {"EC": "EstructuraDeControl", "ED": "EstructuraDeDatos", "TD": "TipoDeDato",
       "PA": "Paradigma", "FI": "FuncionIntegrada", "ML": "ModuloLibreria",
       "PT": "PrincipioTransversal"}

TEMAS = {
    "T_tipos": ("Sistema de tipos", "Type system"),
    "T_funcional": ("Programación funcional", "Functional programming"),
    "T_concurrencia": ("Concurrencia", "Concurrency"),
    "T_ficheros": ("Ficheros y E/S", "Files and I/O"),
    "T_strings": ("Cadenas de texto", "Strings"),
    "T_modulos": ("Módulos y paquetes", "Modules and packages"),
    "T_testing": ("Pruebas y estilo", "Testing and style"),
    "T_algoritmos": ("Algoritmos", "Algorithms"),
}

# (id, es, en, categoria, tema, dificultad, prerequisitos, contrastes)
C = [
    ("tipo_float", "Flotante (float)", "Float", "TD", "T_tipos", 1, [], ["tipo_int"]),
    ("tipo_complex", "Complejo (complex)", "Complex", "TD", "T_tipos", 3, ["tipo_float"], []),
    ("tipo_none", "NoneType (None)", "NoneType", "TD", "T_tipos", 1, [], []),
    ("tipo_bytes", "Bytes", "Bytes", "TD", "T_tipos", 3, ["tipo_str"], []),
    ("conversion_tipos", "Conversión de tipos", "Type casting", "PT", "T_tipos", 2, ["tipo_int", "tipo_str"], []),
    ("anotaciones_tipo", "Anotaciones de tipo", "Type hints", "PT", "T_tipos", 3, ["funcion"], []),
    ("typing_optional", "typing.Optional", "Optional", "PT", "T_tipos", 3, ["anotaciones_tipo", "tipo_none"], []),
    ("typing_union", "typing.Union", "Union", "PT", "T_tipos", 3, ["anotaciones_tipo"], []),
    ("typing_generics", "Genéricos (TypeVar)", "Generics", "PA", "T_tipos", 4, ["anotaciones_tipo", "clase"], []),
    ("dataclass", "Dataclass", "Dataclass", "PA", "T_tipos", 3, ["clase", "anotaciones_tipo"], []),
    ("namedtuple", "namedtuple", "Named tuple", "ED", "T_tipos", 3, ["tupla"], []),
    ("enum_tipo", "Enumeración (Enum)", "Enum", "PA", "T_tipos", 3, ["clase"], []),
    ("truthiness", "Valores de verdad", "Truthiness", "PT", "T_tipos", 2, ["tipo_bool"], []),
    ("mutable_inmutable", "Mutable vs inmutable", "Mutable vs immutable", "PT", "T_tipos", 3, ["mutabilidad"], ["tupla"]),
    ("identidad_objetos", "Identidad de objetos (is)", "Object identity", "PT", "T_tipos", 3, ["mutable_inmutable"], []),
    ("copia_superficial", "Copia superficial", "Shallow copy", "PT", "T_tipos", 4, ["lista", "mutabilidad"], []),
    ("copia_profunda", "Copia profunda", "Deep copy", "PT", "T_tipos", 4, ["copia_superficial"], ["copia_superficial"]),
    ("comprension_dicts", "Comprensión de diccionarios", "Dict comprehension", "EC", "T_estructuras", 4, ["diccionario", "comprension_listas"], []),
    ("comprension_sets", "Comprensión de conjuntos", "Set comprehension", "EC", "T_estructuras", 4, ["conjunto", "comprension_listas"], []),
    ("deque", "collections.deque", "deque", "ED", "T_estructuras", 3, ["lista"], []),
    ("defaultdict", "collections.defaultdict", "defaultdict", "ED", "T_estructuras", 3, ["diccionario"], []),
    ("counter", "collections.Counter", "Counter", "ED", "T_estructuras", 3, ["diccionario"], []),
    ("heap", "Montículo (heapq)", "Heap", "ED", "T_estructuras", 4, ["lista", "complejidad"], []),
    ("pila", "Pila (stack)", "Stack", "ED", "T_estructuras", 2, ["lista"], ["cola"]),
    ("cola", "Cola (queue)", "Queue", "ED", "T_estructuras", 2, ["lista"], ["pila"]),
    ("desempaquetado", "Desempaquetado", "Unpacking", "PT", "T_estructuras", 2, ["tupla", "lista"], []),
    ("operador_estrella", "Operador * y **", "Star operator", "PT", "T_estructuras", 3, ["desempaquetado"], []),
    ("iterables", "Iterables", "Iterables", "PT", "T_estructuras", 2, ["lista"], []),
    ("indexacion_negativa", "Indexación negativa", "Negative indexing", "PT", "T_estructuras", 2, ["indexacion"], []),
    ("parametros", "Parámetros y argumentos", "Parameters", "PT", "T_funciones", 2, ["funcion"], []),
    ("args_kwargs", "*args y **kwargs", "args and kwargs", "PT", "T_funciones", 3, ["parametros", "operador_estrella"], []),
    ("valor_por_defecto", "Argumentos por defecto", "Default arguments", "PT", "T_funciones", 2, ["parametros"], []),
    ("argumentos_nombrados", "Argumentos por nombre", "Keyword arguments", "PT", "T_funciones", 2, ["parametros"], []),
    ("retorno_multiple", "Retorno múltiple", "Multiple return", "PT", "T_funciones", 2, ["funcion", "tupla"], []),
    ("funcion_lambda", "Función lambda", "Lambda", "PT", "T_funcional", 3, ["funcion"], []),
    ("funcion_orden_superior", "Funciones de orden superior", "Higher-order functions", "PT", "T_funcional", 4, ["funcion"], []),
    ("map_func", "map()", "map", "FI", "T_funcional", 3, ["funcion_orden_superior", "iterables"], []),
    ("filter_func", "filter()", "filter", "FI", "T_funcional", 3, ["funcion_orden_superior", "iterables"], []),
    ("reduce_func", "functools.reduce()", "reduce", "FI", "T_funcional", 4, ["funcion_orden_superior"], []),
    ("closure", "Clausura (closure)", "Closure", "PT", "T_funcional", 4, ["ambito", "funcion"], []),
    ("decorador", "Decorador", "Decorator", "PA", "T_funcional", 5, ["closure", "funcion_orden_superior"], []),
    ("functools_wraps", "functools.wraps", "functools.wraps", "ML", "T_funcional", 4, ["decorador"], []),
    ("partial", "functools.partial", "partial", "ML", "T_funcional", 4, ["funcion_orden_superior"], []),
    ("recursion_cola", "Recursión de cola", "Tail recursion", "PT", "T_recursion", 5, ["recursion"], []),
    ("memoizacion", "Memoización (lru_cache)", "Memoization", "PT", "T_recursion", 4, ["recursion", "diccionario"], []),
    ("iterador", "Iterador (iter, next)", "Iterator", "PT", "T_funcional", 4, ["iterables"], []),
    ("generador", "Generador (yield)", "Generator", "EC", "T_funcional", 4, ["iterador", "funcion"], []),
    ("expresion_generadora", "Expresión generadora", "Generator expression", "EC", "T_funcional", 4, ["generador", "comprension_listas"], []),
    ("yield_from", "yield from", "yield from", "EC", "T_funcional", 5, ["generador"], []),
    ("match_case", "match-case", "Structural pattern matching", "EC", "T_control", 4, ["condicional"], []),
    ("with_context", "Sentencia with", "with statement", "EC", "T_control", 4, ["excepcion"], []),
    ("context_manager", "Gestor de contexto", "Context manager", "PA", "T_control", 5, ["with_context", "clase"], []),
    ("walrus", "Operador morsa (:=)", "Walrus operator", "PT", "T_control", 3, ["condicional"], []),
    ("ternario", "Operador ternario", "Ternary operator", "EC", "T_control", 2, ["condicional"], []),
    ("break_continue", "break y continue", "break and continue", "EC", "T_control", 2, ["bucle_for"], []),
    ("else_bucle", "else en bucles", "loop else", "EC", "T_control", 3, ["bucle_for"], []),
    ("enumerate_f", "enumerate()", "enumerate", "FI", "T_control", 2, ["bucle_for", "indexacion"], []),
    ("zip_f", "zip()", "zip", "FI", "T_control", 3, ["bucle_for", "iterables"], []),
    ("range_f", "range()", "range", "FI", "T_control", 1, ["bucle_for"], []),
    ("objeto", "Objeto / instancia", "Object", "PA", "T_poo", 3, ["clase"], []),
    ("atributo", "Atributo de instancia", "Attribute", "PA", "T_poo", 3, ["objeto"], []),
    ("metodo", "Método", "Method", "PA", "T_poo", 3, ["clase", "funcion"], []),
    ("init_method", "Constructor __init__", "Constructor", "PA", "T_poo", 3, ["metodo"], []),
    ("self_param", "Parámetro self", "self", "PA", "T_poo", 3, ["metodo"], []),
    ("encapsulacion", "Encapsulación", "Encapsulation", "PA", "T_poo", 4, ["atributo"], []),
    ("propiedad", "Propiedad (@property)", "Property", "PA", "T_poo", 4, ["encapsulacion", "decorador"], []),
    ("metodo_clase", "Método de clase", "Class method", "PA", "T_poo", 4, ["metodo", "decorador"], []),
    ("metodo_estatico", "Método estático", "Static method", "PA", "T_poo", 4, ["metodo", "decorador"], []),
    ("dunder", "Métodos especiales (dunder)", "Dunder methods", "PA", "T_poo", 4, ["metodo"], []),
    ("str_repr", "__str__ y __repr__", "str and repr", "PA", "T_poo", 4, ["dunder"], []),
    ("sobrecarga_operadores", "Sobrecarga de operadores", "Operator overloading", "PA", "T_poo", 5, ["dunder"], []),
    ("polimorfismo", "Polimorfismo", "Polymorphism", "PA", "T_poo", 4, ["herencia"], []),
    ("herencia_multiple", "Herencia múltiple", "Multiple inheritance", "PA", "T_poo", 5, ["herencia"], []),
    ("mro", "Orden de resolución (MRO)", "Method resolution order", "PA", "T_poo", 5, ["herencia_multiple"], []),
    ("super_call", "super()", "super", "PA", "T_poo", 4, ["herencia"], []),
    ("abstract_class", "Clase abstracta (ABC)", "Abstract base class", "PA", "T_poo", 5, ["herencia"], []),
    ("mixin", "Mixin", "Mixin", "PA", "T_poo", 5, ["herencia_multiple"], []),
    ("composicion", "Composición", "Composition", "PA", "T_poo", 4, ["objeto"], ["herencia"]),
    ("jerarquia_excepciones", "Jerarquía de excepciones", "Exception hierarchy", "EC", "T_excepciones", 3, ["excepcion", "herencia"], []),
    ("try_except_else", "try/except/else/finally", "try/except/else/finally", "EC", "T_excepciones", 3, ["excepcion"], []),
    ("raise_excepcion", "raise", "raise", "EC", "T_excepciones", 3, ["excepcion"], []),
    ("excepcion_personalizada", "Excepción personalizada", "Custom exception", "PA", "T_excepciones", 4, ["excepcion", "herencia"], []),
    ("encadenar_excepciones", "Encadenar excepciones", "Exception chaining", "EC", "T_excepciones", 4, ["raise_excepcion"], []),
    ("fstring", "f-strings", "f-strings", "PT", "T_strings", 2, ["tipo_str"], []),
    ("formato_str", "Formateo de cadenas", "String formatting", "PT", "T_strings", 2, ["tipo_str"], []),
    ("metodos_str", "Métodos de cadena", "String methods", "FI", "T_strings", 2, ["tipo_str"], []),
    ("slicing_str", "Slicing de cadenas", "String slicing", "PT", "T_strings", 3, ["slicing", "tipo_str"], []),
    ("regex", "Expresiones regulares (re)", "Regular expressions", "ML", "T_strings", 5, ["tipo_str"], []),
    ("encoding", "Codificación de texto", "Text encoding", "PT", "T_strings", 4, ["tipo_str", "tipo_bytes"], []),
    ("abrir_fichero", "Apertura de ficheros (open)", "File open", "FI", "T_ficheros", 3, ["with_context"], []),
    ("leer_fichero", "Lectura de ficheros", "File reading", "FI", "T_ficheros", 3, ["abrir_fichero"], []),
    ("escribir_fichero", "Escritura de ficheros", "File writing", "FI", "T_ficheros", 3, ["abrir_fichero"], []),
    ("json_mod", "Módulo json", "json module", "ML", "T_ficheros", 3, ["diccionario"], []),
    ("csv_mod", "Módulo csv", "csv module", "ML", "T_ficheros", 3, ["lista"], []),
    ("pathlib", "pathlib", "pathlib", "ML", "T_ficheros", 3, ["abrir_fichero"], []),
    ("import_mod", "import", "import", "PT", "T_modulos", 2, [], []),
    ("from_import", "from ... import", "from import", "PT", "T_modulos", 2, ["import_mod"], []),
    ("paquete", "Paquete", "Package", "ML", "T_modulos", 3, ["import_mod"], []),
    ("modulo_os", "Módulo os", "os module", "ML", "T_modulos", 3, ["import_mod"], []),
    ("modulo_sys", "Módulo sys", "sys module", "ML", "T_modulos", 3, ["import_mod"], []),
    ("modulo_math", "Módulo math", "math module", "ML", "T_modulos", 2, ["import_mod"], []),
    ("modulo_random", "Módulo random", "random module", "ML", "T_modulos", 2, ["import_mod"], []),
    ("modulo_datetime", "Módulo datetime", "datetime module", "ML", "T_modulos", 3, ["import_mod"], []),
    ("itertools_mod", "itertools", "itertools", "ML", "T_funcional", 4, ["iterables"], []),
    ("collections_mod", "collections", "collections", "ML", "T_modulos", 3, ["import_mod"], []),
    ("entorno_virtual", "Entornos virtuales (venv)", "Virtual environments", "PT", "T_modulos", 3, ["paquete"], []),
    ("pip_mod", "Gestor de paquetes (pip)", "pip", "PT", "T_modulos", 2, ["paquete"], []),
    ("gil", "GIL", "Global Interpreter Lock", "PT", "T_concurrencia", 5, [], []),
    ("hilos", "Hilos (threading)", "Threads", "PA", "T_concurrencia", 5, ["gil"], ["multiproceso"]),
    ("multiproceso", "Multiproceso", "Multiprocessing", "PA", "T_concurrencia", 5, ["gil"], ["hilos"]),
    ("async_await", "async/await", "async/await", "EC", "T_concurrencia", 5, ["funcion"], []),
    ("asyncio_mod", "asyncio", "asyncio", "ML", "T_concurrencia", 5, ["async_await"], []),
    ("corrutina", "Corrutina", "Coroutine", "PT", "T_concurrencia", 5, ["async_await", "generador"], []),
    ("notacion_o", "Notación O grande", "Big-O notation", "PT", "T_algoritmos", 4, ["complejidad"], []),
    ("busqueda_lineal", "Búsqueda lineal", "Linear search", "PT", "T_algoritmos", 2, ["bucle_for"], ["busqueda_binaria"]),
    ("ordenacion_burbuja", "Ordenación de burbuja", "Bubble sort", "PT", "T_algoritmos", 3, ["bucle_for"], []),
    ("ordenacion_mezcla", "Ordenación por mezcla", "Merge sort", "PT", "T_algoritmos", 5, ["recursion", "notacion_o"], []),
    ("ordenacion_rapida", "Ordenación rápida", "Quicksort", "PT", "T_algoritmos", 5, ["recursion"], []),
    ("sorted_f", "sorted() y sort()", "sorted/sort", "FI", "T_algoritmos", 2, ["lista"], []),
    ("prog_dinamica", "Programación dinámica", "Dynamic programming", "PT", "T_algoritmos", 5, ["memoizacion", "recursion"], []),
    ("backtracking", "Backtracking", "Backtracking", "PT", "T_algoritmos", 5, ["recursion"], []),
    ("grafo_estr", "Grafo (estructura)", "Graph", "ED", "T_algoritmos", 4, ["diccionario"], []),
    ("arbol_estr", "Árbol", "Tree", "ED", "T_algoritmos", 4, ["recursion"], []),
    ("bfs", "Recorrido en anchura (BFS)", "Breadth-first search", "PT", "T_algoritmos", 5, ["grafo_estr", "cola"], ["dfs"]),
    ("dfs", "Recorrido en profundidad (DFS)", "Depth-first search", "PT", "T_algoritmos", 5, ["grafo_estr", "recursion"], ["bfs"]),
    ("tabla_hash", "Tabla hash", "Hash table", "ED", "T_algoritmos", 4, ["diccionario"], []),
    ("docstring", "Docstring", "Docstring", "PT", "T_testing", 2, ["funcion"], []),
    ("pep8", "PEP 8 (estilo)", "PEP 8", "PT", "T_testing", 2, [], []),
    ("unittest_mod", "unittest", "unittest", "ML", "T_testing", 4, ["clase", "funcion"], []),
    ("pytest_mod", "pytest", "pytest", "ML", "T_testing", 4, ["funcion"], []),
    ("assert_stmt", "assert", "assert", "EC", "T_testing", 3, ["condicional"], []),
    ("type_checking", "Comprobación de tipos (mypy)", "Type checking", "PT", "T_testing", 4, ["anotaciones_tipo"], []),
]

# (id, es, en, concepto_afectado)
ERR = [
    ("err_decorador_wraps", "Decorador sin functools.wraps", "Decorator without wraps", "decorador"),
    ("err_generador_agotado", "Reutilizar un generador agotado", "Exhausted generator reuse", "generador"),
    ("err_late_binding", "Late binding en clausuras de bucle", "Loop closure late binding", "closure"),
    ("err_shallow_copy", "Copia superficial cuando se necesita profunda", "Shallow when deep needed", "copia_superficial"),
    ("err_mod_durante_iteracion", "Modificar una lista mientras se itera", "Mutating list while iterating", "bucle_for"),
    ("err_float_igualdad", "Comparar flotantes con ==", "Float equality comparison", "tipo_float"),
    ("err_self_olvidado", "Olvidar self en un método", "Missing self parameter", "metodo"),
    ("err_super_olvidado", "No llamar a super() en la subclase", "Missing super() call", "herencia"),
    ("err_gil_paralelismo", "Esperar paralelismo real con hilos (GIL)", "Expecting threads to parallelize", "gil"),
    ("err_except_generico", "Capturar Exception de forma demasiado amplia", "Overly broad except", "jerarquia_excepciones"),
    ("err_global_local", "Confundir variable global y local", "Global vs local confusion", "ambito"),
    ("err_concatenar_tipos", "Concatenar cadena y número (TypeError)", "Concatenating str and int", "conversion_tipos"),
]

NIVEL = {1: "basico", 2: "basico", 3: "intermedio", 4: "avanzado", 5: "avanzado"}


def main():
    g = Graph()
    g.parse(ONTO, format="turtle")
    antes = len(g)

    for tid, (es, en) in TEMAS.items():
        g.add((CFR[tid], RDF.type, CFKG.Tema))
        g.add((CFR[tid], RDFS.label, Literal(es, lang="es")))
        g.add((CFR[tid], RDFS.label, Literal(en, lang="en")))

    for cid, es, en, cat, tema, dif, prereqs, contrasts in C:
        iri = CFR[cid]
        g.add((iri, RDF.type, CFKG[CAT[cat]]))
        g.add((iri, RDFS.label, Literal(es, lang="es")))
        g.add((iri, RDFS.label, Literal(en, lang="en")))
        g.add((iri, CFKG.perteneceATema, CFR[tema]))
        g.add((iri, CFKG.tieneDificultad, Literal(dif, datatype=XSD.integer)))
        g.add((iri, CFKG.aNivelDominio, CFR[NIVEL[dif]]))
        for pr in prereqs:
            g.add((iri, CFKG.requierePrerrequisito, CFR[pr]))
        for ct in contrasts:
            g.add((iri, CFKG.contrastaCon, CFR[ct]))

    for eid, es, en, concepto in ERR:
        iri = CFR[eid]
        g.add((iri, RDF.type, CFKG.ErrorConceptual))
        g.add((iri, RDFS.label, Literal(es, lang="es")))
        g.add((iri, RDFS.label, Literal(en, lang="en")))
        g.add((iri, CFKG.errorSobreConcepto, CFR[concepto]))

    # ID-006 — enlaces a Wikidata con skos:exactMatch (NO owl:sameAs: evita la
    # fusión lógica de individuos que el razonador OWL-RL impondría con owl:sameAs).
    n_sameas = 0
    sa_path = BASE / "ontologia" / "wikidata_sameas.json"
    if sa_path.exists():
        for cid, info in json.loads(sa_path.read_text(encoding="utf-8")).items():
            g.add((CFR[cid], SKOS.exactMatch, URIRef("http://www.wikidata.org/entity/" + info["qid"])))
            n_sameas += 1

    # P11 — relación N-aria EvaluacionActividad (nodo intermedio) + propiedades
    g.add((CFKG.EvaluacionActividad, RDF.type, OWL.Class))
    g.add((CFKG.EvaluacionActividad, RDFS.subClassOf, CFKG.EntidadEducativa))
    g.add((CFKG.EvaluacionActividad, RDFS.label, Literal("Evaluación de actividad", lang="es")))
    g.add((CFKG.EvaluacionActividad, RDFS.label, Literal("Activity assessment", lang="en")))
    for p, dom, rng, es, en in [
        ("evaluaA", CFKG.EvaluacionActividad, CFKG.Ejercicio, "evalúa la actividad", "assesses activity"),
        ("porEstudiante", CFKG.EvaluacionActividad, CFKG.Estudiante, "realizada por", "carried out by"),
    ]:
        g.add((CFKG[p], RDF.type, OWL.ObjectProperty))
        g.add((CFKG[p], RDFS.domain, dom)); g.add((CFKG[p], RDFS.range, rng))
        g.add((CFKG[p], RDFS.label, Literal(es, lang="es"))); g.add((CFKG[p], RDFS.label, Literal(en, lang="en")))
    for p, rng, es, en in [("obtuvoNota", XSD.decimal, "obtuvo nota", "obtained grade"),
                           ("enFecha", XSD.date, "en la fecha", "on date")]:
        g.add((CFKG[p], RDF.type, OWL.DatatypeProperty))
        g.add((CFKG[p], RDFS.domain, CFKG.EvaluacionActividad)); g.add((CFKG[p], RDFS.range, rng))
        g.add((CFKG[p], RDFS.label, Literal(es, lang="es"))); g.add((CFKG[p], RDFS.label, Literal(en, lang="en")))

    estudiantes = ["est_alicia", "est_borja"]
    ejercicios = ["ej_suma_lista", "ej_factorial", "ej_busqueda"]
    notas = [8.5, 6.0, 9.0, 7.5, 5.5, 10.0, 6.5, 8.0, 7.0, 9.5]
    fechas = ["2026-03-02", "2026-03-09", "2026-03-16", "2026-03-23", "2026-03-30",
              "2026-04-06", "2026-04-13", "2026-04-20", "2026-04-27", "2026-05-04"]
    for i in range(10):
        ev = CFR[f"evalact_{i+1:02d}"]
        g.add((ev, RDF.type, CFKG.EvaluacionActividad))
        g.add((ev, RDFS.label, Literal(f"Evaluación de actividad {i+1:02d}", lang="es")))
        g.add((ev, RDFS.label, Literal(f"Activity assessment {i+1:02d}", lang="en")))
        g.add((ev, CFKG.porEstudiante, CFR[estudiantes[i % 2]]))
        g.add((ev, CFKG.evaluaA, CFR[ejercicios[i % 3]]))
        g.add((ev, CFKG.obtuvoNota, Literal(notas[i], datatype=XSD.decimal)))
        g.add((ev, CFKG.enFecha, Literal(fechas[i], datatype=XSD.date)))

    # ID-008 — normalización de etiquetas bilingües faltantes
    for cid, en in {"rec_doc_listas": "Official documentation: data structures",
                    "est_alicia": "Alice", "est_borja": "Borja",
                    "envio_001": "Submission 001", "envio_002": "Submission 002"}.items():
        g.add((CFR[cid], RDFS.label, Literal(en, lang="en")))
    for p, en in {"enEjercicio": "in exercise", "sobreConcepto": "about concept",
                  "relacionadoConceptualmenteCon": "conceptually related to"}.items():
        g.add((CFKG[p], RDFS.label, Literal(en, lang="en")))
    g.add((CFR["ref_keuning2019"], RDFS.label, Literal(
        "Keuning et al. (2019): revisión sistemática de generación automática de feedback", lang="es")))
    for cid, es, en in [("basico", "básico", "basic"), ("intermedio", "intermedio", "intermediate"),
                        ("avanzado", "avanzado", "advanced")]:
        g.add((CFR[cid], RDFS.label, Literal(es, lang="es")))
        g.add((CFR[cid], RDFS.label, Literal(en, lang="en")))
    g.add((CFR["eval_busqueda_bb"], RDFS.label, Literal("Evaluación de búsqueda binaria en ej_busqueda", lang="es")))
    g.add((CFR["eval_busqueda_bb"], RDFS.label, Literal("Binary-search assessment in ej_busqueda", lang="en")))
    g.add((CFR["stmt_offbyone"], RDFS.label, Literal("Procedencia (reificación): off-by-one sobre indexación según Keuning et al.", lang="es")))
    g.add((CFR["stmt_offbyone"], RDFS.label, Literal("Provenance (reification): off-by-one on indexing per Keuning et al.", lang="en")))

    # ID-007 — red SKOS skos:broader (específico -> general) entre conceptos existentes
    skos_broader = [
        ("comprension_listas", "bucle_for"),
        ("comprension_dicts", "comprension_listas"),
        ("comprension_sets", "comprension_listas"),
        ("expresion_generadora", "comprension_listas"),
        ("recursion_cola", "recursion"),
        ("ordenacion_burbuja", "notacion_o"),
        ("ordenacion_mezcla", "notacion_o"),
        ("ordenacion_rapida", "notacion_o"),
        ("bfs", "grafo_estr"),
        ("dfs", "grafo_estr"),
        ("slicing", "indexacion"),
        ("slicing_str", "slicing"),
        ("indexacion_negativa", "indexacion"),
        ("herencia_multiple", "herencia"),
        ("metodo_clase", "metodo"),
        ("metodo_estatico", "metodo"),
        ("init_method", "metodo"),
        ("pila", "lista"),
        ("cola", "lista"),
    ]
    for esp, gen in skos_broader:
        g.add((CFR[esp], SKOS.broader, CFR[gen]))
        g.add((CFR[gen], SKOS.narrower, CFR[esp]))

    # ID-091 — skos:related entre conceptos que se contrastan o relacionan lateralmente
    skos_related = [
        ("recursion", "bucle_for"),
        ("lista", "tupla"),
        ("conjunto", "lista"),
        ("herencia", "composicion"),
        ("pila", "cola"),
        ("hilos", "multiproceso"),
        ("bfs", "dfs"),
        ("busqueda_lineal", "busqueda_binaria"),
    ]
    for a, b in skos_related:
        g.add((CFR[a], SKOS.related, CFR[b]))
        g.add((CFR[b], SKOS.related, CFR[a]))

    g.bind("schema", SCHEMA, override=True, replace=True)
    g.bind("skos", SKOS, override=True, replace=True)
    g.serialize(destination=str(SALIDA), format="turtle", encoding="utf-8")
    print(f"Conceptos nuevos: {len(C)} | temas nuevos: {len(TEMAS)} | errores nuevos: {len(ERR)} | sameAs: {n_sameas} | EvaluacionActividad: 10")
    print(f"Triples: {antes} -> {len(g)} (+{len(g) - antes})")
    print(f"Escrito en: {SALIDA.name}")


if __name__ == "__main__":
    main()
