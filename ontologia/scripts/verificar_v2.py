# -*- coding: utf-8 -*-
"""
verificar_v2.py — Verificacion integral de CodeFeedback-KG v2.0.

1) Parsea codefeedback-kg.ttl (v2.0) con rdflib.
2) Ejecuta el cierre OWL-RL y comprueba CONSISTENCIA (sin owl:Nothing,
   sin owl:sameAs no reflexivo) e informa de triples afirmados/inferidos
   y del numero de cfkg:Concepto inferidos.
3) Ejecuta SHACL (pyshacl, inferencia RDFS) con shapes-codefeedback-kg.ttl
   sobre el grafo valido  -> debe Conforms:True.
4) Ejecuta SHACL sobre el grafo + ejemplo-invalido.ttl -> violaciones > 0.

No modifica ningun fichero de ontologia; solo escribe informes en salidas/.
"""
import sys
from pathlib import Path
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, OWL, SH
import owlrl
from pyshacl import validate

BASE = Path(__file__).resolve().parent.parent
ONTO = BASE / "ontologia" / "codefeedback-kg.ttl"
SHAPES = BASE / "ontologia" / "shapes-codefeedback-kg.ttl"
INVALID = BASE / "ontologia" / "ejemplo-invalido.ttl"
OUT = BASE / "salidas"
CFKG = "https://w3id.org/codefeedback-kg/schema#"


def main():
    OUT.mkdir(exist_ok=True)
    ok = True

    # 1) parse
    g = Graph()
    g.parse(ONTO, format="turtle")
    asserted = len(g)
    print(f"[1] rdflib parse OK — triples afirmados: {asserted}")

    # 2) OWL-RL closure + consistencia
    gc = Graph()
    for t in g:
        gc.add(t)
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(gc)
    total = len(gc)
    nothing = set(gc.subjects(RDF.type, OWL.Nothing))
    sameas_nr = [(s, o) for s, o in gc.subject_objects(OWL.sameAs) if s != o]
    concepto = set(gc.subjects(RDF.type, URIRef(CFKG + "Concepto")))
    print(f"[2] OWL-RL cierre — afirmados: {asserted} | inferidos: {total - asserted} | total: {total}")
    print(f"    owl:Nothing: {len(nothing)} | owl:sameAs no reflexivo: {len(sameas_nr)}")
    print(f"    cfkg:Concepto inferidos: {len(concepto)}")
    consistente = (len(nothing) == 0 and len(sameas_nr) == 0)
    print(f"    CONSISTENTE: {consistente}")
    if not consistente or len(concepto) < 210:
        ok = False

    # 3) SHACL sobre grafo valido
    conforms, rg, rep = validate(str(ONTO), shacl_graph=str(SHAPES),
                                 inference="rdfs", advanced=True)
    n_shapes = len(set(Graph().parse(str(SHAPES), format="turtle").subjects(RDF.type, SH.NodeShape)))
    (OUT / "informe-shacl-v2.txt").write_text(rep, encoding="utf-8")
    nv = len(set(rg.subjects(SH.resultMessage, None)))
    print(f"[3] SHACL grafo valido — Conforms: {conforms} (violaciones: {nv}) | formas: {n_shapes}")
    if not conforms:
        ok = False

    # 4) SHACL sobre grafo + ejemplo invalido
    g2 = Graph()
    g2.parse(ONTO, format="turtle")
    g2.parse(INVALID, format="turtle")
    conf2, rg2, rep2 = validate(g2, shacl_graph=str(SHAPES),
                                inference="rdfs", advanced=True)
    (OUT / "informe-shacl-v2-invalido.txt").write_text(rep2, encoding="utf-8")
    nv2 = len(set(rg2.subjects(SH.resultMessage, None)))
    print(f"[4] SHACL grafo + ejemplo-invalido — Conforms: {conf2} (violaciones: {nv2})")
    if conf2 or nv2 == 0:
        ok = False

    print(f"\nRESULTADO GLOBAL: {'OK' if ok else 'FALLO'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
