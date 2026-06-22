# -*- coding: utf-8 -*-
"""Exporta la 'Grafoteca' a JSON (formato Cytoscape.js) desde los artefactos REALES.
Genera salidas/grafos/grafoteca.json con todos los tipos de grafo del proyecto.
Cifras por SPARQL/parseo del .ttl (cero invención). Se ancla a Path(__file__)."""
import json
from pathlib import Path
import rdflib
from rdflib.namespace import RDF, RDFS, OWL

BASE = Path(__file__).resolve().parent.parent
ONTO = BASE / "ontologia" / "codefeedback-kg-150.ttl"
SHAPES = BASE / "ontologia" / "shapes-ekg.ttl"
WD = BASE / "ontologia" / "wikidata_sameas.json"
VOID = BASE / "ontologia" / "void.ttl"
FED = BASE / "salidas" / "08_federada_wikidata.txt"
OUT = BASE / "salidas" / "grafos"
OUT.mkdir(parents=True, exist_ok=True)

PY = rdflib.Namespace("https://w3id.org/codefeedback-kg/schema#")
CFR = rdflib.Namespace("https://w3id.org/codefeedback-kg/id/")
SKOS = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")
g = rdflib.Graph(); g.parse(ONTO, format="turtle")

def loc(u): return str(u).split("/")[-1].split("#")[-1]
def es(s):
    for o in g.objects(s, RDFS.label):
        if getattr(o, "language", None) == "es": return str(o)
    for o in g.objects(s, RDFS.label): return str(o)
    for o in g.objects(s, SKOS.prefLabel): return str(o)
    return loc(s)

def N(i, label, kind, **extra):
    d = {"id": i, "label": label, "kind": kind}; d.update(extra); return {"data": d}
def E(s, t, rel):
    return {"data": {"id": f"{rel}__{s}__{t}", "source": s, "target": t, "rel": rel}}

# ---- conceptos / temas / errores ----
concepts = sorted({s for s in g.subjects(PY.perteneceATema, None)}, key=loc)
cid = {c: loc(c) for c in concepts}
tema_of = {c: next(g.objects(c, PY.perteneceATema), None) for c in concepts}
dif_of = {c: (int(next(g.objects(c, PY.tieneDificultad), 0)) or None) for c in concepts}
temas = sorted({t for t in tema_of.values() if t}, key=loc)
nodes_concept = [N(cid[c], es(c), "concept", tema=es(tema_of[c]) if tema_of[c] else "",
                   dif=dif_of[c]) for c in concepts]
nodes_tema = [N("tema_" + loc(t), es(t), "tema") for t in temas]

edges = {k: [] for k in ("prereq", "contrasta", "error", "broader", "narrower", "related", "tema")}
for s, o in g.subject_objects(PY.requierePrerrequisito):
    if s in cid and o in cid: edges["prereq"].append(E(cid[s], cid[o], "prereq"))
for s, o in g.subject_objects(PY.contrastaCon):
    if s in cid and o in cid: edges["contrasta"].append(E(cid[s], cid[o], "contrasta"))
for s, o in g.subject_objects(SKOS.broader):
    if s in cid and o in cid: edges["broader"].append(E(cid[s], cid[o], "broader"))
for s, o in g.subject_objects(SKOS.narrower):
    if s in cid and o in cid: edges["narrower"].append(E(cid[s], cid[o], "narrower"))
for s, o in g.subject_objects(SKOS.related):
    if s in cid and o in cid: edges["related"].append(E(cid[s], cid[o], "related"))
for c in concepts:
    if tema_of[c]: edges["tema"].append(E(cid[c], "tema_" + loc(tema_of[c]), "tema"))
# errores
err_nodes, err_edges = [], []
for e in g.subjects(RDF.type, PY.ErrorConceptual):
    eid = "err_" + loc(e); err_nodes.append(N(eid, es(e), "error"))
    for c in g.objects(e, PY.errorSobreConcepto):
        if c in cid: err_edges.append(E(eid, cid[c], "error"))

# ---- TBox (clases + subClassOf + dominio/rango) ----
tbox_nodes, tbox_edges = [], []
classes = sorted({s for s in g.subjects(RDF.type, OWL.Class) if isinstance(s, rdflib.URIRef)}, key=loc)
for c in classes: tbox_nodes.append(N("cls_" + loc(c), loc(c), "class"))
for s, o in g.subject_objects(RDFS.subClassOf):
    if s in classes and o in classes:
        tbox_edges.append(E("cls_" + loc(s), "cls_" + loc(o), "subClassOf"))
for p in set(g.subjects(RDF.type, OWL.ObjectProperty)) | set(g.subjects(RDF.type, OWL.DatatypeProperty)):
    dom = next(g.objects(p, RDFS.domain), None); rng = next(g.objects(p, RDFS.range), None)
    pid = "prop_" + loc(p); tbox_nodes.append(N(pid, loc(p), "prop"))
    if dom in classes: tbox_edges.append(E("cls_" + loc(dom), pid, "domain"))
    if rng in classes: tbox_edges.append(E(pid, "cls_" + loc(rng), "range"))

