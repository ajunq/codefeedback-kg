import sys
from pathlib import Path
from rdflib import Graph
import owlrl

BASE = Path(__file__).resolve().parent.parent
ONTO = BASE / "ontologia" / "codefeedback-kg-150.ttl"
OUT = BASE / "salidas"


def main():
    OUT.mkdir(exist_ok=True)
    g = Graph()
    try:
        g.parse(ONTO, format="turtle")
    except (OSError, SyntaxError, ValueError) as e:
        print(f"Error al leer/parsear la ontologia {ONTO}: {e}", file=sys.stderr)
        sys.exit(1)
    asserted = len(g)

    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
    total = len(g)

    destino = OUT / "codefeedback-kg-inferido.ttl"
    try:
        g.serialize(destination=str(destino), format="turtle", encoding="utf-8")
    except (OSError, ValueError) as e:
        print(f"Error al serializar {destino}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Triples afirmados : {asserted}")
    print(f"Triples inferidos : {total - asserted}")
    print(f"Triples totales   : {total}")
    print(f"Grafo con cierre OWL-RL escrito en: {destino}")


if __name__ == "__main__":
    main()
