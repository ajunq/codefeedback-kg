# -*- coding: utf-8 -*-
"""
reporte_v2.py — Re-deriva CADA dimension del objetivo §10 sobre el grafo
final v2.0 (y sobre la v1.0 congelada -150) y emite:
    salidas/v2-target-report.md
    salidas/v2-target-report.json
Incluye el recuento del cierre OWL-RL y el resultado SHACL. Marca con
honestidad PASS/FAIL cada dimension (no se rebaja ningun objetivo).
"""
import json
from pathlib import Path
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS, OWL, SH, SKOS
import owlrl
from pyshacl import validate

BASE = Path(__file__).resolve().parent.parent
V2 = BASE / "ontologia" / "codefeedback-kg.ttl"
V1 = BASE / "ontologia" / "codefeedback-kg-150.ttl"
SHAPES = BASE / "ontologia" / "shapes-codefeedback-kg.ttl"
INVALID = BASE / "ontologia" / "ejemplo-invalido.ttl"
OUT = BASE / "salidas"
CFKG = "https://w3id.org/codefeedback-kg/schema#"
C = lambda n: URIRef(CFKG + n)
LEAF = ["TipoDeDato", "FuncionIntegrada", "EstructuraDeDatos", "ModuloLibreria",
        "EstructuraDeControl", "Paradigma", "PrincipioTransversal"]


def load(p):
    g = Graph()
    g.parse(p, format="turtle")
    return g


def concepto_inferido(g):
    gc = Graph()
    for t in g:
        gc.add(t)
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(gc)
    n = len(set(gc.subjects(RDF.type, C("Concepto"))))
    nothing = len(set(gc.subjects(RDF.type, OWL.Nothing)))
    sa_nr = len([1 for s, o in gc.subject_objects(OWL.sameAs) if s != o])
    return n, len(gc), len(g), nothing, sa_nr


def props_missing(g):
    props = set(g.subjects(RDF.type, OWL.ObjectProperty)) | set(g.subjects(RDF.type, OWL.DatatypeProperty))
    md = sum(1 for p in props if (p, RDFS.domain, None) not in g)
    mr = sum(1 for p in props if (p, RDFS.range, None) not in g)
    return md, mr


def conceptos_directos(g):
    s = set()
    for lf in LEAF:
        s |= set(g.subjects(RDF.type, C(lf)))
    return s


def cobertura_skos(g):
    # conceptos (inferencia leaf directa + nuevas subclases via cierre rdfs no necesario:
    # usamos cierre OWL-RL para el conjunto completo)
    gc = Graph()
    for t in g:
        gc.add(t)
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(gc)
    conc = set(gc.subjects(RDF.type, C("Concepto")))
    completos = 0
    for c in conc:
        if (c, SKOS.definition, None) in g and (c, SKOS.scopeNote, None) in g and (c, SKOS.example, None) in g:
            completos += 1
    return completos, len(conc)


def vocabularios(g):
    vocs = set()
    for _, o in g.subject_objects(SKOS.exactMatch):
        if str(o).startswith("http://www.wikidata.org/"):
            vocs.add("Wikidata")
    for _, o in g.subject_objects(SKOS.closeMatch):
        if str(o).startswith("http://dbpedia.org/"):
            vocs.add("DBpedia")
    # schema.org (uso/alineamiento de clases)
    if any("schema.org" in str(o) for o in g.objects(None, RDFS.subClassOf)) or \
       any("schema.org" in str(o) for o in g.objects(None, RDF.type)):
        vocs.add("schema.org")
    if (None, URIRef("http://purl.org/dc/terms/title"), None) in g or \
       (None, URIRef("http://purl.org/dc/terms/creator"), None) in g:
        vocs.add("DCTerms")
    if any("xmlns.com/foaf" in str(o) for o in g.objects(None, RDF.type)) or \
       any("xmlns.com/foaf" in str(o) for o in g.objects(None, RDFS.subClassOf)):
        vocs.add("FOAF")
    return sorted(vocs)