# ---- SHACL (shapes -> targetClass + property constraints) ----
gs = rdflib.Graph(); gs.parse(SHAPES, format="turtle")
shacl_nodes, shacl_edges = [], []
for sh in gs.subjects(RDF.type, SH.NodeShape):
    tc = next(gs.objects(sh, SH.targetClass), None)
    if tc is None: continue
    sid = "sh_" + loc(tc); shacl_nodes.append(N(sid, "Shape:" + loc(tc), "shape"))
    cnode = "shcls_" + loc(tc); shacl_nodes.append(N(cnode, loc(tc), "class"))
    shacl_edges.append(E(sid, cnode, "targetClass"))
    for ps in gs.objects(sh, SH.property):
        path = next(gs.objects(ps, SH.path), None)
        mn = next(gs.objects(ps, SH.minCount), None)
        oblig = " (min 1)" if mn is not None and int(mn) >= 1 else ""
        if path is not None:
            pid = sid + "_p_" + loc(path)
            shacl_nodes.append(N(pid, loc(path) + oblig, "constraint"))
            shacl_edges.append(E(sid, pid, "property"))

# ---- Federado a Wikidata (30 enlaces; 20 con descripción) ----
wd = json.loads(WD.read_text(encoding="utf-8"))
desc = {}
for l in FED.read_text(encoding="utf-8").split("\n"):
    p = l.split("\t")
    if len(p) == 3 and p[0] != "id": desc[p[0]] = p[2]
fed_nodes, fed_edges = [], []
# wikidata_sameas.json puede ser dict {id:QID} o lista; normalizar
pairs = wd.items() if isinstance(wd, dict) else [(x.get("id"), x.get("qid") or x.get("wikidata")) for x in wd]
for cid_, qid in pairs:
    if not cid_: continue
    qid = (qid if isinstance(qid, str) else "").split("/")[-1]
    wn = "wd_" + qid
    lab = next((es(c) for c in concepts if cid[c] == cid_), cid_)
    if not any(n["data"]["id"] == cid_ for n in fed_nodes):
        fed_nodes.append(N(cid_, lab, "concept"))
    fed_nodes.append(N(wn, qid + ((" · " + desc[cid_]) if cid_ in desc else ""), "wikidata",
                       hasdesc=bool(cid_ in desc)))
    fed_edges.append(E(cid_, wn, "exactMatch"))

# ---- LOD / vocabularios (void.ttl) ----
gv = rdflib.Graph(); gv.parse(VOID, format="turtle")
VOIDNS = rdflib.Namespace("http://rdfs.org/ns/void#")
lod_nodes = [N("ekg", "CodeFeedback-KG (157 conc.)", "dataset"), N("wikidata", "Wikidata", "dataset")]
lod_edges = [E("ekg", "wikidata", "linkset")]
for v in gv.objects(None, VOIDNS.vocabulary):
    vn = "voc_" + loc(v); lod_nodes.append(N(vn, loc(v) or str(v), "vocab"))
    lod_edges.append(E("ekg", vn, "reusa"))

# ---- RAG: caso 07 (estático, real, documentado) ----
def prereqs(c):
    return [cid[o] for o in g.objects(c, PY.requierePrerrequisito) if o in cid]
rag_nodes, rag_edges = [], []
def add_caso(env, errlbl, concepto_id):
    c = next((x for x in concepts if cid[x] == concepto_id), None)
    if not c: return
    rag_nodes.append(N(env, env, "envio"))
    en = env + "_err"; rag_nodes.append(N(en, errlbl, "error")); rag_edges.append(E(env, en, "diagnostica"))
    rag_nodes.append(N(cid[c], es(c), "recuperado")); rag_edges.append(E(en, cid[c], "sobre"))
    for p in prereqs(c):
        pc = next((x for x in concepts if cid[x] == p), None)
        rag_nodes.append(N(p, es(pc) if pc else p, "prereq")); rag_edges.append(E(cid[c], p, "prereq"))
add_caso("Envío 001", "off-by-one", "indexacion")
add_caso("Envío 002", "iteración/recursión", "recursion")

DATA = {
    "concepts": nodes_concept, "temas": nodes_tema, "errors": err_nodes,
    "edges": edges, "errorEdges": err_edges,
    "tbox": {"nodes": tbox_nodes, "edges": tbox_edges},
    "shacl": {"nodes": shacl_nodes, "edges": shacl_edges},
    "federado": {"nodes": fed_nodes, "edges": fed_edges},
    "lod": {"nodes": lod_nodes, "edges": lod_edges},
    "rag": {"nodes": rag_nodes, "edges": rag_edges},
    "meta": {
        "conceptos": len(concepts), "temas": len(temas), "errores": len(err_nodes),
        "prereq": len(edges["prereq"]), "contrasta": len(edges["contrasta"]),
        "broader": len(edges["broader"]), "narrower": len(edges["narrower"]),
        "related": len(edges["related"]),
        "clases": len(classes), "shapes": len(set(gs.subjects(RDF.type, SH.NodeShape))),
        "exactMatch": len(fed_edges), "fed_desc": len(desc), "vocabs": len(lod_nodes) - 2,
    },
}
(OUT / "grafoteca.json").write_text(json.dumps(DATA, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("[ok] grafoteca.json")
for k, v in DATA["meta"].items(): print(f"  {k}: {v}")
print("  bytes:", (OUT / "grafoteca.json").stat().st_size)
