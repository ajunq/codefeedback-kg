import sys
from pathlib import Path
from rdflib import Graph

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
    for fmt, ext in [("json-ld", "jsonld"), ("nt", "nt"), ("xml", "rdf")]:
        destino = OUT / f"codefeedback-kg.{ext}"
        try:
            g.serialize(destination=str(destino), format=fmt, encoding="utf-8")
        except (OSError, ValueError) as e:
            print(f"Error al serializar {destino} en formato {fmt}: {e}", file=sys.stderr)
            sys.exit(1)
        print(f"{fmt:10} -> {destino.name}")
    print(f"{len(g)} triples exportados en cada formato.")


if __name__ == "__main__":
    main()