def ontology_header(g):
    onto = URIRef(CFKG)
    needed = [DCT("title"), DCT("creator"), DCT("license"), DCT("description"),
              OWL.versionInfo, OWL.versionIRI]
    present = all((onto, p, None) in g for p in needed)
    vi = list(g.objects(onto, OWL.versionInfo))
    return present, (str(vi[0]) if vi else None)


def DCT(x):
    return URIRef("http://purl.org/dc/terms/" + x)


def metrics(g):
    return {
        "owl:Class": len(set(g.subjects(RDF.type, OWL.Class))),
        "owl:ObjectProperty": len(set(g.subjects(RDF.type, OWL.ObjectProperty))),
        "owl:DatatypeProperty": len(set(g.subjects(RDF.type, OWL.DatatypeProperty))),
        "rdfs:subClassOf": len(list(g.triples((None, RDFS.subClassOf, None)))),
        "owl:TransitiveProperty": len(set(g.subjects(RDF.type, OWL.TransitiveProperty))),
        "owl:SymmetricProperty": len(set(g.subjects(RDF.type, OWL.SymmetricProperty))),
        "owl:FunctionalProperty": len(set(g.subjects(RDF.type, OWL.FunctionalProperty))),
        "owl:inverseOf": len(list(g.triples((None, OWL.inverseOf, None)))),
        "owl:disjointWith": len(list(g.triples((None, OWL.disjointWith, None)))),
        "owl:Restriction": len(set(g.subjects(RDF.type, OWL.Restriction))),
        "owl:sameAs": len(list(g.triples((None, OWL.sameAs, None)))),
        "skos:broader": len(list(g.triples((None, SKOS.broader, None)))),
        "skos:narrower": len(list(g.triples((None, SKOS.narrower, None)))),
        "skos:related": len(list(g.triples((None, SKOS.related, None)))),
        "skos:exactMatch(Wikidata)": len([1 for _, o in g.subject_objects(SKOS.exactMatch)
                                          if "wikidata.org" in str(o)]),
    }


