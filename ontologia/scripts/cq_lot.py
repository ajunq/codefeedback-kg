# -*- coding: utf-8 -*-
"""
cq_lot.py — Ejecuta las preguntas de competencia (CQ1..CQ14) de la
metodologia LOT contra el grafo v2.0. Las que requieren inferencia
(transitividad de prerrequisitos, skos:broaderTransitive, subsuncion de
subpropiedades) se evaluan sobre el cierre OWL-RL. Escribe el numero de
filas de cada CQ en salidas/cq-resultados.txt.
"""
from pathlib import Path
from rdflib import Graph
import owlrl

BASE = Path(__file__).resolve().parent.parent
ONTO = BASE / "ontologia" / "codefeedback-kg.ttl"
OUT = BASE / "salidas"

PREF = """
PREFIX cfkg: <https://w3id.org/codefeedback-kg/schema#>
PREFIX cfr:  <https://w3id.org/codefeedback-kg/id/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
"""

CQ = {
 "CQ1 Prerrequisitos (in)directos de la recursion": (True, """
   SELECT DISTINCT ?prereq WHERE { cfr:recursion cfkg:requierePrerrequisito+ ?prereq . }"""),
 "CQ2 Conceptos del tema POO": (False, """
   SELECT ?c WHERE { ?c cfkg:perteneceATema cfr:T_poo . }"""),
 "CQ3 Errores sobre conceptos avanzados": (False, """
   SELECT ?err ?c WHERE {
     ?err cfkg:errorSobreConcepto ?c . ?c cfkg:aNivelDominio cfr:avanzado . }"""),
 "CQ4 Conceptos con alineamiento Wikidata": (False, """
   SELECT ?c ?qid WHERE {
     ?c skos:exactMatch ?qid . FILTER(STRSTARTS(STR(?qid), "http://www.wikidata.org/")) }"""),
 "CQ5 Conceptos SIN ejemplo (debe ser 0)": (True, """
   SELECT ?c WHERE { ?c a cfkg:Concepto . FILTER NOT EXISTS { ?c skos:example ?e } }"""),
 "CQ6 Conceptos con mas prerrequisitos directos": (False, """
   SELECT ?c (COUNT(?p) AS ?n) WHERE { ?c cfkg:requierePrerrequisito ?p . }
   GROUP BY ?c ORDER BY DESC(?n) LIMIT 10"""),
 "CQ7 Pares de conceptos que contrastan (confusiones)": (False, """
   SELECT ?a ?b WHERE { ?a cfkg:contrastaCon ?b . FILTER(STR(?a) < STR(?b)) }"""),
 "CQ8 Ejercicios que cubren busqueda binaria y su dificultad": (False, """
   SELECT ?ej ?dif WHERE {
     ?ej cfkg:cubreConcepto cfr:busqueda_binaria ; cfkg:tieneDificultad ?dif . }"""),
 "CQ9 Recursos que ilustran un concepto": (False, """
   SELECT ?rec ?c WHERE { ?rec cfkg:ilustraConcepto ?c . }"""),
 "CQ10 Conceptos introducidos en Python 3.10": (False, """
   SELECT ?c ?v WHERE { ?c cfkg:introducidoEnVersion ?v . FILTER(?v = "3.10") }"""),
 "CQ11 Conceptos con complejidad O(log n)": (False, """
   SELECT ?c ?o WHERE { ?c cfkg:tieneComplejidadTemporal ?o . FILTER(CONTAINS(?o,"log")) }"""),
 "CQ12 Especializaciones (broaderTransitive) de comprension de listas": (True, """
   SELECT ?sub WHERE { ?sub skos:broaderTransitive cfr:comprension_listas . }"""),
 "CQ13 Envios que manifiestan un error y el concepto implicado": (False, """
   SELECT ?env ?err ?c WHERE {
     ?env cfkg:manifiestaError ?err . ?err cfkg:errorSobreConcepto ?c . }"""),
 "CQ14 Conceptos avanzados de concurrencia": (False, """
   SELECT ?c WHERE {
     ?c cfkg:perteneceATema cfr:T_concurrencia ; cfkg:aNivelDominio cfr:avanzado . }"""),
}


def main():
    OUT.mkdir(exist_ok=True)
    base = Graph(); base.parse(ONTO, format="turtle")
    cerr = Graph()
    for t in base:
        cerr.add(t)
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(cerr)

    lineas = ["Preguntas de competencia LOT — CodeFeedback-KG v2.0", ""]
    for nombre, (inf, q) in CQ.items():
        g = cerr if inf else base
        res = list(g.query(PREF + q))
        marca = " [cierre OWL-RL]" if inf else ""
        lineas.append(f"{nombre}{marca}: {len(res)} filas")
        print(f"{nombre}{marca}: {len(res)} filas")
    (OUT / "cq-resultados.txt").write_text("\n".join(lineas), encoding="utf-8")


if __name__ == "__main__":
    main()
