# -*- coding: utf-8 -*-
"""
construir_v2.py — Constructor reproducible y determinista del CodeFeedback-KG v2.0.

Carga la ontologia v2.0 de partida (codefeedback-kg.ttl), la fortalece de forma
ADITIVA siguiendo la metodologia LOT y el perfil OWL 2 RL:
  * completa dominio/rango en TODAS las propiedades,
  * anade clases, propiedades (objeto/datos), restricciones, disjunciones,
    inversas, transitivas y funcionales OWL 2 RL-safe,
  * anade >=56 conceptos nuevos de pedagogia Python (genuinos),
  * dota a TODO cfkg:Concepto de skos:definition + skos:scopeNote + skos:example,
  * alinea con Wikidata / DBpedia / schema.org / DCTerms (>=4 vocabularios),
  * verifica consistencia con cierre OWL-RL (sin owl:Nothing, sin owl:sameAs),
  * serializa de nuevo sobre codefeedback-kg.ttl (solo triples AFIRMADOS).

No borra nada de la v1.0. Antes de escribir hace copia *.bak-YYYYMMDD-HHMM.
"""
import sys
import shutil
from datetime import datetime
from pathlib import Path

from rdflib import Graph, Literal, URIRef, BNode, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD, SKOS, DCTERMS
import owlrl

BASE = Path(__file__).resolve().parent.parent
ONTO = BASE / "ontologia" / "codefeedback-kg.ttl"

