"""Análisis del estado actual del grafo v2.0 (diagnóstico, no destructivo)."""
import sys
from pathlib import Path
from collections import defaultdict
from rdflib import Graph, RDF, RDFS, OWL, URIRef
import owlrl

BASE = Path(__file__).resolve().parent.parent
ONTO = BASE / "ontologia" / "codefeedback-kg.ttl"
SKOS = "http://www.w3.org/2004/02/skos/core#"
CFKG = "https://w3id.org/codefeedback-kg/schema#"

g = Graph()
g.parse(ONTO, format="turtle")
asserted = len(g)
print("asserted triples:", asserted)

def n(pred, obj):
    return len(list(g.subjects(pred, obj)))

print("owl:Class:", len(set(g.subjects(RDF.type, OWL.Class))))
print("owl:ObjectProperty:", len(set(g.subjects(RDF.type, OWL.ObjectProperty))))
print("owl:DatatypeProperty:", len(set(g.subjects(RDF.type, OWL.DatatypeProperty))))
print("rdfs:subClassOf triples:", len(list(g.triples((None, RDFS.subClassOf, None)))))
print("owl:TransitiveProperty:", len(set(g.subjects(RDF.type, OWL.TransitiveProperty))))
print("owl:SymmetricProperty:", len(set(g.subjects(RDF.type, OWL.SymmetricProperty))))
print("owl:FunctionalProperty:", len(set(g.subjects(RDF.type, OWL.FunctionalProperty))))
print("owl:Restriction:", len(set(g.subjects(RDF.type, OWL.Restriction))))
print("owl:disjointWith:", len(list(g.triples((None, OWL.disjointWith, None)))))
print("owl:inverseOf:", len(list(g.triples((None, OWL.inverseOf, None)))))
print("owl:sameAs:", len(list(g.triples((None, OWL.sameAs, None)))))
for p in ["broader","narrower","related","exactMatch","closeMatch","definition","scopeNote","example"]:
    print(f"skos:{p}:", len(list(g.triples((None, URIRef(SKOS+p), None)))))

# concept leaf classes
leafs = ["TipoDeDato","FuncionIntegrada","EstructuraDeDatos","ModuloLibreria",
         "EstructuraDeControl","Paradigma","PrincipioTransversal"]
leaf_uris = [URIRef(CFKG+c) for c in leafs]
concept_individuals = set()
typed = defaultdict(list)
for lu in leaf_uris:
    for s in g.subjects(RDF.type, lu):
        concept_individuals.add(s)
        typed[s].append(str(lu).split("#")[1])
print("\nconcept individuals (direct leaf typing):", len(concept_individuals))

# double-typed individuals (disjointness risk)
dbl = {s:ts for s,ts in typed.items() if len(ts) > 1}
print("double-leaf-typed individuals:", len(dbl))
for s,ts in dbl.items():
    print("   ", s, ts)

# OWL-RL inferred Concepto count
g2 = Graph(); g2.parse(ONTO, format="turtle")
owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g2)
concepto = set(g2.subjects(RDF.type, URIRef(CFKG+"Concepto")))
print("inferred cfkg:Concepto:", len(concepto))
print("inferred owl:Nothing members:", len(set(g2.subjects(RDF.type, OWL.Nothing))))

# properties missing domain/range
allprops = set(g.subjects(RDF.type, OWL.ObjectProperty)) | set(g.subjects(RDF.type, OWL.DatatypeProperty))
miss_d = [str(p).split("#")[-1] for p in allprops if (p, RDFS.domain, None) not in g]
miss_r = [str(p).split("#")[-1] for p in allprops if (p, RDFS.range, None) not in g]
print("missing domain:", sorted(miss_d))
print("missing range:", sorted(miss_r))

# concepts missing def/scope/example
defp=URIRef(SKOS+"definition"); scp=URIRef(SKOS+"scopeNote"); exp=URIRef(SKOS+"example")
miss_def=[s for s in concept_individuals if (s,defp,None) not in g]
print("concepts missing skos:definition:", len(miss_def))

# dump concept list with type for authoring
out = BASE/"salidas"/"_conceptos_actuales.txt"
lines=[]
for s in sorted(concept_individuals, key=str):
    local=str(s).split("/")[-1]
    labels=[str(o) for o in g.objects(s, RDFS.label)]
    lines.append(f"{local}\t{typed[s][0]}\t{' | '.join(labels)}")
out.write_text("\n".join(lines), encoding="utf-8")
print("wrote", out, len(lines), "concepts")
