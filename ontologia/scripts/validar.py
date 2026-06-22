import sys
from pathlib import Path
from rdflib import Graph
from rdflib.namespace import SH
from pyshacl import validate

BASE = Path(__file__).resolve().parent.parent
ONTO = BASE / "ontologia" / "codefeedback-kg.ttl"
ONTO150 = BASE / "ontologia" / "codefeedback-kg-150.ttl"
SHAPES = BASE / "ontologia" / "shapes-ekg.ttl"
INVALID = BASE / "ontologia" / "ejemplo-invalido.ttl"
OUT = BASE / "salidas"


def run(data_graph, etiqueta, destino):
    conforms, results_graph, report_text = validate(
        data_graph,
        shacl_graph=str(SHAPES),
        inference="rdfs",
        advanced=True,
    )
    destino.write_text(report_text, encoding="utf-8")
    estado = "CONFORME" if conforms else "NO CONFORME"
    n = len(set(results_graph.subjects(SH.resultMessage, None)))
    print(f"[{etiqueta}] {estado}  (violaciones: {n})  -> {destino.name}")
    return conforms


def main():
    OUT.mkdir(exist_ok=True)

    g = Graph()
    g.parse(ONTO, format="turtle")
    ok = run(g, "Grafo principal", OUT / "informe-shacl.txt")

    g2 = Graph()
    g2.parse(ONTO, format="turtle")
    g2.parse(INVALID, format="turtle")
    run(g2, "Grafo + ejemplo invalido", OUT / "informe-shacl-invalido.txt")

    ok150 = True
    if ONTO150.exists():
        g150 = Graph()
        g150.parse(ONTO150, format="turtle")
        ok150 = run(g150, "Grafo ampliado (150 conceptos)", OUT / "informe-shacl-150.txt")

    sys.exit(0 if (ok and ok150) else 1)


if __name__ == "__main__":
    main()