CFKG = Namespace("https://w3id.org/codefeedback-kg/schema#")
CFR = Namespace("https://w3id.org/codefeedback-kg/id/")
WD = Namespace("http://www.wikidata.org/entity/")
DBR = Namespace("http://dbpedia.org/resource/")
SCHEMA = Namespace("http://schema.org/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

ES = "es"
EN = "en"


def L(txt, lang=ES):
    return Literal(txt, lang=lang)


#  1. CONTENIDO SKOS DE LOS 157 CONCEPTOS EXISTENTES
#     name -> (definicion_es, scopeNote_es, ejemplo_codigo)
C = {
"abrir_fichero": ("Funcion open() que abre un fichero y devuelve un objeto de fichero para leer o escribir.",
    "Usala siempre dentro de una sentencia with para garantizar el cierre del recurso y evitar fugas de descriptores.",
    "with open('datos.txt', 'r', encoding='utf-8') as f:\n    contenido = f.read()"),
"abstract_class": ("Clase base abstracta (ABC) que define una interfaz comun y no puede instanciarse directamente.",
    "Se declara heredando de abc.ABC y marcando metodos con @abstractmethod; obliga a las subclases a implementarlos.",
    "from abc import ABC, abstractmethod\nclass Figura(ABC):\n    @abstractmethod\n    def area(self): ..."),
"ambito": ("Region del programa donde un nombre de variable es visible y accesible (regla LEGB).",
    "Distingue ambito local, envolvente, global e incorporado; una asignacion crea una variable local salvo global/nonlocal.",
    "x = 1\ndef f():\n    x = 2  # variable local, no afecta a la global\n    return x"),
"anotaciones_tipo": ("Indicaciones opcionales del tipo esperado de variables, parametros y valores de retorno (type hints).",
    "No las comprueba el interprete en tiempo de ejecucion; las usan herramientas como mypy y los editores.",
    "def saluda(nombre: str) -> str:\n    return f'Hola {nombre}'"),
"arbol_estr": ("Estructura de datos jerarquica formada por nodos con un nodo raiz y subarboles hijos.",
    "Es la base de arboles binarios, de busqueda y montículos; se recorre habitualmente de forma recursiva.",
    "nodo = {'valor': 1, 'hijos': [{'valor': 2, 'hijos': []}]}"),
"args_kwargs": ("Sintaxis *args y **kwargs para aceptar un numero variable de argumentos posicionales y por nombre.",
    "*args agrupa posicionales en una tupla y **kwargs los nombrados en un diccionario.",
    "def f(*args, **kwargs):\n    print(args, kwargs)\nf(1, 2, a=3)"),
"argumentos_nombrados": ("Argumentos que se pasan a una funcion indicando el nombre del parametro (clave=valor).",
    "Mejoran la legibilidad y permiten omitir el orden; deben ir despues de los posicionales.",
    "def conecta(host, puerto=80):\n    ...\nconecta('localhost', puerto=8080)"),
"asignacion": ("Operacion que vincula un nombre a un objeto en memoria mediante el operador =.",
    "En Python la asignacion no copia el objeto: asocia una referencia; varios nombres pueden apuntar al mismo objeto.",
    "x = [1, 2, 3]\ny = x  # y referencia la misma lista"),
"assert_stmt": ("Sentencia assert que verifica una condicion y lanza AssertionError si es falsa.",
    "Util para comprobaciones internas y pruebas; se desactiva al ejecutar Python con la opcion -O.",
    "def media(xs):\n    assert len(xs) > 0, 'lista vacia'\n    return sum(xs) / len(xs)"),
"async_await": ("Sintaxis async/await para definir y suspender corrutinas en programacion asincrona.",
    "await solo puede usarse dentro de una funcion async def; cede el control al bucle de eventos sin bloquear el hilo.",
    "import asyncio\nasync def main():\n    await asyncio.sleep(1)\n    print('listo')"),
"asyncio_mod": ("Modulo estandar asyncio para escribir codigo concurrente con corrutinas y un bucle de eventos.",
    "Adecuado para E/S concurrente (red, ficheros); no acelera calculo intensivo de CPU.",
    "import asyncio\nasync def tarea():\n    return 42\nasyncio.run(tarea())"),
"atributo": ("Variable asociada a una instancia que almacena parte de su estado.",
    "Se define normalmente en __init__ usando self; no confundir con atributos de clase compartidos.",
    "class Punto:\n    def __init__(self, x):\n        self.x = x  # atributo de instancia"),
"backtracking": ("Tecnica algoritmica que construye soluciones de forma incremental y retrocede al detectar un callejon sin salida.",
    "Tipica en problemas de combinatoria (N reinas, sudoku); se implementa con recursion y poda.",
    "def resolver(estado):\n    if completo(estado):\n        return estado\n    for mov in movimientos(estado):\n        if valido(mov):\n            r = resolver(aplicar(estado, mov))\n            if r:\n                return r\n    return None"),
"bfs": ("Recorrido en anchura de un grafo que visita los nodos por niveles desde el origen usando una cola.",
    "Encuentra el camino mas corto en grafos no ponderados; contrasta con DFS que usa pila/recursion.",
    "from collections import deque\ndef bfs(g, inicio):\n    visto, cola = {inicio}, deque([inicio])\n    while cola:\n        n = cola.popleft()\n        for v in g[n]:\n            if v not in visto:\n                visto.add(v); cola.append(v)"),
"break_continue": ("Sentencias break (sale del bucle) y continue (salta a la siguiente iteracion).",
    "Afectan solo al bucle mas interno; un uso excesivo puede dificultar la lectura del codigo.",
    "for n in range(10):\n    if n == 5:\n        break\n    if n % 2 == 0:\n        continue\n    print(n)"),
"bucle_for": ("Bucle que itera sobre los elementos de un iterable ejecutando un bloque por cada uno.",
    "Es el bucle idiomatico en Python; con range() permite repetir un numero fijo de veces.",
    "for x in [1, 2, 3]:\n    print(x)"),
"bucle_while": ("Bucle que repite un bloque mientras una condicion sea verdadera.",
    "Adecuado cuando no se conoce de antemano el numero de iteraciones; cuida la condicion de parada para evitar bucles infinitos.",
    "i = 0\nwhile i < 3:\n    print(i)\n    i += 1"),
"busqueda_binaria": ("Algoritmo que localiza un elemento en una lista ordenada dividiendo a la mitad el espacio de busqueda.",
    "Requiere que la secuencia este ordenada; su coste es O(log n) frente a O(n) de la busqueda lineal.",
    "def binaria(xs, x):\n    lo, hi = 0, len(xs) - 1\n    while lo <= hi:\n        m = (lo + hi) // 2\n        if xs[m] == x: return m\n        if xs[m] < x: lo = m + 1\n        else: hi = m - 1\n    return -1"),
"busqueda_lineal": ("Algoritmo que recorre una secuencia elemento a elemento hasta encontrar el buscado.",
    "Simple y sin requisitos de orden, pero ineficiente (O(n)) para colecciones grandes.",
    "def lineal(xs, x):\n    for i, v in enumerate(xs):\n        if v == x:\n            return i\n    return -1"),
"clase": ("Plantilla que define atributos y metodos para crear objetos de un mismo tipo.",
    "Convencion: el nombre va en CamelCase; instanciar la clase llama a __init__.",
    "class Coche:\n    def __init__(self, marca):\n        self.marca = marca"),
"closure": ("Funcion interna que recuerda y captura variables del ambito envolvente donde fue creada.",
    "Permite fabricas de funciones; las variables capturadas se evaluan en el momento de la llamada (cuidado con el late binding).",
    "def multiplicador(n):\n    def f(x):\n        return x * n\n    return f\ndoble = multiplicador(2)"),
"cola": ("Estructura FIFO (primero en entrar, primero en salir) que anade por un extremo y extrae por el otro.",
    "Usa collections.deque para operaciones O(1) en ambos extremos en lugar de list.pop(0).",
    "from collections import deque\nq = deque()\nq.append(1); q.popleft()"),
"collections_mod": ("Modulo collections con tipos de contenedor especializados (deque, Counter, defaultdict, namedtuple).",
    "Ofrece alternativas mas eficientes o expresivas que las estructuras integradas para casos concretos.",
    "from collections import Counter\nCounter('aabbbc')  # Counter({'b': 3, 'a': 2, 'c': 1})"),
"complejidad": ("Estimacion del crecimiento del tiempo o memoria de un algoritmo segun el tamano de la entrada.",
    "Se expresa con notacion O grande; guia la eleccion de algoritmos y estructuras de datos.",
    "# Recorrer una lista es O(n)\nfor x in xs:\n    procesar(x)"),
"composicion": ("Diseno en el que un objeto contiene instancias de otras clases para reutilizar su comportamiento.",
    "Suele preferirse a la herencia ('composicion sobre herencia') por su menor acoplamiento.",
    "class Motor: ...\nclass Coche:\n    def __init__(self):\n        self.motor = Motor()  # composicion"),
"comprension_dicts": ("Sintaxis concisa para construir diccionarios a partir de un iterable en una sola expresion.",
    "Sigue el patron {clave: valor for ...}; mas legible que un bucle con asignaciones cuando es simple.",
    "cuadrados = {n: n*n for n in range(5)}"),
"comprension_listas": ("Sintaxis concisa para construir listas a partir de un iterable, con filtros opcionales.",
    "Mas legible y rapida que un bucle con append para transformaciones simples; evita anidar demasiado.",
    "ys = [x*x for x in range(10) if x % 2 == 0]"),
"comprension_sets": ("Sintaxis concisa para construir conjuntos eliminando duplicados a partir de un iterable.",
    "Sigue el patron {expr for ...}; util para obtener elementos unicos transformados.",
    "iniciales = {p[0] for p in ['ana', 'alba', 'bea']}"),
"condicional": ("Sentencia if/elif/else que ejecuta bloques distintos segun condiciones booleanas.",
    "La sangria delimita el bloque; las condiciones se evaluan en orden hasta la primera verdadera.",
    "if x > 0:\n    print('positivo')\nelif x == 0:\n    print('cero')\nelse:\n    print('negativo')"),
"conjunto": ("Coleccion no ordenada de elementos unicos e inmutables (set).",
    "Ofrece pertenencia y operaciones de conjunto (union, interseccion) en tiempo medio O(1); no admite duplicados.",
    "s = {1, 2, 2, 3}  # {1, 2, 3}\n2 in s  # True"),
"context_manager": ("Objeto que define la entrada (__enter__) y salida (__exit__) de un bloque with para gestionar recursos.",
    "Garantiza la liberacion del recurso incluso si ocurre una excepcion; contextlib facilita crearlos.",
    "class Recurso:\n    def __enter__(self): return self\n    def __exit__(self, *a): print('cerrado')"),
"conversion_tipos": ("Cambio explicito del tipo de un valor mediante constructores como int(), str() o float().",
    "Evita errores de TypeError al combinar tipos incompatibles; puede lanzar ValueError si el formato no es valido.",
    "edad = int('42')\ntexto = str(3.14)"),
"copia_profunda": ("Copia que duplica recursivamente un objeto y todos los objetos anidados que contiene.",
    "Usa copy.deepcopy cuando modificar la copia no debe afectar al original anidado; es mas costosa que la superficial.",
    "import copy\nb = copy.deepcopy(a)"),
"copia_superficial": ("Copia que duplica el contenedor externo pero comparte las referencias a los objetos internos.",
    "list(x), x[:] o copy.copy crean copias superficiales; modificar elementos anidados afecta a ambas copias.",
    "import copy\nb = copy.copy(a)  # superficial"),
"corrutina": ("Funcion que puede suspender y reanudar su ejecucion, cooperando con un planificador.",
    "En Python moderno se definen con async def; las clasicas usaban generadores con yield.",
    "async def contador():\n    for i in range(3):\n        await asyncio.sleep(0)\n        yield i"),
"counter": ("Subclase de diccionario (collections.Counter) que cuenta apariciones de elementos hashables.",
    "Ofrece most_common() y aritmetica de multiconjuntos; ideal para frecuencias.",
    "from collections import Counter\nc = Counter('banana')\nc.most_common(1)  # [('a', 3)]"),
"csv_mod": ("Modulo estandar csv para leer y escribir ficheros de valores separados por comas.",
    "Maneja correctamente comillas y delimitadores; usa newline='' al abrir el fichero.",
    "import csv\nwith open('d.csv', newline='') as f:\n    for fila in csv.reader(f):\n        print(fila)"),
"dataclass": ("Decorador @dataclass que genera automaticamente __init__, __repr__ y __eq__ a partir de anotaciones.",
    "Reduce el codigo repetitivo de las clases que solo almacenan datos; admite valores por defecto y campos.",
    "from dataclasses import dataclass\n@dataclass\nclass Punto:\n    x: int\n    y: int = 0"),
"decorador": ("Funcion que envuelve a otra para anadir comportamiento sin modificar su codigo, aplicada con @.",
    "Conserva metadatos con functools.wraps; util para logging, cache, control de acceso o tiempos.",
    "def log(f):\n    def envoltura(*a, **k):\n        print('llamando', f.__name__)\n        return f(*a, **k)\n    return envoltura"),
"defaultdict": ("Diccionario (collections.defaultdict) que crea un valor por defecto al acceder a una clave inexistente.",
    "Evita comprobar la existencia de la clave; se inicializa con una fabrica (list, int, set).",
    "from collections import defaultdict\nd = defaultdict(list)\nd['a'].append(1)"),
"deque": ("Cola doblemente terminada (collections.deque) con insercion y extraccion O(1) por ambos extremos.",
    "Preferible a list para colas y pilas; permite limitar su tamano con maxlen.",
    "from collections import deque\nd = deque([1, 2])\nd.appendleft(0); d.pop()"),
"desempaquetado": ("Asignacion simultanea de los elementos de un iterable a varias variables.",
    "Admite el comodin * para capturar el resto; util para intercambios y retorno multiple.",
    "a, b, *resto = [1, 2, 3, 4]"),
"dfs": ("Recorrido en profundidad de un grafo que explora un camino al maximo antes de retroceder.",
    "Se implementa con recursion o pila explicita; util para deteccion de ciclos y ordenacion topologica.",
    "def dfs(g, n, visto=None):\n    visto = visto or set()\n    visto.add(n)\n    for v in g[n]:\n        if v not in visto:\n            dfs(g, v, visto)"),
"diccionario": ("Coleccion de pares clave-valor con acceso por clave en tiempo medio O(1).",
    "Las claves deben ser hashables; desde Python 3.7 conserva el orden de insercion.",
    "d = {'a': 1, 'b': 2}\nd['a']  # 1"),
"docstring": ("Cadena de documentacion situada al inicio de un modulo, clase o funcion.",
    "Accesible mediante help() y __doc__; conviene seguir convenciones como PEP 257.",
    "def suma(a, b):\n    \"\"\"Devuelve la suma de a y b.\"\"\"\n    return a + b"),
"dunder": ("Metodos especiales con doble guion bajo (__init__, __len__, __eq__) que integran objetos con el lenguaje.",
    "Permiten personalizar operadores, iteracion o representacion; tambien llamados metodos magicos.",
    "class Vec:\n    def __init__(self, n): self.n = n\n    def __add__(self, o): return Vec(self.n + o.n)"),
"else_bucle": ("Clausula else de un bucle que se ejecuta solo si el bucle termina sin break.",
    "Util para detectar si una busqueda no encontro el elemento; suele confundir a los principiantes.",
    "for x in xs:\n    if x == objetivo:\n        break\nelse:\n    print('no encontrado')"),
"encadenar_excepciones": ("Mecanismo (raise ... from ...) que vincula una excepcion con la causa original.",
    "Preserva la traza completa y aclara el origen del error; from None oculta la causa intencionadamente.",
    "try:\n    int('x')\nexcept ValueError as e:\n    raise RuntimeError('dato invalido') from e"),
"encapsulacion": ("Principio de ocultar el estado interno de un objeto exponiendo solo una interfaz controlada.",
    "Python usa convenciones (_protegido, __privado con name mangling) en lugar de modificadores estrictos.",
    "class Cuenta:\n    def __init__(self):\n        self.__saldo = 0  # 'privado'"),
"encoding": ("Esquema que asocia caracteres a secuencias de bytes (UTF-8, Latin-1) al codificar texto.",
    "Especifica siempre encoding al abrir ficheros de texto; errores de codificacion causan UnicodeDecodeError.",
    "datos = 'cana'.encode('utf-8')\ntexto = datos.decode('utf-8')"),
"entorno_virtual": ("Entorno aislado (venv) con su propio interprete y dependencias para un proyecto.",
    "Evita conflictos de versiones entre proyectos; se activa antes de instalar paquetes con pip.",
    "python -m venv .venv\nsource .venv/bin/activate"),
"enum_tipo": ("Tipo enumerado (enum.Enum) que define un conjunto de constantes simbolicas con nombre.",
    "Mejora la legibilidad frente a constantes sueltas; los miembros son unicos y comparables por identidad.",
    "from enum import Enum\nclass Color(Enum):\n    ROJO = 1\n    VERDE = 2"),
"enumerate_f": ("Funcion enumerate() que produce pares (indice, elemento) al iterar un iterable.",
    "Evita gestionar manualmente un contador; admite un indice inicial con start.",
    "for i, v in enumerate(['a', 'b'], start=1):\n    print(i, v)"),
"escribir_fichero": ("Escritura de datos en un fichero mediante metodos como write() o writelines().",
    "Abre en modo 'w' (sobrescribe) o 'a' (anade); usa with para cerrar y volcar el buffer.",
    "with open('s.txt', 'w', encoding='utf-8') as f:\n    f.write('hola')"),
"excepcion": ("Evento que interrumpe el flujo normal del programa para senalar un error o situacion especial.",
    "Se captura con try/except; en Python se prefiere pedir perdon (EAFP) a comprobar antes (LBYL).",
    "try:\n    1 / 0\nexcept ZeroDivisionError:\n    print('division por cero')"),
"excepcion_personalizada": ("Clase de excepcion propia que hereda de Exception para representar errores del dominio.",
    "Permite capturar selectivamente y anadir contexto; nombra la clase terminando en Error por convencion.",
    "class SaldoInsuficienteError(Exception):\n    pass"),
"expresion_generadora": ("Expresion perezosa, similar a una comprension, que produce valores bajo demanda con parentesis.",
    "Ahorra memoria frente a una lista cuando solo se itera una vez; no se puede indexar.",
    "suma = sum(x*x for x in range(1000))"),
"filter_func": ("Funcion filter() que selecciona los elementos de un iterable que cumplen un predicado.",
    "Devuelve un iterador perezoso; a menudo una comprension con if resulta mas legible.",
    "pares = list(filter(lambda x: x % 2 == 0, range(10)))"),
"formato_str": ("Conjunto de tecnicas para insertar valores en cadenas (f-strings, str.format, %).",
    "Las f-strings son la opcion recomendada por su claridad y rendimiento desde Python 3.6.",
    "n = 3\nf'hay {n} elementos'"),
"from_import": ("Variante del import que trae nombres concretos de un modulo al espacio de nombres actual.",
    "Evita el prefijo del modulo pero puede provocar colisiones; no abuses de from modulo import *.",
    "from math import sqrt\nsqrt(16)"),
"fstring": ("Cadena literal con prefijo f que permite interpolar expresiones entre llaves.",
    "Disponible desde Python 3.6; admite formato y, desde 3.8, la sintaxis de depuracion {x=}.",
    "nombre = 'Ana'\nf'Hola {nombre}, {2+2=}'"),
"funcion": ("Bloque de codigo reutilizable con nombre que recibe parametros y puede devolver un valor.",
    "Se define con def; favorece la modularidad y evita la repeticion de codigo.",
    "def cuadrado(x):\n    return x * x"),
"funcion_lambda": ("Funcion anonima de una sola expresion definida con la palabra clave lambda.",
    "Util como argumento breve (key de sorted); si crece, mejor una funcion con def.",
    "ordenar = sorted(pares, key=lambda p: p[1])"),
"funcion_orden_superior": ("Funcion que recibe otras funciones como argumento o devuelve una funcion.",
    "Base de map, filter y los decoradores; aprovecha que las funciones son objetos de primera clase.",
    "def aplica(f, x):\n    return f(x)\naplica(abs, -5)"),
"functools_wraps": ("Decorador functools.wraps que copia los metadatos de la funcion original a la envoltura.",
    "Conserva __name__ y __doc__ al crear decoradores; sin el se pierde la introspeccion.",
    "import functools\ndef d(f):\n    @functools.wraps(f)\n    def w(*a, **k): return f(*a, **k)\n    return w"),
"generador": ("Funcion que produce una secuencia de valores de forma perezosa usando yield.",
    "Mantiene su estado entre llamadas y ahorra memoria; se agota tras recorrerse una vez.",
    "def cuenta(n):\n    i = 0\n    while i < n:\n        yield i\n        i += 1"),
"gil": ("Bloqueo global del interprete (GIL) de CPython que permite ejecutar un solo hilo de bytecode a la vez.",
    "Limita el paralelismo real con hilos en tareas de CPU; usa multiprocessing para calculo intensivo.",
    "# Los hilos no aceleran calculo puro de CPU por el GIL\nimport threading"),
"grafo_estr": ("Estructura de datos formada por nodos (vertices) y conexiones (aristas) entre ellos.",
    "Se representa habitualmente con listas o diccionarios de adyacencia; base de BFS y DFS.",
    "g = {'a': ['b', 'c'], 'b': ['c'], 'c': []}"),
"heap": ("Arbol binario parcialmente ordenado que da acceso O(1) al minimo o maximo (modulo heapq).",
    "heapq implementa un min-heap sobre una lista; util para colas de prioridad y los k mayores.",
    "import heapq\nh = [3, 1, 2]\nheapq.heapify(h)\nheapq.heappop(h)  # 1"),
"herencia": ("Mecanismo por el que una clase deriva atributos y metodos de otra clase base.",
    "Modela relaciones 'es-un'; usa super() para extender el comportamiento heredado sin duplicarlo.",
    "class Animal:\n    def hablar(self): ...\nclass Perro(Animal):\n    def hablar(self): return 'guau'"),
"herencia_multiple": ("Capacidad de una clase de heredar de varias clases base a la vez.",
    "Util con mixins; el orden de resolucion de metodos (MRO) determina que implementacion se usa.",
    "class A: ...\nclass B: ...\nclass C(A, B): ..."),
"hilos": ("Hilos de ejecucion (threading) que comparten memoria dentro de un mismo proceso.",
    "Adecuados para E/S concurrente; por el GIL no paralelizan calculo de CPU. Cuidado con las condiciones de carrera.",
    "import threading\nt = threading.Thread(target=tarea)\nt.start(); t.join()"),
"identidad_objetos": ("Comprobacion (is) de si dos nombres referencian exactamente el mismo objeto en memoria.",
    "is compara identidad y == compara valor; reserva is para None y centinelas.",
    "a = [1]\nb = a\na is b  # True\na is [1]  # False"),
"import_mod": ("Sentencia import que carga un modulo y lo pone a disposicion del programa.",
    "El interprete cachea los modulos importados; situa los imports al inicio del fichero (PEP 8).",
    "import math\nmath.pi"),
"indexacion": ("Acceso a un elemento de una secuencia mediante su posicion entre corchetes.",
    "Los indices empiezan en 0; acceder fuera de rango lanza IndexError.",
    "xs = [10, 20, 30]\nxs[0]  # 10"),
"indexacion_negativa": ("Acceso a elementos contando desde el final con indices negativos (-1 es el ultimo).",
    "Evita calcular len(x)-1; tambien aplica al slicing.",
    "xs = [1, 2, 3]\nxs[-1]  # 3"),
"init_method": ("Metodo especial __init__ que inicializa el estado de una instancia recien creada.",
    "Recibe self y los argumentos del constructor; no devuelve valor (debe retornar None).",
    "class Punto:\n    def __init__(self, x, y):\n        self.x, self.y = x, y"),
"iterables": ("Objetos que pueden recorrerse en un bucle for porque producen un iterador (listas, cadenas, dicts).",
    "Implementan __iter__; distingue iterable (se puede recorrer) de iterador (mantiene la posicion).",
    "for c in 'abc':\n    print(c)"),
"iterador": ("Objeto que produce los elementos de un iterable de uno en uno mediante next().",
    "Implementa __iter__ y __next__; lanza StopIteration al agotarse.",
    "it = iter([1, 2])\nnext(it)  # 1"),
"itertools_mod": ("Modulo itertools con utilidades para construir iteradores eficientes y combinatorios.",
    "Incluye count, cycle, chain, product o combinations; opera de forma perezosa.",
    "import itertools\nlist(itertools.islice(itertools.count(), 3))  # [0, 1, 2]"),
"jerarquia_excepciones": ("Arbol de clases de excepcion donde las mas especificas heredan de las generales.",
    "Captura primero las especificas; except Exception captura casi todo y puede ocultar errores.",
    "try:\n    ...\nexcept FileNotFoundError:\n    ...\nexcept OSError:\n    ..."),
"json_mod": ("Modulo json para serializar objetos Python a texto JSON y deserializarlos.",
    "dumps/loads trabajan con cadenas; dump/load con ficheros. No todos los tipos son serializables.",
    "import json\njson.dumps({'a': 1})  # '{\"a\": 1}'"),
"leer_fichero": ("Lectura del contenido de un fichero con metodos como read(), readline() o iterando lineas.",
    "Iterar el objeto de fichero linea a linea es eficiente en memoria para ficheros grandes.",
    "with open('d.txt', encoding='utf-8') as f:\n    for linea in f:\n        print(linea.rstrip())"),
"lista": ("Secuencia mutable y ordenada que admite elementos de cualquier tipo.",
    "Crece dinamicamente; el acceso por indice es O(1) y la insercion al final amortizada O(1).",
    "xs = [1, 'a', True]\nxs.append(2)"),
"map_func": ("Funcion map() que aplica una funcion a cada elemento de uno o varios iterables.",
    "Devuelve un iterador perezoso; una comprension suele ser mas legible.",
    "dobles = list(map(lambda x: x*2, [1, 2, 3]))"),
"match_case": ("Coincidencia estructural de patrones (match/case) que compara un valor con varias formas.",
    "Disponible desde Python 3.10; permite desestructurar y usar guardas, mas potente que una cadena de if.",
    "match punto:\n    case (0, 0):\n        print('origen')\n    case (x, y):\n        print(x, y)"),
"memoizacion": ("Tecnica que almacena en cache los resultados de una funcion para reutilizarlos.",
    "functools.lru_cache la implementa con un decorador; acelera funciones puras y recursivas.",
    "import functools\n@functools.lru_cache\ndef fib(n):\n    return n if n < 2 else fib(n-1) + fib(n-2)"),
"metodo": ("Funcion definida dentro de una clase que opera sobre sus instancias.",
    "Recibe la instancia como primer parametro (self); se invoca con la notacion objeto.metodo().",
    "class Saludo:\n    def hola(self):\n        return 'hola'"),
"metodo_clase": ("Metodo (@classmethod) que recibe la clase (cls) en lugar de la instancia.",
    "Util para constructores alternativos (fabricas) que devuelven instancias configuradas.",
    "class Fecha:\n    @classmethod\n    def hoy(cls):\n        return cls()"),
"metodo_estatico": ("Metodo (@staticmethod) que no recibe ni instancia ni clase, agrupado por afinidad logica.",
    "Se comporta como una funcion normal dentro del espacio de nombres de la clase.",
    "class Mat:\n    @staticmethod\n    def suma(a, b):\n        return a + b"),
"metodos_str": ("Conjunto de metodos del tipo str para manipular texto (upper, strip, replace, find).",
    "Las cadenas son inmutables: estos metodos devuelven una cadena nueva, no modifican la original.",
    "'  Hola  '.strip().lower()  # 'hola'"),
"mixin": ("Clase pequena que aporta funcionalidad concreta para combinarse por herencia multiple.",
    "No se instancia por si sola; anade un comportamiento transversal a varias clases.",
    "class SerializableMixin:\n    def to_dict(self):\n        return self.__dict__"),
"modulo_datetime": ("Modulo datetime para representar y operar con fechas, horas y duraciones.",
    "Distingue objetos 'naive' y 'aware' (con zona horaria); usa timedelta para aritmetica.",
    "from datetime import date\ndate.today().isoformat()"),
"modulo_math": ("Modulo math con funciones y constantes matematicas para numeros reales.",
    "Incluye sqrt, sin, factorial, pi y e; para vectores grandes considera numpy.",
    "import math\nmath.sqrt(2)"),
"modulo_os": ("Modulo os con utilidades para interactuar con el sistema operativo y los ficheros.",
    "Para rutas, os.path o, preferiblemente, pathlib; os.environ accede a las variables de entorno.",
    "import os\nos.getcwd()"),
"modulo_random": ("Modulo random para generar numeros pseudoaleatorios y muestreos.",
    "No es criptograficamente seguro; usa el modulo secrets para contrasenas o tokens.",
    "import random\nrandom.randint(1, 6)"),
"modulo_sys": ("Modulo sys con acceso a parametros y funciones del interprete (argv, path, exit).",
    "sys.argv recibe los argumentos de linea de comandos; sys.exit termina el programa.",
    "import sys\nprint(sys.argv)"),
"mro": ("Orden de resolucion de metodos (MRO) que determina como Python busca atributos en herencia multiple.",
    "Se calcula con el algoritmo C3 y es consultable con NombreClase.mro().",
    "class C(A, B): ...\nC.mro()"),
"multiproceso": ("Ejecucion paralela mediante varios procesos (multiprocessing) con memoria independiente.",
    "Esquiva el GIL y aprovecha varios nucleos para calculo de CPU; comunicar procesos tiene coste.",
    "from multiprocessing import Pool\nwith Pool() as p:\n    p.map(cuadrado, range(10))"),
"mutabilidad": ("Propiedad de los objetos cuyo estado puede modificarse tras su creacion.",
    "Listas, dicts y sets son mutables; numeros, cadenas y tuplas son inmutables. Afecta a alias y copias.",
    "xs = [1]\nxs.append(2)  # mutado en sitio"),
"mutable_inmutable": ("Distincion entre objetos modificables (mutables) y no modificables (inmutables).",
    "Los inmutables son hashables y seguros como claves; evita usar mutables como valores por defecto.",
    "t = (1, 2)   # inmutable\nl = [1, 2]   # mutable"),
"namedtuple": ("Tupla con campos nombrados (collections.namedtuple) accesibles por atributo.",
    "Ligera e inmutable; mejora la legibilidad frente a tuplas posicionales. Para datos mutables usa dataclass.",
    "from collections import namedtuple\nPunto = namedtuple('Punto', 'x y')\nPunto(1, 2).x"),
"notacion_o": ("Notacion O grande que describe el crecimiento asintotico del coste de un algoritmo.",
    "Ignora constantes y terminos menores; O(1) < O(log n) < O(n) < O(n log n) < O(n^2).",
    "# Busqueda binaria: O(log n)\n# Ordenacion por mezcla: O(n log n)"),
"objeto": ("Instancia concreta de una clase con su propio estado y comportamiento.",
    "Todo en Python es un objeto; se crea llamando a la clase y vive mientras haya referencias a el.",
    "p = Punto(1, 2)  # p es un objeto"),
"operador_estrella": ("Operadores * y ** para empaquetar y desempaquetar argumentos e iterables.",
    "* expande secuencias y ** diccionarios; permiten reenviar argumentos entre funciones.",
    "def f(a, b, c): ...\nargs = [1, 2, 3]\nf(*args)"),
"ordenacion_burbuja": ("Algoritmo de ordenacion que intercambia repetidamente elementos adyacentes desordenados.",
    "Didactico pero ineficiente (O(n^2)); en la practica usa sorted() (Timsort).",
    "def burbuja(xs):\n    for i in range(len(xs)):\n        for j in range(len(xs)-1-i):\n            if xs[j] > xs[j+1]:\n                xs[j], xs[j+1] = xs[j+1], xs[j]"),
"ordenacion_mezcla": ("Algoritmo de ordenacion por division y conquista que fusiona sublistas ordenadas.",
    "Estable y O(n log n) en el peor caso, pero usa memoria adicional O(n).",
    "def mezcla(xs):\n    if len(xs) <= 1: return xs\n    m = len(xs)//2\n    return fusion(mezcla(xs[:m]), mezcla(xs[m:]))"),
"ordenacion_rapida": ("Algoritmo de ordenacion por division y conquista que particiona en torno a un pivote.",
    "O(n log n) en promedio y O(n^2) en el peor caso; la eleccion del pivote es clave.",
    "def rapida(xs):\n    if len(xs) <= 1: return xs\n    p = xs[0]\n    return rapida([x for x in xs[1:] if x < p]) + [p] + rapida([x for x in xs[1:] if x >= p])"),
"paquete": ("Directorio que agrupa modulos relacionados y se importa como una unidad.",
    "Tradicionalmente contiene __init__.py; permite organizar proyectos en jerarquias de espacios de nombres.",
    "from paquete.subpaquete import modulo"),
"parametros": ("Variables declaradas en la definicion de una funcion que reciben los argumentos al llamarla.",
    "Distingue parametro (en la definicion) de argumento (en la llamada); admiten valores por defecto.",
    "def f(a, b=0):  # a y b son parametros\n    return a + b"),
"partial": ("Funcion functools.partial que fija algunos argumentos de otra y devuelve una nueva.",
    "Util para especializar funciones genericas y pasarlas como callbacks.",
    "from functools import partial\ncubo = partial(pow, exp=3)"),
"pathlib": ("Modulo pathlib con una API orientada a objetos para rutas del sistema de ficheros.",
    "Sustituye a os.path con codigo mas legible y portable; el operador / compone rutas.",
    "from pathlib import Path\np = Path('datos') / 'fichero.txt'\np.exists()"),
"pila": ("Estructura LIFO (ultimo en entrar, primero en salir) que apila y desapila por un mismo extremo.",
    "Una lista funciona como pila con append y pop; base de la recursion, el deshacer y la evaluacion de expresiones.",
    "pila = []\npila.append(1)\npila.pop()  # 1"),
"pep8": ("Guia de estilo oficial PEP 8 con convenciones de formato del codigo Python.",
    "Recomienda sangria de 4 espacios, snake_case y lineas de hasta 79 caracteres; herramientas como flake8 la verifican.",
    "# correcto\ndef calcular_total(precio, cantidad):\n    return precio * cantidad"),
"pip_mod": ("Gestor de paquetes pip para instalar bibliotecas desde el indice PyPI.",
    "Trabaja con requirements.txt e idealmente dentro de un entorno virtual.",
    "pip install requests\npip freeze > requirements.txt"),
"polimorfismo": ("Capacidad de tratar de forma uniforme objetos de distintas clases que comparten interfaz.",
    "Python lo logra por duck typing: importa el comportamiento, no el tipo exacto.",
    "for a in animales:\n    print(a.hablar())  # cada clase implementa hablar"),
"prog_dinamica": ("Tecnica que resuelve un problema combinando soluciones de subproblemas solapados, guardandolas.",
    "Combina recursion con memoizacion o tablas; evita recalcular (p. ej. Fibonacci, mochila).",
    "def fib(n, memo={}):\n    if n < 2: return n\n    if n not in memo:\n        memo[n] = fib(n-1) + fib(n-2)\n    return memo[n]"),
"propiedad": ("Atributo gestionado (@property) que ejecuta metodos al leer o escribir un valor.",
    "Permite anadir validacion o calculo sin cambiar la interfaz publica del atributo.",
    "class C:\n    @property\n    def area(self):\n        return self.lado ** 2"),
"pytest_mod": ("Marco de pruebas pytest que descubre y ejecuta tests con asserts simples.",
    "Ofrece fixtures, parametrizacion y mensajes de fallo detallados; estandar de facto en Python.",
    "def test_suma():\n    assert 1 + 1 == 2"),
"python": ("Lenguaje de programacion interpretado, de alto nivel y tipado dinamico, con enfasis en la legibilidad.",
    "Multiparadigma (imperativo, orientado a objetos y funcional); su filosofia se resume en el Zen de Python.",
    "print('Hola, mundo')"),
"raise_excepcion": ("Sentencia raise que lanza una excepcion de forma explicita.",
    "Permite senalar errores del dominio; puede relanzar la actual con raise a secas dentro de un except.",
    "if x < 0:\n    raise ValueError('x debe ser positivo')"),
"range_f": ("Funcion range() que genera una secuencia perezosa de enteros equiespaciados.",
    "Define inicio, fin (excluido) y paso; no crea una lista, ahorra memoria.",
    "list(range(2, 10, 2))  # [2, 4, 6, 8]"),
"recursion": ("Tecnica en la que una funcion se define en terminos de si misma sobre un problema menor.",
    "Necesita un caso base que detenga la recursion; cuidado con el limite de profundidad de la pila.",
    "def fact(n):\n    return 1 if n == 0 else n * fact(n - 1)"),
"recursion_cola": ("Recursion en la que la llamada recursiva es la ultima operacion de la funcion.",
    "Otros lenguajes la optimizan, pero CPython no elimina la recursion de cola: puede desbordar la pila.",
    "def suma(xs, acc=0):\n    if not xs: return acc\n    return suma(xs[1:], acc + xs[0])"),
"reduce_func": ("Funcion functools.reduce que combina los elementos de un iterable en un unico valor.",
    "Aplica una funcion binaria acumulando; para sumas o productos hay alternativas mas claras (sum, math.prod).",
    "from functools import reduce\nreduce(lambda a, b: a*b, [1, 2, 3, 4])  # 24"),
"regex": ("Expresiones regulares (modulo re) para buscar y manipular texto segun patrones.",
    "Compila patrones con re.compile; usa cadenas raw (r'...') para las barras invertidas.",
    "import re\nre.findall(r'\\d+', 'a12b3')  # ['12', '3']"),
"retorno_multiple": ("Devolucion de varios valores desde una funcion empaquetandolos en una tupla.",
    "El receptor los desempaqueta en variables separadas; mejora la claridad frente a parametros de salida.",
    "def divmod2(a, b):\n    return a // b, a % b\nc, r = divmod2(7, 2)"),
"self_param": ("Primer parametro de los metodos de instancia que referencia al propio objeto.",
    "Es explicito por convencion (no palabra clave); olvidarlo causa un TypeError frecuente en principiantes.",
    "class C:\n    def m(self):\n        return self"),
"slicing": ("Extraccion de subsecuencias mediante la notacion [inicio:fin:paso].",
    "El fin se excluye; admite indices negativos y omitir extremos. xs[:] copia la secuencia.",
    "xs = [0, 1, 2, 3, 4]\nxs[1:4]  # [1, 2, 3]"),
"slicing_str": ("Aplicacion del slicing a cadenas para obtener subcadenas.",
    "Las cadenas son inmutables: el slicing devuelve una nueva cadena. xs[::-1] la invierte.",
    "'Python'[0:3]  # 'Pyt'"),
"sobrecarga_operadores": ("Definicion del comportamiento de los operadores (+, ==, []) para objetos propios.",
    "Se implementa con metodos dunder (__add__, __eq__); usala cuando aporte semantica natural.",
    "class V:\n    def __init__(self, n): self.n = n\n    def __add__(self, o): return V(self.n + o.n)"),
"sorted_f": ("Funcion sorted() que devuelve una lista ordenada y metodo list.sort() que ordena en sitio.",
    "Admiten key para criterio y reverse; el algoritmo Timsort es estable y O(n log n).",
    "sorted([3, 1, 2])  # [1, 2, 3]\nsorted(palabras, key=len)"),
"str_repr": ("Metodos __str__ (representacion legible) y __repr__ (representacion no ambigua) de un objeto.",
    "__str__ se usa en print y __repr__ en la consola/depuracion; define __repr__ al menos.",
    "class P:\n    def __repr__(self):\n        return f'P({self.x!r})'"),
"super_call": ("Funcion super() que invoca metodos de la clase base segun el MRO.",
    "Esencial para encadenar __init__ en herencia y cooperar correctamente con herencia multiple.",
    "class B(A):\n    def __init__(self):\n        super().__init__()"),
"tabla_hash": ("Estructura que asocia claves a valores usando una funcion hash para acceso medio O(1).",
    "Es la base interna de dict y set; las colisiones se resuelven internamente.",
    "d = {}\nd['clave'] = 'valor'  # respaldado por una tabla hash"),
"ternario": ("Expresion condicional en una linea: valor_si_verdadero if condicion else valor_si_falso.",
    "Util para asignaciones breves; si la logica crece, un if/else completo es mas claro.",
    "signo = 'par' if n % 2 == 0 else 'impar'"),
"tipo_bool": ("Tipo booleano con los valores True y False, subtipo de int.",
    "Resulta de comparaciones; True equivale a 1 y False a 0 en contextos numericos.",
    "es_mayor = 5 > 3  # True"),
"tipo_bytes": ("Secuencia inmutable de bytes (0-255) para datos binarios.",
    "Se obtiene codificando texto; no confundas bytes con str. Para datos mutables usa bytearray.",
    "b'abc'\n'cana'.encode('utf-8')"),
"tipo_complex": ("Tipo numerico para numeros complejos con parte real e imaginaria (sufijo j).",
    "Soporta aritmetica compleja nativa; accede a .real y .imag.",
    "z = 2 + 3j\nz.real  # 2.0"),
"tipo_float": ("Tipo numerico de coma flotante de doble precision (IEEE 754).",
    "Tiene precision limitada: evita comparar floats con == y usa math.isclose.",
    "0.1 + 0.2  # 0.30000000000000004"),
"tipo_int": ("Tipo numerico entero de precision arbitraria en Python.",
    "No desborda como en otros lenguajes; admite bases y separadores de miles con guion bajo.",
    "10 ** 100  # entero enorme sin desbordamiento"),
"tipo_none": ("Tipo con un unico valor, None, que representa la ausencia de valor.",
    "Es el retorno por defecto de las funciones; comparalo con is None, no con ==.",
    "def f():\n    pass\nf() is None  # True"),
"tipo_str": ("Secuencia inmutable de caracteres Unicode para representar texto.",
    "Admite indexacion, slicing y muchos metodos; al ser inmutable, cada operacion crea una cadena nueva.",
    "s = 'Python'\ns[0]  # 'P'"),
"truthiness": ("Evaluacion de un objeto como verdadero o falso en un contexto booleano.",
    "Colecciones vacias, 0, None y '' son falsy; el resto es truthy. Aprovechalo en condiciones idiomaticas.",
    "if not lista:\n    print('vacia')"),
"try_except_else": ("Estructura try/except/else/finally para capturar y gestionar excepciones.",
    "else se ejecuta si no hubo excepcion y finally siempre; mantenes el try lo mas pequeno posible.",
    "try:\n    x = int(s)\nexcept ValueError:\n    x = 0\nelse:\n    print('ok')\nfinally:\n    print('fin')"),
"tupla": ("Secuencia ordenada e inmutable de elementos, posiblemente de distintos tipos.",
    "Util para datos heterogeneos fijos y como claves de diccionario; es hashable si sus elementos lo son.",
    "punto = (3, 4)\nx, y = punto"),
"type_checking": ("Comprobacion estatica de tipos a partir de las anotaciones, sin ejecutar el programa.",
    "Herramientas como mypy detectan incoherencias antes de la ejecucion; no afecta al rendimiento.",
    "# def f(x: int) -> int: return x + 1\n# mypy avisa si se llama f('a')"),
"typing_generics": ("Tipos genericos parametrizados (TypeVar, Generic) que abstraen el tipo de los elementos.",
    "Permiten contenedores con seguridad de tipos reutilizables; el chequeo lo hace el verificador estatico.",
    "from typing import TypeVar\nT = TypeVar('T')\ndef primero(xs: list[T]) -> T:\n    return xs[0]"),
"typing_optional": ("Anotacion Optional[X] que indica un valor de tipo X o None.",
    "Equivale a Union[X, None]; documenta funciones que pueden no devolver un valor.",
    "from typing import Optional\ndef buscar(k) -> Optional[int]:\n    return None"),
"typing_union": ("Anotacion Union[A, B] que indica que un valor puede ser de varios tipos.",
    "Desde Python 3.10 se escribe A | B; usala con moderacion para no diluir el tipado.",
    "from typing import Union\ndef f(x: Union[int, str]) -> str:\n    return str(x)"),
"unittest_mod": ("Marco de pruebas unittest de la biblioteca estandar, basado en clases TestCase.",
    "Inspirado en xUnit; ofrece metodos assert y setUp/tearDown para preparar cada prueba.",
    "import unittest\nclass T(unittest.TestCase):\n    def test_ok(self):\n        self.assertEqual(1 + 1, 2)"),
"valor_por_defecto": ("Valor asignado a un parametro cuando la llamada no proporciona ese argumento.",
    "Nunca uses objetos mutables como valor por defecto: se comparten entre llamadas. Usa None y crealo dentro.",
    "def f(xs=None):\n    if xs is None:\n        xs = []"),
"variable": ("Nombre que referencia un valor almacenado en memoria.",
    "En Python no se declara el tipo: el nombre se vincula al objeto en la asignacion y puede reasignarse.",
    "x = 42\nx = 'ahora texto'"),
"walrus": ("Operador de asignacion en expresion := que asigna y devuelve un valor a la vez.",
    "Disponible desde Python 3.8; util para reutilizar un calculo dentro de una condicion sin repetirlo.",
    "if (n := len(datos)) > 10:\n    print(f'{n} elementos')"),
"with_context": ("Sentencia with que delega en un gestor de contexto la apertura y cierre de un recurso.",
    "Garantiza la liberacion del recurso aunque ocurra una excepcion; reduce el codigo repetitivo de try/finally.",
    "with open('f.txt') as f:\n    datos = f.read()"),
"yield_from": ("Expresion yield from que delega la produccion de valores a otro generador o iterable.",
    "Simplifica la composicion de generadores y transmite valores enviados y excepciones.",
    "def aplanar(listas):\n    for l in listas:\n        yield from l"),
"zip_f": ("Funcion zip() que combina varios iterables en tuplas de elementos correspondientes.",
    "Se detiene en el iterable mas corto; zip(*m) permite transponer; para rellenar usa itertools.zip_longest.",
    "list(zip([1, 2], ['a', 'b']))  # [(1, 'a'), (2, 'b')]"),
}


#  2. CONCEPTOS NUEVOS (>=56)
#     campos: tipo, tema, dif, nivel, prereq, def, scope, ej,
#             y opcionales: wd, dbr, broader, related, version, big_o, url
NUEVOS = [
 dict(id="lista_enlazada", tipo="EstructuraDeDatos", tema="T_estructuras", dif=3, nivel="intermedio",
      en="Linked list", es="Lista enlazada", prereq=["objeto", "clase"], wd="Q7003418",
      dbr="Linked_list", related=["lista"], big_o="O(n)",
      d="Estructura lineal de nodos donde cada nodo guarda un valor y una referencia al siguiente.",
      s="Insertar al principio es O(1), pero el acceso por posicion es O(n); en Python suele bastar con list o deque.",
      e="class Nodo:\n    def __init__(self, valor, sig=None):\n        self.valor = valor\n        self.sig = sig"),
 dict(id="arbol_binario", tipo="EstructuraDeDatos", tema="T_algoritmos", dif=4, nivel="avanzado",
      en="Binary tree", es="Arbol binario", prereq=["arbol_estr"], dbr="Binary_tree",
      broader="arbol_estr", wd="Q380172",
      d="Arbol en el que cada nodo tiene como maximo dos hijos, izquierdo y derecho.",
      s="Base de los arboles de busqueda y los montículos; se recorre en preorden, inorden o postorden.",
      e="class NodoB:\n    def __init__(self, v):\n        self.v = v\n        self.izq = self.der = None"),
 dict(id="arbol_busqueda_binaria", tipo="EstructuraDeDatos", tema="T_algoritmos", dif=4, nivel="avanzado",
      en="Binary search tree", es="Arbol de busqueda binaria", prereq=["arbol_binario"], dbr="Binary_search_tree",
      broader="arbol_binario", big_o="O(log n)",
      d="Arbol binario donde el subarbol izquierdo solo contiene valores menores y el derecho, mayores.",
      s="Permite busqueda, insercion y borrado en O(log n) si esta equilibrado; degenera a O(n) si no.",
      e="def buscar(nodo, x):\n    if nodo is None or nodo.v == x:\n        return nodo\n    return buscar(nodo.izq if x < nodo.v else nodo.der, x)"),
 dict(id="cola_prioridad", tipo="EstructuraDeDatos", tema="T_estructuras", dif=4, nivel="avanzado",
      en="Priority queue", es="Cola de prioridad", prereq=["heap"], dbr="Priority_queue",
      related=["cola", "heap"], big_o="O(log n)", wd="Q629283",
      d="Cola en la que cada elemento tiene una prioridad y se extrae siempre el de mayor prioridad.",
      s="Se implementa eficientemente con un monticulo (heapq); base de algoritmos como Dijkstra.",
      e="import heapq\npq = []\nheapq.heappush(pq, (2, 'tarea B'))\nheapq.heappush(pq, (1, 'tarea A'))\nheapq.heappop(pq)  # (1, 'tarea A')"),
 dict(id="frozenset_tipo", tipo="EstructuraDeDatos", tema="T_estructuras", dif=3, nivel="intermedio",
      en="frozenset", es="Conjunto inmutable (frozenset)", prereq=["conjunto"], related=["conjunto"],
      d="Version inmutable y hashable del conjunto, que no admite anadir ni quitar elementos.",
      s="Al ser hashable puede usarse como clave de diccionario o elemento de otro conjunto.",
      e="fs = frozenset({1, 2, 3})\n{fs: 'valor'}  # valido como clave"),
 dict(id="ordered_dict", tipo="EstructuraDeDatos", tema="T_estructuras", dif=3, nivel="intermedio",
      en="OrderedDict", es="collections.OrderedDict", prereq=["diccionario"], related=["diccionario"],
      d="Diccionario que recuerda el orden de insercion y ofrece operaciones de reordenacion.",
      s="Desde Python 3.7 dict ya conserva el orden, pero OrderedDict aporta move_to_end e igualdad sensible al orden.",
      e="from collections import OrderedDict\nd = OrderedDict(a=1, b=2)\nd.move_to_end('a')"),
 dict(id="chainmap", tipo="EstructuraDeDatos", tema="T_estructuras", dif=3, nivel="intermedio",
      en="ChainMap", es="collections.ChainMap", prereq=["diccionario"], related=["diccionario"],
      d="Vista que agrupa varios diccionarios y los consulta como si fueran uno solo.",
      s="Util para gestionar capas de configuracion (por defecto, usuario, entorno) sin copiarlas.",
      e="from collections import ChainMap\ncfg = ChainMap({'a': 1}, {'a': 0, 'b': 2})\ncfg['a']  # 1"),
 dict(id="bytearray_tipo", tipo="TipoDeDato", tema="T_tipos", dif=3, nivel="intermedio",
      en="bytearray", es="bytearray", prereq=["tipo_bytes"], related=["tipo_bytes"],
      d="Secuencia mutable de bytes que permite modificar su contenido en sitio.",
      s="Util para construir o transformar datos binarios sin crear copias; complementa al inmutable bytes.",
      e="ba = bytearray(b'abc')\nba[0] = 65  # b'Abc'"),
 dict(id="memoryview_tipo", tipo="TipoDeDato", tema="T_tipos", dif=4, nivel="avanzado",
      en="memoryview", es="memoryview", prereq=["tipo_bytes"],
      d="Vista que expone el buffer de memoria de un objeto binario sin copiarlo.",
      s="Permite manipular grandes bloques de bytes de forma eficiente, por ejemplo al hacer slicing.",
      e="mv = memoryview(bytearray(b'abcdef'))\nbytes(mv[1:4])  # b'bcd'"),
 dict(id="recoleccion_basura", tipo="PrincipioTransversal", tema="T_fundamentos", dif=4, nivel="avanzado",
      en="Garbage collection", es="Recoleccion de basura", prereq=["objeto"], wd="Q322202",
      dbr="Garbage_collection_(computer_science)",
      d="Gestion automatica de la memoria que libera los objetos que ya no son alcanzables.",
      s="CPython usa conteo de referencias mas un recolector ciclico (modulo gc) para los ciclos de referencias.",
      e="import gc\ngc.collect()  # fuerza una recoleccion"),
 dict(id="conteo_referencias", tipo="PrincipioTransversal", tema="T_fundamentos", dif=4, nivel="avanzado",
      en="Reference counting", es="Conteo de referencias", prereq=["recoleccion_basura"],
      dbr="Reference_counting", related=["recoleccion_basura"],
      d="Tecnica que libera un objeto cuando el numero de referencias que lo apuntan llega a cero.",
      s="Es inmediata pero no detecta ciclos; por eso CPython la combina con un recolector de ciclos.",
      e="import sys\nx = []\nsys.getrefcount(x)  # numero de referencias"),
 dict(id="duck_typing", tipo="Paradigma", tema="T_poo", dif=3, nivel="intermedio",
      en="Duck typing", es="Duck typing", prereq=["polimorfismo"], dbr="Duck_typing",
      related=["polimorfismo"], wd="Q374282",
      d="Estilo en el que la idoneidad de un objeto depende de los metodos que ofrece, no de su tipo.",
      s="'Si camina como un pato y grazna como un pato, es un pato'; favorece el polimorfismo flexible.",
      e="def total(coleccion):\n    return sum(coleccion)  # vale cualquier iterable de numeros"),
 dict(id="descriptor", tipo="Paradigma", tema="T_poo", dif=5, nivel="avanzado",
      en="Descriptor", es="Descriptor", prereq=["propiedad"],
      d="Objeto que define __get__, __set__ o __delete__ para controlar el acceso a un atributo.",
      s="Es el mecanismo subyacente de property, los metodos y classmethod; protocolo avanzado de POO.",
      e="class SoloLectura:\n    def __get__(self, obj, tipo=None):\n        return 42"),
 dict(id="metaclase", tipo="Paradigma", tema="T_poo", dif=5, nivel="avanzado",
      en="Metaclass", es="Metaclase", prereq=["clase"], dbr="Metaclass", wd="Q1924819",
      d="Clase cuyas instancias son a su vez clases, lo que permite personalizar como se crean.",
      s="type es la metaclase por defecto; rara vez necesarias, pero potentes para frameworks (ORM, ABC).",
      e="class Meta(type):\n    def __new__(mcs, n, b, d):\n        return super().__new__(mcs, n, b, d)"),
 dict(id="slots", tipo="Paradigma", tema="T_poo", dif=4, nivel="avanzado",
      en="__slots__", es="__slots__", prereq=["atributo"],
      d="Declaracion que fija los atributos permitidos de una clase y evita el __dict__ por instancia.",
      s="Reduce el consumo de memoria con muchas instancias, a costa de perder atributos dinamicos.",
      e="class Punto:\n    __slots__ = ('x', 'y')\n    def __init__(self, x, y):\n        self.x, self.y = x, y"),
 dict(id="atributo_clase", tipo="Paradigma", tema="T_poo", dif=3, nivel="intermedio",
      en="Class attribute", es="Atributo de clase", prereq=["atributo"], related=["atributo"],
      d="Atributo definido en la clase y compartido por todas sus instancias.",
      s="Cuidado al usar valores mutables: se comparten entre instancias; las asignaciones via self crean copias locales.",
      e="class Contador:\n    total = 0  # atributo de clase compartido"),
 dict(id="protocolo_typing", tipo="ConceptoDeTipado", tema="T_tipos", dif=4, nivel="avanzado",
      en="Protocol (structural typing)", es="typing.Protocol", prereq=["anotaciones_tipo"], version="3.8",
      d="Tipo que describe una interfaz por su estructura (metodos y atributos), no por herencia explicita.",
      s="Formaliza el duck typing para los verificadores estaticos; una clase la satisface si tiene los miembros.",
      e="from typing import Protocol\nclass Dibujable(Protocol):\n    def dibujar(self) -> None: ..."),
 dict(id="typing_callable", tipo="ConceptoDeTipado", tema="T_tipos", dif=3, nivel="intermedio",
      en="typing.Callable", es="typing.Callable", prereq=["anotaciones_tipo", "funcion_orden_superior"],
      d="Anotacion que describe el tipo de un objeto invocable indicando sus argumentos y retorno.",
      s="Util para anotar callbacks y funciones de orden superior; Callable[[int], str] toma un int y devuelve str.",
      e="from typing import Callable\ndef aplica(f: Callable[[int], int], x: int) -> int:\n    return f(x)"),
 dict(id="typing_literal", tipo="ConceptoDeTipado", tema="T_tipos", dif=3, nivel="intermedio",
      en="typing.Literal", es="typing.Literal", prereq=["anotaciones_tipo"], version="3.8",
      d="Anotacion que restringe un valor a un conjunto concreto de constantes literales.",
      s="Documenta parametros que solo admiten ciertos valores; el verificador rechaza los demas.",
      e="from typing import Literal\ndef mover(d: Literal['n', 's', 'e', 'o']) -> None: ..."),
 dict(id="typing_typeddict", tipo="ConceptoDeTipado", tema="T_tipos", dif=4, nivel="avanzado",
      en="TypedDict", es="typing.TypedDict", prereq=["anotaciones_tipo", "diccionario"], version="3.8",
      d="Tipo que especifica las claves esperadas de un diccionario y el tipo de cada valor.",
      s="Aporta seguridad de tipos a los diccionarios tipo registro sin crear una clase.",
      e="from typing import TypedDict\nclass Usuario(TypedDict):\n    nombre: str\n    edad: int"),
 dict(id="typing_any", tipo="ConceptoDeTipado", tema="T_tipos", dif=2, nivel="intermedio",
      en="typing.Any", es="typing.Any", prereq=["anotaciones_tipo"],
      d="Tipo comodin compatible con cualquier otro, que desactiva la comprobacion estatica.",
      s="Usalo con moderacion: cada Any es un agujero en el tipado; prefiere tipos concretos o genericos.",
      e="from typing import Any\ndef registrar(valor: Any) -> None:\n    print(valor)"),
 dict(id="typing_final", tipo="ConceptoDeTipado", tema="T_tipos", dif=3, nivel="intermedio",
      en="typing.Final", es="typing.Final", prereq=["anotaciones_tipo"], version="3.8",
      d="Anotacion que marca un nombre como constante que no debe reasignarse ni redefinirse.",
      s="El verificador estatico avisa si se intenta modificar; no impide el cambio en tiempo de ejecucion.",
      e="from typing import Final\nMAX: Final = 100"),
 dict(id="variable_anotada", tipo="ConceptoDeTipado", tema="T_tipos", dif=2, nivel="intermedio",
      en="Variable annotations", es="Anotaciones de variable", prereq=["anotaciones_tipo"], version="3.6",
      d="Sintaxis (PEP 526) para anotar el tipo de una variable, con o sin asignacion.",
      s="Las anotaciones se guardan en __annotations__; documentan la intencion sin afectar a la ejecucion.",
      e="conteo: int = 0\nnombres: list[str]"),
 dict(id="future_annotations", tipo="ConceptoDeTipado", tema="T_tipos", dif=4, nivel="avanzado",
      en="Postponed annotations", es="from __future__ import annotations", prereq=["anotaciones_tipo"], version="3.7",
      d="Directiva que evalua las anotaciones como cadenas, posponiendo su resolucion.",
      s="Evita referencias adelantadas y costes de importacion; conviene conocerla al usar tipos recursivos.",
      e="from __future__ import annotations\nclass Nodo:\n    sig: Nodo | None = None"),
 dict(id="operador_aritmetico", tipo="OperadorDelLenguaje", tema="T_fundamentos", dif=1, nivel="basico",
      en="Arithmetic operators", es="Operadores aritmeticos", prereq=["variable"],
      d="Operadores que realizan calculos numericos: +, -, *, /, //, % y **.",
      s="// es la division entera y / siempre devuelve float; ** eleva a una potencia.",
      e="7 // 2   # 3\n7 % 2    # 1\n2 ** 10  # 1024"),
 dict(id="operador_comparacion", tipo="OperadorDelLenguaje", tema="T_fundamentos", dif=1, nivel="basico",
      en="Comparison operators", es="Operadores de comparacion", prereq=["variable"],
      d="Operadores que comparan valores y devuelven un booleano: ==, !=, <, <=, >, >=.",
      s="Pueden encadenarse (1 < x < 10); == compara valor mientras que is compara identidad.",
      e="1 < 2 <= 2  # True"),
 dict(id="operador_logico", tipo="OperadorDelLenguaje", tema="T_fundamentos", dif=1, nivel="basico",
      en="Logical operators", es="Operadores logicos", prereq=["tipo_bool"],
      d="Operadores and, or y not que combinan o niegan expresiones booleanas.",
      s="and/or evaluan de forma perezosa (cortocircuito) y devuelven uno de los operandos, no solo True/False.",
      e="(x > 0) and (x < 10)\nnombre or 'anonimo'"),
 dict(id="operador_bitwise", tipo="OperadorDelLenguaje", tema="T_fundamentos", dif=3, nivel="intermedio",
      en="Bitwise operators", es="Operadores a nivel de bits", prereq=["tipo_int"],
      d="Operadores que manipulan los bits individuales de los enteros: &, |, ^, ~, << y >>.",
      s="Utiles para mascaras, banderas y optimizaciones; no confundir & con and.",
      e="0b1100 & 0b1010  # 0b1000 (8)\n1 << 4           # 16"),
 dict(id="operador_pertenencia", tipo="OperadorDelLenguaje", tema="T_estructuras", dif=1, nivel="basico",
      en="Membership operators", es="Operadores de pertenencia (in)", prereq=["lista"],
      d="Operadores in y not in que comprueban si un valor esta contenido en una coleccion.",
      s="En sets y dicts es O(1); en listas es O(n). Tambien busca subcadenas en strings.",
      e="3 in [1, 2, 3]   # True\n'a' in 'casa'    # True"),
 dict(id="operador_identidad", tipo="OperadorDelLenguaje", tema="T_tipos", dif=2, nivel="intermedio",
      en="Identity operators", es="Operadores de identidad (is)", prereq=["identidad_objetos"],
      d="Operadores is e is not que comprueban si dos nombres referencian el mismo objeto.",
      s="Reservalos para comparar con None; para igualdad de valor usa ==.",
      e="x = None\nx is None  # True"),
 dict(id="operador_asignacion_aumentada", tipo="OperadorDelLenguaje", tema="T_fundamentos", dif=1, nivel="basico",
      en="Augmented assignment", es="Asignacion aumentada", prereq=["asignacion"],
      d="Operadores como +=, -= o *= que combinan una operacion con la asignacion.",
      s="En objetos mutables (listas) modifican en sitio; en inmutables crean un objeto nuevo.",
      e="total = 0\ntotal += 5  # total == 5"),
 dict(id="concatenacion_str", tipo="PrincipioTransversal", tema="T_strings", dif=1, nivel="basico",
      en="String concatenation", es="Concatenacion de cadenas", prereq=["tipo_str"],
      d="Union de varias cadenas en una sola mediante el operador + o por yuxtaposicion.",
      s="Para unir muchas cadenas en un bucle, str.join es mas eficiente que la concatenacion repetida.",
      e="'Hola' + ' ' + 'mundo'\n''.join(['a', 'b', 'c'])"),
 dict(id="format_method", tipo="FuncionIntegrada", tema="T_strings", dif=2, nivel="basico",
      en="str.format", es="Metodo str.format", prereq=["tipo_str"], related=["fstring"],
      d="Metodo que inserta valores en una cadena usando campos de reemplazo con llaves.",
      s="Anterior a las f-strings; sigue siendo util para plantillas reutilizables separadas de los datos.",
      e="'{} tiene {} anos'.format('Ana', 30)"),
 dict(id="metodo_split_join", tipo="FuncionIntegrada", tema="T_strings", dif=2, nivel="basico",
      en="split and join", es="Metodos split y join", prereq=["tipo_str", "lista"],
      d="split() divide una cadena en una lista y join() une una lista de cadenas con un separador.",
      s="Son operaciones inversas habituales al procesar texto y ficheros delimitados.",
      e="'a,b,c'.split(',')   # ['a', 'b', 'c']\n'-'.join(['a', 'b'])  # 'a-b'"),
 dict(id="fstring_format_spec", tipo="PrincipioTransversal", tema="T_strings", dif=3, nivel="intermedio",
      en="Format specification", es="Mini-lenguaje de formato", prereq=["fstring"], related=["fstring"],
      d="Sintaxis tras los dos puntos en un campo de formato para controlar ancho, precision y alineacion.",
      s="Permite formatear numeros (:.2f), porcentajes (:.0%) o rellenar con ceros (:03d).",
      e="import math\nf'{math.pi:.2f}'  # '3.14'\nf'{42:05d}'        # '00042'"),
 dict(id="raw_string", tipo="PrincipioTransversal", tema="T_strings", dif=2, nivel="basico",
      en="Raw strings", es="Cadenas en bruto (raw)", prereq=["tipo_str"], related=["regex"],
      d="Cadena con prefijo r en la que la barra invertida no se interpreta como secuencia de escape.",
      s="Imprescindible para patrones de expresiones regulares y rutas de Windows.",
      e="ruta = r'C:\\nuevo\\datos'\npatron = r'\\d+'"),
 dict(id="multilinea_str", tipo="PrincipioTransversal", tema="T_strings", dif=1, nivel="basico",
      en="Triple-quoted strings", es="Cadenas multilinea", prereq=["tipo_str"],
      d="Cadena delimitada por triples comillas que puede abarcar varias lineas.",
      s="Tambien se usan como docstrings; conservan los saltos de linea y la sangria literal.",
      e='texto = """linea 1\nlinea 2"""'),
 dict(id="with_multiple", tipo="EstructuraDeControl", tema="T_control", dif=4, nivel="avanzado",
      en="Multiple context managers", es="with multiple", prereq=["with_context"], related=["with_context"],
      d="Sintaxis que gestiona varios recursos en una sola sentencia with separados por comas.",
      s="Desde Python 3.10 admite parentesis para repartirlos en varias lineas de forma legible.",
      e="with open('a') as a, open('b') as b:\n    b.write(a.read())"),
 dict(id="contextlib_mod", tipo="ModuloLibreria", tema="T_control", dif=4, nivel="avanzado",
      en="contextlib", es="Modulo contextlib", prereq=["context_manager"], related=["context_manager"],
      d="Modulo con utilidades para crear gestores de contexto, como el decorador @contextmanager.",
      s="@contextmanager convierte un generador con un unico yield en un gestor de contexto.",
      e="from contextlib import contextmanager\n@contextmanager\ndef abierto(p):\n    f = open(p)\n    try:\n        yield f\n    finally:\n        f.close()"),
 dict(id="suppress_context", tipo="EstructuraDeControl", tema="T_excepciones", dif=3, nivel="intermedio",
      en="contextlib.suppress", es="contextlib.suppress", prereq=["try_except_else"], related=["try_except_else"],
      d="Gestor de contexto que ignora silenciosamente las excepciones indicadas dentro del bloque.",
      s="Alternativa concisa a un try/except con pass; usalo solo cuando ignorar el error sea intencionado.",
      e="from contextlib import suppress\nwith suppress(FileNotFoundError):\n    open('quiza.txt')"),
 dict(id="finally_clause", tipo="EstructuraDeControl", tema="T_excepciones", dif=2, nivel="intermedio",
      en="finally clause", es="Clausula finally", prereq=["try_except_else"], broader="try_except_else",
      d="Bloque finally que se ejecuta siempre tras un try, haya o no excepcion.",
      s="Ideal para liberar recursos; se ejecuta incluso si hay return dentro del try.",
      e="try:\n    f = open('d')\nfinally:\n    print('siempre se ejecuta')"),
 dict(id="concurrent_futures", tipo="ConceptoDeConcurrencia", tema="T_concurrencia", dif=4, nivel="avanzado",
      en="concurrent.futures", es="concurrent.futures", prereq=["hilos"], related=["hilos", "multiproceso"],
      d="Interfaz de alto nivel para ejecutar tareas en grupos de hilos o procesos mediante Executors.",
      s="ThreadPoolExecutor para E/S y ProcessPoolExecutor para CPU; map() y submit() devuelven futuros.",
      e="from concurrent.futures import ThreadPoolExecutor\nwith ThreadPoolExecutor() as ex:\n    list(ex.map(str, range(3)))"),
 dict(id="lock_threading", tipo="ConceptoDeConcurrencia", tema="T_concurrencia", dif=5, nivel="avanzado",
      en="Lock", es="Cerrojo (Lock)", prereq=["hilos"], dbr="Lock_(computer_science)", related=["hilos"], wd="Q1047554",
      d="Primitiva de sincronizacion que garantiza que solo un hilo accede a una seccion critica a la vez.",
      s="Protege estado compartido frente a condiciones de carrera; usalo como gestor de contexto con with.",
      e="import threading\ncerrojo = threading.Lock()\nwith cerrojo:\n    saldo += 1"),
 dict(id="condicion_carrera", tipo="ConceptoDeConcurrencia", tema="T_concurrencia", dif=5, nivel="avanzado",
      en="Race condition", es="Condicion de carrera", prereq=["hilos"], dbr="Race_condition",
      related=["lock_threading"], wd="Q616554",
      d="Defecto en el que el resultado depende del orden imprevisible en que se intercalan los hilos.",
      s="Se evita sincronizando el acceso al estado compartido con cerrojos u otras primitivas.",
      e="# saldo += 1 no es atomico: dos hilos pueden\n# leer el mismo valor y perder una actualizacion"),
 dict(id="interbloqueo", tipo="ConceptoDeConcurrencia", tema="T_concurrencia", dif=5, nivel="avanzado",
      en="Deadlock", es="Interbloqueo", prereq=["lock_threading"], dbr="Deadlock", related=["lock_threading"], wd="Q623276",
      d="Situacion en la que dos o mas hilos se bloquean mutuamente esperando recursos que el otro retiene.",
      s="Se previene adquiriendo los cerrojos siempre en el mismo orden o con tiempos de espera.",
      e="# Hilo 1: lock_a luego lock_b\n# Hilo 2: lock_b luego lock_a  -> interbloqueo"),
 dict(id="event_loop", tipo="ConceptoDeConcurrencia", tema="T_concurrencia", dif=5, nivel="avanzado",
      en="Event loop", es="Bucle de eventos", prereq=["asyncio_mod"], dbr="Event_loop", related=["asyncio_mod"], wd="Q1349935",
      d="Planificador que ejecuta y reanuda corrutinas a medida que sus operaciones de E/S se completan.",
      s="Es el nucleo de asyncio; asyncio.run() crea y gestiona el bucle por ti.",
      e="import asyncio\nasyncio.run(main())  # arranca el bucle de eventos"),
 dict(id="async_generator", tipo="EstructuraDeControl", tema="T_concurrencia", dif=5, nivel="avanzado",
      en="Async generator", es="Generador asincrono", prereq=["async_await", "generador"], version="3.6",
      d="Funcion async def que produce valores con yield y se recorre con async for.",
      s="Combina produccion perezosa y espera asincrona; util para flujos de datos de red por lotes.",
      e="async def numeros():\n    for i in range(3):\n        await asyncio.sleep(0)\n        yield i"),
 dict(id="lru_cache", tipo="ModuloLibreria", tema="T_funcional", dif=4, nivel="avanzado",
      en="functools.lru_cache", es="functools.lru_cache", prereq=["memoizacion", "decorador"], related=["memoizacion"],
      d="Decorador que cachea los resultados de una funcion descartando los menos usados (LRU).",
      s="Acelera funciones puras y deterministas; los argumentos deben ser hashables.",
      e="from functools import lru_cache\n@lru_cache(maxsize=None)\ndef fib(n):\n    return n if n < 2 else fib(n-1) + fib(n-2)"),
 dict(id="cached_property_mod", tipo="ModuloLibreria", tema="T_poo", dif=4, nivel="avanzado",
      en="functools.cached_property", es="functools.cached_property", prereq=["propiedad"], version="3.8",
      related=["propiedad"],
      d="Decorador que convierte un metodo en una propiedad cuyo valor se calcula una vez y se cachea.",
      s="Ideal para calculos costosos que no cambian; el resultado se guarda en el __dict__ de la instancia.",
      e="from functools import cached_property\nclass D:\n    @cached_property\n    def media(self):\n        return sum(self.xs) / len(self.xs)"),
 dict(id="singledispatch", tipo="ModuloLibreria", tema="T_funcional", dif=4, nivel="avanzado",
      en="functools.singledispatch", es="functools.singledispatch", prereq=["polimorfismo"], related=["polimorfismo"],
      d="Decorador que crea una funcion generica cuya implementacion se elige segun el tipo del primer argumento.",
      s="Aporta despacho multiple basico al estilo funcional, sin recurrir a una jerarquia de clases.",
      e="from functools import singledispatch\n@singledispatch\ndef mostrar(x): print(x)\n@mostrar.register\ndef _(x: list): print('lista', x)"),
 dict(id="itertools_chain", tipo="ModuloLibreria", tema="T_funcional", dif=3, nivel="intermedio",
      en="itertools.chain", es="itertools.chain", prereq=["itertools_mod"], broader="itertools_mod",
      d="Funcion que encadena varios iterables y los recorre como una unica secuencia.",
      s="Evita crear listas intermedias al concatenar; chain.from_iterable aplana un iterable de iterables.",
      e="from itertools import chain\nlist(chain([1, 2], [3, 4]))  # [1, 2, 3, 4]"),
 dict(id="itertools_product", tipo="ModuloLibreria", tema="T_funcional", dif=3, nivel="intermedio",
      en="itertools.product", es="itertools.product", prereq=["itertools_mod"], broader="itertools_mod",
      d="Funcion que genera el producto cartesiano de varios iterables.",
      s="Equivale a bucles for anidados; util para explorar combinaciones de parametros.",
      e="from itertools import product\nlist(product([0, 1], repeat=2))  # [(0,0),(0,1),(1,0),(1,1)]"),
 dict(id="any_all", tipo="FuncionIntegrada", tema="T_control", dif=2, nivel="basico",
      en="any and all", es="Funciones any y all", prereq=["iterables"], related=["truthiness"],
      d="any() devuelve True si algun elemento es verdadero; all() si todos lo son.",
      s="Operan de forma perezosa con cortocircuito; sobre un iterable vacio, all es True y any es False.",
      e="all(x > 0 for x in [1, 2, 3])  # True\nany(x < 0 for x in [1, 2, 3])  # False"),
 dict(id="min_max", tipo="FuncionIntegrada", tema="T_algoritmos", dif=1, nivel="basico",
      en="min and max", es="Funciones min y max", prereq=["iterables"],
      d="Funciones que devuelven el menor o mayor elemento de un iterable o de varios argumentos.",
      s="Aceptan key para definir el criterio y default para iterables vacios.",
      e="max([3, 1, 2])             # 3\nmax(palabras, key=len)"),
 dict(id="sum_func", tipo="FuncionIntegrada", tema="T_control", dif=1, nivel="basico",
      en="sum", es="Funcion sum", prereq=["iterables"],
      d="Funcion que suma los elementos de un iterable numerico, con un valor inicial opcional.",
      s="No la uses para concatenar cadenas (usa join); admite un segundo argumento como punto de partida.",
      e="sum([1, 2, 3])      # 6\nsum([1, 2], 10)     # 13"),
 dict(id="isinstance_func", tipo="FuncionIntegrada", tema="T_poo", dif=2, nivel="basico",
      en="isinstance", es="Funcion isinstance", prereq=["clase"], related=["herencia"],
      d="Funcion que comprueba si un objeto es instancia de una clase o de alguna de varias clases.",
      s="Respeta la herencia y es preferible a comparar type(x) directamente; acepta una tupla de tipos.",
      e="isinstance(3, (int, float))  # True"),
 dict(id="getattr_setattr", tipo="FuncionIntegrada", tema="T_poo", dif=3, nivel="intermedio",
      en="getattr and setattr", es="getattr y setattr", prereq=["atributo"], related=["atributo"],
      d="Funciones que leen y escriben atributos de un objeto a partir de su nombre como cadena.",
      s="Permiten acceso dinamico a atributos; getattr admite un valor por defecto para evitar AttributeError.",
      e="getattr(obj, 'x', 0)\nsetattr(obj, 'x', 10)"),
 dict(id="callable_func", tipo="FuncionIntegrada", tema="T_funcional", dif=3, nivel="intermedio",
      en="callable", es="Funcion callable", prereq=["funcion"], related=["funcion_orden_superior"],
      d="Funcion que indica si un objeto puede invocarse como una funcion.",
      s="Son invocables las funciones, clases y objetos con __call__; util al recibir callbacks.",
      e="callable(len)   # True\ncallable(42)    # False"),
 dict(id="nonlocal_kw", tipo="PrincipioTransversal", tema="T_funciones", dif=4, nivel="avanzado",
      en="nonlocal", es="Palabra clave nonlocal", prereq=["closure"], related=["ambito", "closure"],
      d="Declaracion que permite a una funcion anidada reasignar una variable del ambito envolvente.",
      s="Sin ella, una asignacion crearia una variable local; clave en clausuras que mantienen estado.",
      e="def contador():\n    n = 0\n    def inc():\n        nonlocal n\n        n += 1\n        return n\n    return inc"),
 dict(id="global_kw", tipo="PrincipioTransversal", tema="T_funciones", dif=3, nivel="intermedio",
      en="global", es="Palabra clave global", prereq=["ambito"], related=["ambito"],
      d="Declaracion que permite a una funcion reasignar una variable del ambito global.",
      s="Su uso suele indicar un diseno mejorable; prefiere devolver valores o encapsular el estado.",
      e="contador = 0\ndef inc():\n    global contador\n    contador += 1"),
 dict(id="dataclass_field", tipo="Paradigma", tema="T_tipos", dif=3, nivel="intermedio",
      en="dataclasses.field", es="dataclasses.field", prereq=["dataclass"], broader="dataclass",
      d="Funcion que personaliza un campo de una dataclass, por ejemplo con fabricas por defecto.",
      s="Usa default_factory=list para valores mutables por defecto y evitar compartirlos entre instancias.",
      e="from dataclasses import dataclass, field\n@dataclass\nclass C:\n    items: list = field(default_factory=list)"),
 dict(id="frozen_dataclass", tipo="Paradigma", tema="T_tipos", dif=4, nivel="avanzado",
      en="Frozen dataclass", es="Dataclass inmutable", prereq=["dataclass"], broader="dataclass",
      d="Dataclass declarada con frozen=True cuyas instancias son inmutables y hashables.",
      s="Intentar modificar un campo lanza FrozenInstanceError; util para objetos de valor.",
      e="from dataclasses import dataclass\n@dataclass(frozen=True)\nclass Punto:\n    x: int\n    y: int"),
 dict(id="patron_captura", tipo="EstructuraDeControl", tema="T_control", dif=4, nivel="avanzado",
      en="Capture patterns", es="Patrones de captura", prereq=["match_case"], broader="match_case", version="3.10",
      d="Patrones de match que extraen partes de una estructura y las vinculan a variables.",
      s="Permiten desestructurar secuencias y objetos; combinados con guardas (if) afinan la coincidencia.",
      e="match punto:\n    case (x, y) if x == y:\n        print('diagonal')\n    case (x, y):\n        print(x, y)"),
 dict(id="logging_mod", tipo="ModuloLibreria", tema="T_testing", dif=3, nivel="intermedio",
      en="logging", es="Modulo logging", prereq=["import_mod"], related=["pep8"],
      d="Modulo estandar para registrar mensajes con distintos niveles de severidad.",
      s="Preferible a print en programas reales: permite niveles, formato y destinos configurables.",
      e="import logging\nlogging.basicConfig(level=logging.INFO)\nlogging.info('iniciado')"),
 dict(id="argparse_mod", tipo="ModuloLibreria", tema="T_modulos", dif=3, nivel="intermedio",
      en="argparse", es="Modulo argparse", prereq=["modulo_sys"], related=["modulo_sys"],
      d="Modulo estandar para definir y analizar argumentos de la linea de comandos.",
      s="Genera ayuda automatica y valida tipos; mas robusto que leer sys.argv manualmente.",
      e="import argparse\np = argparse.ArgumentParser()\np.add_argument('nombre')\np.parse_args()"),
]


def build():
    g = Graph()
    g.parse(ONTO, format="turtle")
    inicial = len(g)

    g.bind("cfkg", CFKG); g.bind("cfr", CFR); g.bind("wd", WD)
    g.bind("dbr", DBR); g.bind("schema", SCHEMA); g.bind("skos", SKOS)

    leaf_classes = ["TipoDeDato", "FuncionIntegrada", "EstructuraDeDatos", "ModuloLibreria",
                    "EstructuraDeControl", "Paradigma", "PrincipioTransversal"]

    # 2.0  Completar dominios que faltaban
    g.add((CFKG.aNivelDominio, RDFS.domain, CFKG.EntidadEducativa))
    g.add((CFKG.tieneEjemploCodigo, RDFS.domain, CFKG.Concepto))

    # 2.1  Nuevas CLASES (>=8 para llegar a >=28) — todas con rdfs:subClassOf
    nuevas_clases = [
        ("Algoritmo", "Algorithm", "Algoritmo", "Concepto",
         "Procedimiento paso a paso bien definido para resolver un problema."),
        ("PatronDeDiseno", "Design pattern", "Patron de diseno", "Paradigma",
         "Solucion reutilizable a un problema recurrente de diseno de software."),
        ("OperadorDelLenguaje", "Language operator", "Operador del lenguaje", "Concepto",
         "Simbolo que representa una operacion sobre uno o varios operandos."),
        ("CaracteristicaDelLenguaje", "Language feature", "Caracteristica del lenguaje", "Concepto",
         "Elemento sintactico o semantico propio del lenguaje Python."),
        ("ConceptoDeConcurrencia", "Concurrency concept", "Concepto de concurrencia", "Concepto",
         "Concepto relacionado con la ejecucion concurrente o paralela."),
        ("ConceptoDeTipado", "Typing concept", "Concepto de tipado", "Concepto",
         "Concepto relativo al sistema de tipos y a las anotaciones de tipo."),
        ("HerramientaDeDesarrollo", "Development tool", "Herramienta de desarrollo", "Concepto",
         "Herramienta de apoyo al desarrollo (empaquetado, entornos, pruebas)."),
        ("ConceptoDePruebas", "Testing concept", "Concepto de pruebas", "Concepto",
         "Concepto relacionado con la verificacion y las pruebas del codigo."),
    ]
    for local, en, es, parent, comment in nuevas_clases:
        c = CFKG[local]
        g.add((c, RDF.type, OWL.Class))
        g.add((c, RDFS.label, L(en, EN)))
        g.add((c, RDFS.label, L(es, ES)))
        g.add((c, RDFS.subClassOf, CFKG[parent]))
        g.add((c, RDFS.comment, L(comment, ES)))

    # Alineamiento de clases con vocabularios externos (schema.org / FOAF)
    g.add((CFKG.Recurso, RDFS.subClassOf, SCHEMA.LearningResource))
    g.add((CFKG.Estudiante, RDFS.subClassOf, FOAF.Person))

    # 2.2  DISJUNCIONES (>=6) entre clases hoja de Concepto mutuamente excluyentes
    disj_pairs = [
        ("EstructuraDeControl", "EstructuraDeDatos"),
        ("EstructuraDeControl", "TipoDeDato"),
        ("EstructuraDeControl", "ModuloLibreria"),
        ("EstructuraDeDatos", "TipoDeDato"),
        ("EstructuraDeDatos", "ModuloLibreria"),
        ("TipoDeDato", "ModuloLibreria"),
        ("FuncionIntegrada", "TipoDeDato"),
        ("FuncionIntegrada", "EstructuraDeControl"),
        ("Paradigma", "TipoDeDato"),
        ("Paradigma", "EstructuraDeDatos"),
    ]
    for a, b in disj_pairs:
        g.add((CFKG[a], OWL.disjointWith, CFKG[b]))

    # 2.3  Nuevas PROPIEDADES DE OBJETO (>=5 para llegar a >=26)
    def objprop(local, en, es, dom, rng, comment=None, sub=None, types=None):
        p = CFKG[local]
        g.add((p, RDF.type, OWL.ObjectProperty))
        for t in (types or []):
            g.add((p, RDF.type, t))
        g.add((p, RDFS.label, L(en, EN)))
        g.add((p, RDFS.label, L(es, ES)))
        g.add((p, RDFS.domain, CFKG[dom]))
        g.add((p, RDFS.range, CFKG[rng]))
        if comment:
            g.add((p, RDFS.comment, L(comment, ES)))
        if sub:
            g.add((p, RDFS.subPropertyOf, CFKG[sub]))
        return p

    objprop("cubiertoPorEjercicio", "is covered by exercise", "es cubierto por el ejercicio",
            "Concepto", "Ejercicio", "Inversa de cubreConcepto.")
    g.add((CFKG.cubiertoPorEjercicio, OWL.inverseOf, CFKG.cubreConcepto))

    objprop("ilustradoEnRecurso", "is illustrated in resource", "se ilustra en el recurso",
            "Concepto", "Recurso", "Inversa de ilustraConcepto.")
    g.add((CFKG.ilustradoEnRecurso, OWL.inverseOf, CFKG.ilustraConcepto))

    objprop("esVarianteDe", "is a variant of", "es una variante de", "Concepto", "Concepto",
            "Relacion simetrica entre variantes sintacticas o conceptuales de una misma idea.",
            sub="relacionadoConceptualmenteCon", types=[OWL.SymmetricProperty])

    objprop("dependeDe", "depends on", "depende de", "Concepto", "Concepto",
            "Dependencia conceptual generica y transitiva entre conceptos.",
            sub="relacionadoConceptualmenteCon", types=[OWL.TransitiveProperty])

    objprop("introduceConcepto", "introduces concept", "introduce el concepto", "Tema", "Concepto",
            "Un tema curricular introduce (presenta por primera vez) un concepto.")

    # Reforzar perfil: generaliza/especializa transitivas (generalizacion es transitiva)
    g.add((CFKG.generaliza, RDF.type, OWL.TransitiveProperty))
    g.add((CFKG.especializa, RDF.type, OWL.TransitiveProperty))

    # 2.4  Nuevas PROPIEDADES DE DATOS (>=3 para llegar a >=10) + 2a funcional
    def dataprop(local, en, es, dom, rng, comment=None, types=None):
        p = CFKG[local]
        g.add((p, RDF.type, OWL.DatatypeProperty))
        for t in (types or []):
            g.add((p, RDF.type, t))
        g.add((p, RDFS.label, L(en, EN)))
        g.add((p, RDFS.label, L(es, ES)))
        g.add((p, RDFS.domain, CFKG[dom]))
        g.add((p, RDFS.range, rng))
        if comment:
            g.add((p, RDFS.comment, L(comment, ES)))
        return p

    dataprop("introducidoEnVersion", "introduced in version", "introducido en la version",
             "Concepto", XSD.string, "Version de Python que introdujo la caracteristica (p. ej. '3.10').",
             types=[OWL.FunctionalProperty])
    dataprop("tieneComplejidadTemporal", "has time complexity", "tiene complejidad temporal",
             "Concepto", XSD.string, "Complejidad temporal en notacion O grande (p. ej. 'O(log n)').")
    dataprop("tieneURLDocumentacion", "has documentation URL", "tiene URL de documentacion",
             "Concepto", XSD.anyURI, "Enlace a la documentacion oficial del concepto.")
    dataprop("tienePalabraClave", "has keyword", "tiene palabra clave",
             "Concepto", XSD.string, "Termino de busqueda o palabra clave asociada al concepto.")

    # 2.5  SKOS: broader subPropertyOf broaderTransitive
    g.add((SKOS.broader, RDFS.subPropertyOf, SKOS.broaderTransitive))

    # 2.6  RESTRICCIONES OWL 2 RL-safe (>=10):
    #      universales (allValuesFrom) y de cardinalidad maxima cualificada (<=1)
    def restr_all(cls, prop, filler):
        r = BNode()
        g.add((r, RDF.type, OWL.Restriction))
        g.add((r, OWL.onProperty, CFKG[prop]))
        g.add((r, OWL.allValuesFrom, CFKG[filler]))
        g.add((CFKG[cls], RDFS.subClassOf, r))

    def restr_maxqc1(cls, prop, oncls):
        r = BNode()
        g.add((r, RDF.type, OWL.Restriction))
        g.add((r, OWL.onProperty, CFKG[prop]))
        g.add((r, OWL.maxQualifiedCardinality, Literal(1, datatype=XSD.nonNegativeInteger)))
        g.add((r, OWL.onClass, CFKG[oncls]))
        g.add((CFKG[cls], RDFS.subClassOf, r))

    restr_all("ErrorConceptual", "errorSobreConcepto", "Concepto")
    restr_all("Ejercicio", "cubreConcepto", "Concepto")
    restr_all("EnvioEstudiante", "manifiestaError", "ErrorConceptual")
    restr_all("Concepto", "perteneceATema", "Tema")
    restr_all("Concepto", "requierePrerrequisito", "Concepto")
    restr_all("EvaluacionDeConcepto", "sobreConcepto", "Concepto")
    restr_all("EvaluacionActividad", "porEstudiante", "Estudiante")
    restr_all("Recurso", "ilustraConcepto", "Concepto")
    restr_all("Estudiante", "dominaConcepto", "Concepto")
    restr_maxqc1("EnvioEstudiante", "resuelveEjercicio", "Ejercicio")
    restr_maxqc1("EvaluacionActividad", "evaluaA", "Ejercicio")
    restr_maxqc1("EvaluacionDeConcepto", "enEjercicio", "Ejercicio")

    # 2.7  CONCEPTOS NUEVOS
    for c in NUEVOS:
        s = CFR[c["id"]]
        g.add((s, RDF.type, CFKG[c["tipo"]]))
        g.add((s, RDFS.label, L(c["en"], EN)))
        g.add((s, RDFS.label, L(c["es"], ES)))
        g.add((s, CFKG.perteneceATema, CFR[c["tema"]]))
        g.add((s, CFKG.tieneDificultad, Literal(c["dif"], datatype=XSD.integer)))
        g.add((s, CFKG.aNivelDominio, CFR[c["nivel"]]))
        for pr in c.get("prereq", []):
            g.add((s, CFKG.requierePrerrequisito, CFR[pr]))
        if c.get("wd"):
            g.add((s, SKOS.exactMatch, WD[c["wd"]]))
        if c.get("dbr"):
            g.add((s, SKOS.closeMatch, DBR[c["dbr"]]))
        if c.get("broader"):
            g.add((s, SKOS.broader, CFR[c["broader"]]))
            g.add((CFR[c["broader"]], SKOS.narrower, s))
        for rel in c.get("related", []):
            g.add((s, SKOS.related, CFR[rel]))
        if c.get("version"):
            g.add((s, CFKG.introducidoEnVersion, Literal(c["version"], datatype=XSD.string)))
        if c.get("big_o"):
            g.add((s, CFKG.tieneComplejidadTemporal, Literal(c["big_o"], datatype=XSD.string)))
        if c.get("url"):
            g.add((s, CFKG.tieneURLDocumentacion, Literal(c["url"], datatype=XSD.anyURI)))

    # 2.8  SKOS definition / scopeNote / example PARA TODOS LOS CONCEPTOS
    # Existentes
    for name, (d, s_, e) in C.items():
        s = CFR[name]
        g.add((s, SKOS.definition, L(d, ES)))
        g.add((s, SKOS.scopeNote, L(s_, ES)))
        g.add((s, SKOS.example, Literal(e)))
    # Nuevos
    for c in NUEVOS:
        s = CFR[c["id"]]
        g.add((s, SKOS.definition, L(c["d"], ES)))
        g.add((s, SKOS.scopeNote, L(c["s"], ES)))
        g.add((s, SKOS.example, Literal(c["e"])))

    # 2.9  Alineamientos externos adicionales y enriquecimiento SKOS de
    #      conceptos EXISTENTES (DBpedia closeMatch, complejidad, versiones,
    #      URLs de documentacion, broader/narrower/related extra).
    dbpedia = {
        "recursion": "Recursion_(computer_science)", "iterador": "Iterator",
        "generador": "Generator_(computer_programming)", "closure": "Closure_(computer_programming)",
        "funcion_orden_superior": "Higher-order_function", "tupla": "Tuple",
        "lista": "List_(abstract_data_type)", "diccionario": "Associative_array",
        "conjunto": "Set_(abstract_data_type)", "tabla_hash": "Hash_table",
        "grafo_estr": "Graph_(abstract_data_type)", "arbol_estr": "Tree_(data_structure)",
        "pila": "Stack_(abstract_data_type)", "cola": "Queue_(abstract_data_type)",
        "heap": "Heap_(data_structure)", "bfs": "Breadth-first_search", "dfs": "Depth-first_search",
        "busqueda_binaria": "Binary_search_algorithm", "busqueda_lineal": "Linear_search",
        "ordenacion_burbuja": "Bubble_sort", "ordenacion_mezcla": "Merge_sort",
        "ordenacion_rapida": "Quicksort", "notacion_o": "Big_O_notation",
        "complejidad": "Time_complexity", "herencia": "Inheritance_(object-oriented_programming)",
        "polimorfismo": "Polymorphism_(computer_science)", "encapsulacion": "Encapsulation_(computer_programming)",
        "clase": "Class_(computer_programming)", "objeto": "Object_(computer_science)",
        "decorador": "Python_syntax_and_semantics", "funcion_lambda": "Anonymous_function",
        "regex": "Regular_expression", "gil": "Global_interpreter_lock",
        "comprension_listas": "List_comprehension", "excepcion": "Exception_handling",
        "python": "Python_(programming_language)", "json_mod": "JSON", "csv_mod": "Comma-separated_values",
        "hilos": "Thread_(computing)", "multiproceso": "Process_(computing)",
        "prog_dinamica": "Dynamic_programming", "memoizacion": "Memoization",
        "mutabilidad": "Immutable_object", "backtracking": "Backtracking",
        "herencia_multiple": "Multiple_inheritance", "mixin": "Mixin",
        "anotaciones_tipo": "Type_signature", "ambito": "Scope_(computer_science)",
        "variable": "Variable_(computer_science)", "recursion_cola": "Tail_call",
    }
    for name, res in dbpedia.items():
        g.add((CFR[name], SKOS.closeMatch, DBR[res]))

    # Wikidata adicional.
    wikidata_extra = {
        "json_mod": "Q2063",                # JSON
        "hilos": "Q213092",                 # thread (computing)
        "pila": "Q177929",                  # stack (abstract data type)
        "cola": "Q220543",                  # queue (abstract data type)
        "funcion_orden_superior": "Q1474542",  # higher-order function
        "corrutina": "Q1339231",            # coroutine
        "enum_tipo": "Q760170",             # enumerated type
        "recursion_cola": "Q1340959",       # tail recursion
    }
    for name, qid in wikidata_extra.items():
        g.add((CFR[name], SKOS.exactMatch, WD[qid]))

    # Complejidad temporal en estructuras/algoritmos existentes
    big_o = {
        "busqueda_binaria": "O(log n)", "busqueda_lineal": "O(n)",
        "ordenacion_burbuja": "O(n^2)", "ordenacion_mezcla": "O(n log n)",
        "ordenacion_rapida": "O(n log n)", "tabla_hash": "O(1)",
        "diccionario": "O(1)", "conjunto": "O(1)", "lista": "O(n)",
        "heap": "O(log n)", "bfs": "O(V + E)", "dfs": "O(V + E)",
    }
    for name, o in big_o.items():
        g.add((CFR[name], CFKG.tieneComplejidadTemporal, Literal(o, datatype=XSD.string)))

    # Version de introduccion en conceptos existentes
    versiones = {
        "fstring": "3.6", "walrus": "3.8", "match_case": "3.10", "dataclass": "3.7",
        "async_await": "3.5", "typing_generics": "3.5", "typing_optional": "3.5",
        "typing_union": "3.5", "anotaciones_tipo": "3.5", "yield_from": "3.3",
    }
    for name, v in versiones.items():
        g.add((CFR[name], CFKG.introducidoEnVersion, Literal(v, datatype=XSD.string)))

    # URLs de documentacion oficial en modulos existentes
    urls = {
        "json_mod": "https://docs.python.org/3/library/json.html",
        "csv_mod": "https://docs.python.org/3/library/csv.html",
        "itertools_mod": "https://docs.python.org/3/library/itertools.html",
        "collections_mod": "https://docs.python.org/3/library/collections.html",
        "asyncio_mod": "https://docs.python.org/3/library/asyncio.html",
        "pathlib": "https://docs.python.org/3/library/pathlib.html",
        "unittest_mod": "https://docs.python.org/3/library/unittest.html",
        "regex": "https://docs.python.org/3/library/re.html",
        "modulo_datetime": "https://docs.python.org/3/library/datetime.html",
        "modulo_math": "https://docs.python.org/3/library/math.html",
    }
    for name, u in urls.items():
        g.add((CFR[name], CFKG.tieneURLDocumentacion, Literal(u, datatype=XSD.anyURI)))

    # Reforzar la red SKOS (broader/narrower/related) entre conceptos existentes
    skos_broader = [
        ("metodo_clase", "metodo"), ("metodo_estatico", "metodo"), ("init_method", "metodo"),
        ("herencia_multiple", "herencia"), ("recursion_cola", "recursion"),
        ("comprension_dicts", "comprension_listas"), ("comprension_sets", "comprension_listas"),
        ("expresion_generadora", "comprension_listas"), ("slicing", "indexacion"),
        ("slicing_str", "slicing"), ("indexacion_negativa", "indexacion"),
        ("pila", "lista"), ("cola", "lista"), ("ordenacion_burbuja", "notacion_o"),
        ("ordenacion_mezcla", "notacion_o"), ("ordenacion_rapida", "notacion_o"),
        ("bfs", "grafo_estr"), ("dfs", "grafo_estr"), ("encadenar_excepciones", "jerarquia_excepciones"),
        ("excepcion_personalizada", "jerarquia_excepciones"), ("metodo_clase", "decorador"),
        ("propiedad", "decorador"), ("funcion_lambda", "funcion"), ("corrutina", "async_await"),
        ("tabla_hash", "diccionario"), ("counter", "diccionario"), ("defaultdict", "diccionario"),
        ("namedtuple", "tupla"), ("deque", "cola"),
    ]
    for nar, bro in skos_broader:
        g.add((CFR[nar], SKOS.broader, CFR[bro]))
        g.add((CFR[bro], SKOS.narrower, CFR[nar]))

    skos_related_extra = [
        ("fstring", "formato_str"), ("formato_str", "metodos_str"),
        ("map_func", "filter_func"), ("filter_func", "reduce_func"),
        ("any_all", "truthiness"), ("global_kw", "nonlocal_kw"),
        ("hilos", "gil"), ("multiproceso", "gil"), ("dataclass", "namedtuple"),
        ("enum_tipo", "clase"), ("conjunto", "frozenset_tipo"),
    ]
    for a, b in skos_related_extra:
        g.add((CFR[a], SKOS.related, CFR[b]))
        g.add((CFR[b], SKOS.related, CFR[a]))

    final = len(g)
    return g, inicial, final


def verificar(g):
    problemas = []
    # OWL-RL closure sobre una COPIA
    gc = Graph()
    for t in g:
        gc.add(t)
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(gc)

    nothing = set(gc.subjects(RDF.type, OWL.Nothing))
    sameas = list(gc.triples((None, OWL.sameAs, None)))
    sameas_no_reflex = [(s, o) for s, o in gc.subject_objects(OWL.sameAs) if s != o]
    concepto = set(gc.subjects(RDF.type, CFKG.Concepto))
    print(f"  cierre OWL-RL: {len(gc)} triples inferidos+afirmados")
    print(f"  owl:Nothing miembros (inferidos): {len(nothing)}")
    print(f"  owl:sameAs total en cierre: {len(sameas)} (reflexivos eq-ref); NO reflexivos: {len(sameas_no_reflex)}")
    print(f"  cfkg:Concepto inferidos: {len(concepto)}")
    if nothing:
        problemas.append(f"INCONSISTENCIA: {len(nothing)} miembros de owl:Nothing")
    if sameas_no_reflex:
        problemas.append(f"owl:sameAs NO reflexivos inferidos = {len(sameas_no_reflex)} (fusion indebida): {sameas_no_reflex[:5]}")
    if len(concepto) < 210:
        problemas.append(f"Conceptos inferidos {len(concepto)} < 210")

    # sameAs afirmados
    sa_assert = list(g.triples((None, OWL.sameAs, None)))
    if sa_assert:
        problemas.append(f"owl:sameAs afirmados = {len(sa_assert)} (debe ser 0)")

    # dominio/rango en TODAS las propiedades
    props = set(g.subjects(RDF.type, OWL.ObjectProperty)) | set(g.subjects(RDF.type, OWL.DatatypeProperty))
    for p in props:
        if (p, RDFS.domain, None) not in g:
            problemas.append(f"sin dominio: {p}")
        if (p, RDFS.range, None) not in g:
            problemas.append(f"sin rango: {p}")

    # cada concepto con definition + scopeNote + example
    leaf = ["TipoDeDato", "FuncionIntegrada", "EstructuraDeDatos", "ModuloLibreria",
            "EstructuraDeControl", "Paradigma", "PrincipioTransversal"]
    conc = set()
    for lf in leaf:
        conc |= set(g.subjects(RDF.type, CFKG[lf]))
    # incluir instancias de las nuevas subclases de Concepto via cierre
    conc |= concepto
    falt = []
    for s in conc:
        for pr in (SKOS.definition, SKOS.scopeNote, SKOS.example):
            if (s, pr, None) not in g:
                falt.append((str(s), str(pr).split("#")[-1]))
    if falt:
        problemas.append(f"{len(falt)} conceptos sin def/scope/example: {falt[:8]}")

    return problemas, len(concepto), len(gc)


def main():
    print(">> Construyendo CodeFeedback-KG v2.0 ...")
    g, ini, fin = build()
    print(f"  triples afirmados: {ini} -> {fin}")

    problemas, n_concepto, n_cierre = verificar(g)
    if problemas:
        print("\n!! PROBLEMAS DETECTADOS:")
        for p in problemas:
            print("   -", p)
        print("\nNo se serializa. Corrige el modelado.")
        sys.exit(1)

    # backup
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    bak = ONTO.with_suffix(ONTO.suffix + f".bak-{stamp}")
    if not bak.exists():
        shutil.copy2(ONTO, bak)
        print(f"  backup: {bak.name}")

    g.serialize(destination=str(ONTO), format="turtle", encoding="utf-8")
    print(f"  serializado: {ONTO}")
    print(f"  OK — conceptos inferidos: {n_concepto}; triples cierre: {n_cierre}")


if __name__ == "__main__":
    main()
