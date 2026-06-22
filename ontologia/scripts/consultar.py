import sys
from pathlib import Path
from rdflib import Graph
import owlrl

BASE = Path(__file__).resolve().parent.parent
ONTO = BASE / "ontologia" / "codefeedback-kg-150.ttl"
CONS = BASE / "consultas"
OUT = BASE / "salidas"

# 08 requiere red (SERVICE a Wikidata); 09 es una operación de ESCRITURA
# (INSERT/DELETE), no una consulta de lectura, y no la ejecuta este script.
SKIP = {"08_federada_wikidata.rq", "09_update_depuracion.rq"}


def cargar(inferir):
    g = Graph()
    try:
        g.parse(ONTO, format="turtle")
    except (OSError, SyntaxError, ValueError) as e:
        print(f"Error al leer/parsear la ontologia {ONTO}: {e}", file=sys.stderr)
        sys.exit(1)
    if inferir:
        owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
    return g


def formato_select(res):
    cols = [str(v) for v in res.vars]
    filas = [[("" if row[v] is None else str(row[v])) for v in res.vars] for row in res]
    return cols, filas


def main():
    inferir = "--sin-inferencia" not in sys.argv
    g = cargar(inferir)
    modo = "con inferencia OWL-RL" if inferir else "sin inferencia (NONE)"
    out = [f"Resultados de consultas SPARQL — {modo} — {len(g)} triples", ""]

    for archivo in sorted(CONS.glob("*.rq")):
        if archivo.name in SKIP:
            continue
        try:
            consulta = archivo.read_text(encoding="utf-8")
        except OSError as e:
            print(f"Error al leer la consulta {archivo}: {e}", file=sys.stderr)
            sys.exit(1)
        res = g.query(consulta)
        out.append("=" * 72)
        out.append(archivo.name)
        out.append("=" * 72)
        if res.type == "CONSTRUCT":
            cg = Graph()
            for t in res:
                cg.add(t)
            out.append(f"[CONSTRUCT] {len(cg)} triples generados")
        else:
            cols, filas = formato_select(res)
            out.append(" | ".join(cols))
            out.append("-" * 72)
            out.extend(" | ".join(f) for f in filas)
            out.append(f"({len(filas)} filas)")
        out.append("")

    texto = "\n".join(out)
    sufijo = "inferido" if inferir else "base"
    (OUT / f"resultados-consultas-{sufijo}.txt").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