def main():
    OUT.mkdir(exist_ok=True)
    g1, g2 = load(V1), load(V2)
    m1, m2 = metrics(g1), metrics(g2)
    c1, _, a1, _, _ = concepto_inferido(g1)
    c2, cierre2, a2, nothing2, sa2 = concepto_inferido(g2)
    md1, mr1 = props_missing(g1)
    md2, mr2 = props_missing(g2)
    cov2, nconc2 = cobertura_skos(g2)
    cov1, nconc1 = cobertura_skos(g1)
    voc1, voc2 = vocabularios(g1), vocabularios(g2)
    hdr2_ok, ver2 = ontology_header(g2)

    # SHACL
    n_shapes = len(set(load(SHAPES).subjects(RDF.type, SH.NodeShape)))
    conf, rg, rep = validate(str(V2), shacl_graph=str(SHAPES), inference="rdfs", advanced=True)
    nv = len(set(rg.subjects(SH.resultMessage, None)))
    g2inv = load(V2)
    g2inv.parse(INVALID, format="turtle")
    confI, rgI, _ = validate(g2inv, shacl_graph=str(SHAPES), inference="rdfs", advanced=True)
    nvI = len(set(rgI.subjects(SH.resultMessage, None)))

    # filas: (clave, v1, v2, objetivo, passfn, metodo)
    rows = []

    def add(dim, v1, v2, target, ok, metodo):
        rows.append({"dimension": dim, "v1.0": v1, "v2.0": v2, "target": target,
                     "PASS": bool(ok), "re-derivation": metodo})

    add("cfkg:Concepto (inferido OWL-RL)", c1, c2, ">=210", c2 >= 210,
        "owlrl DeductiveClosure; |{?s a cfkg:Concepto}|")
    add("triples afirmados", a1, a2, ">=2500", a2 >= 2500, "len(Graph) tras parse rdflib")
    add("owl:Class", m1["owl:Class"], m2["owl:Class"], ">=28", m2["owl:Class"] >= 28, "|{?s a owl:Class}|")
    add("owl:ObjectProperty", m1["owl:ObjectProperty"], m2["owl:ObjectProperty"], ">=26",
        m2["owl:ObjectProperty"] >= 26, "|{?s a owl:ObjectProperty}|")
    add("owl:DatatypeProperty", m1["owl:DatatypeProperty"], m2["owl:DatatypeProperty"], ">=10",
        m2["owl:DatatypeProperty"] >= 10, "|{?s a owl:DatatypeProperty}|")
    add("rdfs:subClassOf", m1["rdfs:subClassOf"], m2["rdfs:subClassOf"], ">=30",
        m2["rdfs:subClassOf"] >= 30, "|{?s rdfs:subClassOf ?o}|")
    add("owl:TransitiveProperty", m1["owl:TransitiveProperty"], m2["owl:TransitiveProperty"], ">=4",
        m2["owl:TransitiveProperty"] >= 4, "|{?s a owl:TransitiveProperty}|")
    add("owl:SymmetricProperty", m1["owl:SymmetricProperty"], m2["owl:SymmetricProperty"], ">=1",
        m2["owl:SymmetricProperty"] >= 1, "|{?s a owl:SymmetricProperty}|")
    add("owl:FunctionalProperty", m1["owl:FunctionalProperty"], m2["owl:FunctionalProperty"], ">=2",
        m2["owl:FunctionalProperty"] >= 2, "|{?s a owl:FunctionalProperty}|")
    add("owl:inverseOf (pares)", m1["owl:inverseOf"], m2["owl:inverseOf"], ">=4",
        m2["owl:inverseOf"] >= 4, "|{?s owl:inverseOf ?o}|")
    add("owl:disjointWith", m1["owl:disjointWith"], m2["owl:disjointWith"], ">=6",
        m2["owl:disjointWith"] >= 6, "|{?s owl:disjointWith ?o}|")
    add("owl:Restriction", m1["owl:Restriction"], m2["owl:Restriction"], ">=10",
        m2["owl:Restriction"] >= 10, "|{?s a owl:Restriction}|")
    add("propiedades sin dominio", md1, md2, "==0", md2 == 0, "props sin rdfs:domain")
    add("propiedades sin rango", mr1, mr2, "==0", mr2 == 0, "props sin rdfs:range")
    add("owl:Ontology header completo", "parcial", "completo" if hdr2_ok else "incompleto", "completo",
        hdr2_ok, "title/creator/license/description/versionInfo/versionIRI presentes")
    add("versionInfo", "1.0.0", ver2, "2.0.0", ver2 == "2.0.0", "owl:versionInfo del owl:Ontology")
    add("Formas SHACL", 10, n_shapes, ">=16", n_shapes >= 16, "|{?s a sh:NodeShape}| en shapes-codefeedback-kg.ttl")
    add("skos:broader", m1["skos:broader"], m2["skos:broader"], ">=30", m2["skos:broader"] >= 30, "|{?s skos:broader ?o}|")
    add("skos:narrower", m1["skos:narrower"], m2["skos:narrower"], ">=20", m2["skos:narrower"] >= 20, "|{?s skos:narrower ?o}|")
    add("skos:related", m1["skos:related"], m2["skos:related"], ">=20", m2["skos:related"] >= 20, "|{?s skos:related ?o}|")
    add("cobertura def+scopeNote+example", f"{cov1}/{nconc1}", f"{cov2}/{nconc2}", "==conceptos",
        cov2 == nconc2, "cada cfkg:Concepto con skos:definition+scopeNote+example")
    add("skos:exactMatch Wikidata", m1["skos:exactMatch(Wikidata)"], m2["skos:exactMatch(Wikidata)"], ">=40",
        m2["skos:exactMatch(Wikidata)"] >= 40, "exactMatch a wikidata.org (QIDs via API)")
    add("vocabularios externos alineados", len(voc1), f"{len(voc2)} ({', '.join(voc2)})", ">=4",
        len(voc2) >= 4, "Wikidata+DBpedia+schema.org+DCTerms(+FOAF)")
    add("owl:sameAs", m1["owl:sameAs"], m2["owl:sameAs"], "==0", m2["owl:sameAs"] == 0, "|{?s owl:sameAs ?o}| afirmados")
    add("OWL-RL consistencia (owl:Nothing)", "n/d", nothing2, "==0", nothing2 == 0, "miembros de owl:Nothing en el cierre")
    add("OWL-RL sin fusion (sameAs no reflex.)", "n/d", sa2, "==0", sa2 == 0, "owl:sameAs x!=y en el cierre")
    add("SHACL Conforms (grafo valido)", "True", str(conf), "True", conf is True, f"pyshacl rdfs; violaciones={nv}")
    add("SHACL viola en ejemplo-invalido", "n/d", nvI, ">0", nvI > 0, "pyshacl sobre grafo + ejemplo-invalido.ttl")

    n_pass = sum(1 for r in rows if r["PASS"])
    n_total = len(rows)

    report = {
        "ontologia": "CodeFeedback-KG",
        "version": ver2,
        "fecha": "2026-06-21",
        "resumen": {
            "dimensiones_total": n_total,
            "dimensiones_PASS": n_pass,
            "dimensiones_FAIL": n_total - n_pass,
        },
        "owl_rl": {
            "triples_afirmados_v2": a2,
            "triples_cierre_v2": cierre2,
            "triples_inferidos_v2": cierre2 - a2,
            "conceptos_inferidos_v2": c2,
            "owl_Nothing": nothing2,
            "owl_sameAs_no_reflexivo": sa2,
            "consistente": nothing2 == 0 and sa2 == 0,
        },
        "shacl": {
            "formas": n_shapes,
            "conforms_grafo_valido": conf is True,
            "violaciones_grafo_valido": nv,
            "violaciones_ejemplo_invalido": nvI,
        },
        "vocabularios_externos_v2": voc2,
        "dimensiones": rows,
    }
    (OUT / "v2-target-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # Markdown
    lines = []
    lines.append("# CodeFeedback-KG v2.0 — Informe de objetivos (§10)\n")
    lines.append(f"Generado: 2026-06-21 · versionInfo: **{ver2}** · "
                 f"PASS **{n_pass}/{n_total}** dimensiones.\n")
    lines.append("Re-derivado sobre el grafo final con rdflib/SPARQL, el cierre OWL-RL y SHACL "
                 "(pyshacl, inferencia RDFS). v1.0 = `codefeedback-kg-150.ttl` (congelado); "
                 "v2.0 = `codefeedback-kg.ttl`.\n")
    lines.append("## Cierre OWL-RL y SHACL\n")
    lines.append(f"- Triples afirmados v2.0: **{a2}** · cierre OWL-RL: **{cierre2}** "
                 f"(inferidos {cierre2 - a2}).")
    lines.append(f"- cfkg:Concepto inferidos: **{c2}** · owl:Nothing: **{nothing2}** · "
                 f"owl:sameAs no reflexivo: **{sa2}** -> **CONSISTENTE: {nothing2 == 0 and sa2 == 0}**.")
    lines.append(f"- SHACL formas: **{n_shapes}** · Conforms (grafo valido): **{conf}** "
                 f"(violaciones {nv}) · violaciones en ejemplo-invalido: **{nvI}**.\n")
    lines.append("## Tabla de dimensiones\n")
    lines.append("| dimension | v1.0 | v2.0 | objetivo | PASS/FAIL | re-derivacion |")
    lines.append("|---|---|---|---|---|---|")
    for r in rows:
        estado = "PASS" if r["PASS"] else "FAIL"
        lines.append(f"| {r['dimension']} | {r['v1.0']} | {r['v2.0']} | {r['target']} "
                     f"| **{estado}** | {r['re-derivation']} |")
    lines.append("")
    (OUT / "v2-target-report.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"PASS {n_pass}/{n_total}")
    for r in rows:
        if not r["PASS"]:
            print("  FAIL:", r["dimension"], "->", r["v2.0"], "(objetivo", r["target"], ")")
    print("Escritos: salidas/v2-target-report.md y .json")


if __name__ == "__main__":
    main()
