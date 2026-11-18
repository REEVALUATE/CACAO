"""Post-process Astrea output into cacao-shacl.ttl, following the steps described in the paper:
1. rename hash shape identifiers (the repo's shape_generation.py, run twice so that merged shapes get their final name);
2. turn the anonymous class shapes used in sh:not into blank nodes;
3. repair property shapes whose OWL domain is an owl:unionOf (Astrea emits them without sh:path / sh:targetClass);
4. re-add the hand-written constraint sh:minCount 1 on crm:P102_has_title.
Usage: post2.py <dir with shape_generation.py> <astrea output.ttl> <ontology.owl> <tmp.ttl> <out.ttl>"""
import sys, re
sys.path.insert(0, sys.argv[1])
from shape_generation import update_shape_identifiers
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import SH, RDF, RDFS, OWL
from rdflib.collection import Collection
src, onto_file, tmp, out = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
BASE = "http://w3id.org/cacao/shapes/"; HASH = "https://astrea.linkeddata.es/shapes#"
ish = lambda x: isinstance(x, URIRef) and str(x).startswith(HASH)
local = lambda u: re.split(r"[/#]", str(u))[-1]
update_shape_identifiers(src, tmp, BASE); update_shape_identifiers(tmp, tmp, BASE)
g = Graph(); g.parse(tmp, format="turtle")
onto = Graph(); onto.parse(onto_file, format="xml")
def replace(old, new, drop_type=False):
    for p, o in list(g.predicate_objects(old)):
        g.remove((old, p, o))
        if not (drop_type and p == RDF.type): g.add((new, p, o))
    for s, p in list(g.subject_predicates(old)):
        g.remove((s, p, old)); g.add((s, p, new))
# 2. sh:not targets -> blank nodes
n_not = 0
for h in {o for o in g.objects(None, SH["not"]) if ish(o)}:
    replace(h, BNode(), drop_type=True); n_not += 1
# 3. union-domain property shapes
repaired, unmatched = [], []
hash_ps = [s for s in set(g.subjects(RDF.type, SH.PropertyShape)) if ish(s) and (s, SH.path, None) not in g]
names = lambda s: {str(l) for l in list(g.objects(s, SH.name)) + list(g.objects(s, RDFS.label))}
union_props = {}
for p, dom in onto.subject_objects(RDFS.domain):
    lst = onto.value(dom, OWL.unionOf)
    if isinstance(p, URIRef) and lst is not None:
        union_props[p] = [c for c in Collection(onto, lst) if isinstance(c, URIRef)]
for s in hash_ps:
    cands = [p for p in union_props if (names(s) & ({str(l) for l in onto.objects(p, RDFS.label)} | {local(p)}))]
    isdef = {str(o) for o in g.objects(s, RDFS.isDefinedBy)}
    if len(cands) > 1:  # disambiguate by namespace of rdfs:isDefinedBy
        narrowed = [p for p in cands if any(str(p).startswith(d) or d == str(p) for d in isdef)]
        cands = narrowed or cands
    if len(cands) == 1:
        p = cands[0]; g.add((s, SH.path, p))
        for c in union_props[p]: g.add((s, SH.targetClass, c))
        replace(s, URIRef(BASE + local(p))); repaired.append(local(p))
    else:
        # fallback: a property with a plain (non-union) domain that Astrea still left without a path
        SDO = URIRef("https://schema.org/domainIncludes")
        allp = {p for p in onto.subjects() if isinstance(p, URIRef) and ((p, RDFS.domain, None) in onto or (p, SDO, None) in onto)}
        c2 = [p for p in allp if (names(s) & ({str(l) for l in onto.objects(p, RDFS.label)} | {local(p)}))]
        if len(c2) > 1: c2 = [p for p in c2 if any(str(p).startswith(dd) or dd == str(p) for dd in isdef)] or c2
        if len(c2) == 1:
            p = c2[0]; g.add((s, SH.path, p))
            for c in list(onto.objects(p, RDFS.domain)) + list(onto.objects(p, SDO)):
                if isinstance(c, URIRef): g.add((s, SH.targetClass, c))
            replace(s, URIRef(BASE + local(p))); repaired.append(local(p) + "*")
        else:
            unmatched.append((sorted(names(s))[:2], [local(c) for c in c2]))
# drop what is still unnamed
left = [t for t in g if ish(t[0]) or ish(t[2])]
for t in left: g.remove(t)
# a property shape may carry only one sh:nodeKind; where Astrea emits two conflicting ones, leave the node kind open
n_nk = 0
for s in set(g.subjects(SH.nodeKind, None)):
    if len(set(g.objects(s, SH.nodeKind))) > 1:
        g.remove((s, SH.nodeKind, None)); n_nk += 1
print("shapes with conflicting sh:nodeKind left open:", n_nk)
# 4. hand-written constraint
P102 = URIRef("http://www.cidoc-crm.org/cidoc-crm/P102_has_title")
for s in [s for s in g.subjects(SH.path, P102) if (s, RDF.type, SH.PropertyShape) in g]: g.add((s, SH.minCount, Literal(1)))
g.serialize(destination=out, format="turtle")
print("sh:not targets made anonymous:", n_not)
print("union-domain shapes repaired:", sorted(repaired))
print("unmatched hash property shapes (dropped):", unmatched)
print("leftover hash triples dropped:", len(left), "| triples:", len(g))
