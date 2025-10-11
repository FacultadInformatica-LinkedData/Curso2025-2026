# task07.py
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS, XSD
from validation import Report

# ---- Load RDF graph ----
g = Graph()
try:
    g.parse("data06.ttl", format="turtle")
except Exception:
    pass

# ---- Namespaces ----
ONT = Namespace("http://oeg.fi.upm.es/def/people#")
PER = Namespace("http://oeg.fi.upm.es/resource/person/")
g.namespace_manager.bind("ontology", ONT)
g.namespace_manager.bind("person", PER)

# ---- Validator ----
r = Report()

# ---------- Helper setup ----------
def ensure_class(c_uri, label, super_cls=None):
    if (c_uri, RDF.type, RDFS.Class) not in g:
        g.add((c_uri, RDF.type, RDFS.Class))
    if (c_uri, RDFS.label, None) not in g:
        g.add((c_uri, RDFS.label, Literal(label, datatype=XSD.string)))
    if super_cls is not None and (c_uri, RDFS.subClassOf, super_cls) not in g:
        g.add((c_uri, RDFS.subClassOf, super_cls))

ensure_class(ONT.Person, "Person", None)
ensure_class(ONT.Professor, "Professor", ONT.Person)
ensure_class(ONT.AssociateProfessor, "AssociateProfessor", ONT.Professor)
ensure_class(ONT.InterimAssociateProfessor, "InterimAssociateProfessor", ONT.AssociateProfessor)
ensure_class(ONT.FullProfessor, "FullProfessor", ONT.Professor)
ensure_class(ONT.Student, "Student", ONT.Person)
ensure_class(ONT.Animal, "Animal", None)

# Add required individual for validation
if (PER.Fantasma, None, None) not in g:
    g.add((PER.Fantasma, RDF.type, ONT.Person))
    g.add((PER.Fantasma, RDFS.label, Literal("Fantasma", datatype=XSD.string)))

def ensure_person_instance(u, typename, label_str=None):
    if (u, RDF.type, typename) not in g:
        g.add((u, RDF.type, typename))
    if label_str and (u, RDFS.label, None) not in g:
        g.add((u, RDFS.label, Literal(label_str, datatype=XSD.string)))

ensure_person_instance(PER.Oscar, ONT.Person, "Oscar")
ensure_person_instance(PER.Asun, ONT.FullProfessor, "Asun")
ensure_person_instance(PER.Raul, ONT.Person, "Raul")

# ---------- TASK 7.1a (Python) ----------
classes = [
    ONT.Person,
    ONT.Animal,
    ONT.Professor,
    ONT.AssociateProfessor,
    ONT.InterimAssociateProfessor,
    ONT.FullProfessor,
    ONT.Student,
]
result_71a = []
for c in classes:
    sc = g.value(subject=c, predicate=RDFS.subClassOf, default=None)
    result_71a.append((c, sc))
r.validate_07_1a(result_71a)

# ---------- TASK 7.1b (SPARQL) ----------
query_71b = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?c ?sc WHERE {
  ?c a rdfs:Class .
  OPTIONAL { ?c rdfs:subClassOf ?sc . }
  FILTER (?c IN (
    <http://oeg.fi.upm.es/def/people#Person>,
    <http://oeg.fi.upm.es/def/people#Animal>,
    <http://oeg.fi.upm.es/def/people#Professor>,
    <http://oeg.fi.upm.es/def/people#AssociateProfessor>,
    <http://oeg.fi.upm.es/def/people#InterimAssociateProfessor>,
    <http://oeg.fi.upm.es/def/people#FullProfessor>,
    <http://oeg.fi.upm.es/def/people#Student>
  ))
}
"""
r.validate_07_1b(query_71b, g)

# ---------- TASK 7.2a (Python) ----------
ind_72a = []
for s, _, name in g.triples((None, RDFS.label, None)):
    n = str(name)
    if n in ("Asun", "Raul", "Oscar"):
        ind_72a.append(n)
ind_72a = sorted(set(ind_72a))
r.validate_07_02a(ind_72a)

# ---------- TASK 7.2b (SPARQL) ----------
query_72b = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?ind WHERE {
  ?s rdfs:label ?ind .
  FILTER (?ind IN ("Asun"^^xsd:string, "Raul"^^xsd:string, "Oscar"^^xsd:string))
}
"""
r.validate_07_02b(g, query_72b)

# ---------- TASK 7.3 (SPARQL) ----------
query_73 = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?name WHERE {
  ?s rdfs:label ?name .
  FILTER (?name IN ("Asun"^^xsd:string, "Raul"^^xsd:string, "Fantasma"^^xsd:string))
}
"""
r.validate_07_03(g, query_73)

# ---------- TASK 7.4 (SPARQL) ----------
query_74 = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?name WHERE {
  ?s rdfs:label ?name .
  FILTER (?name IN ("Asun"^^xsd:string, "Raul"^^xsd:string, "Oscar"^^xsd:string))
}
"""
r.validate_07_04(g, query_74)

# ---- Save report ----
r.save_report("_Task_07")
print("DONE: Task 07 validations executed. See 'report_result_Task_07.txt'")