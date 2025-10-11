#%% md
# **Task 07: Querying RDF(s)**
#%%
import urllib.request
url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"
#%%
from Assignment4.Diego_Ortega_Martinez_707214.validation import Report
#%% md
# First let's read the RDF file
#%%
from rdflib import Graph, Namespace

# Do not change the name of the variables
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
g.parse(github_storage+"/rdf/data06.ttl", format="TTL")
report = Report()
#%% md
# **TASK 7.1a: For all classes, list each classURI. If the class belogs to another class, then list its superclass.**
# **Do the exercise in RDFLib returning a list of Tuples: (class, superclass) called "result". If a class does not have a super class, then return None as the superclass**
#%%
from rdflib import Namespace, URIRef
from rdflib.namespace import RDF, RDFS

ontology = Namespace("http://oeg.fi.upm.es/def/people#")
ONT = str(ontology)

def in_ontology(u):
    return isinstance(u, URIRef) and str(u).startswith(ONT)



classes = set()

for c in g.subjects(RDF.type, RDFS.Class):
    if in_ontology(c):
        classes.add(c)

for c in g.subjects(RDFS.subClassOf, None):
    if in_ontology(c):
        classes.add(c)

for c in g.objects(None, RDFS.subClassOf):
    if in_ontology(c):
        classes.add(c)


result = []
for c in sorted(classes, key=lambda u: str(u)):

    supers = [s for s in g.objects(c, RDFS.subClassOf) if in_ontology(s)]
    sup = supers[0] if supers else None
    result.append((c, sup))

for r in result:
    print(r)

#%%
## Validation: Do not remove
report.validate_07_1a(result)
#%% md
# **TASK 7.1b: Repeat the same exercise in SPARQL, returning the variables ?c (class) and ?sc (superclass)**
#%%
query = """
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ontology: <http://oeg.fi.upm.es/def/people#>

SELECT ?c (SAMPLE(?sc) AS ?sc) WHERE {
  {
    ?c a rdfs:Class .
  } UNION {
    ?c rdfs:subClassOf ?x .
  } UNION {
    ?x rdfs:subClassOf ?c .
  }

  FILTER(STRSTARTS(STR(?c), STR(ontology:)))

  OPTIONAL {
    ?c rdfs:subClassOf ?sc .
    FILTER(STRSTARTS(STR(?sc), STR(ontology:)))
  }
}
GROUP BY ?c
ORDER BY ?c
"""

for r in g.query(query):
    print(r.c, r.sc)



#%%
## Validation: Do not remove
report.validate_07_1b(query,g)
#%% md
# **TASK 7.2a: List all individuals of "Person" with RDFLib (remember the subClasses). Return the individual URIs in a list called "individuals"**
# 
#%%
from rdflib import Namespace
from rdflib.namespace import RDF, RDFS


ns = Namespace("http://oeg.fi.upm.es/def/people#")


classes = {ns.Person}
changed = True
while changed:
    changed = False
    for c, _, parent in g.triples((None, RDFS.subClassOf, None)):
        if parent in classes and c not in classes:
            classes.add(c)
            changed = True


indiv_set = set()
for cls in classes:
    for s in g.subjects(RDF.type, cls):
        indiv_set.add(s)


individuals = sorted(indiv_set, key=lambda x: str(x))


for i in individuals:
    print(i)

#%%
# validation. Do not remove
report.validate_07_02a(individuals)
#%% md
# **TASK 7.2b: Repeat the same exercise in SPARQL, returning the individual URIs in a variable ?ind**
#%%
query = """
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ontology: <http://oeg.fi.upm.es/def/people#>

SELECT DISTINCT ?ind WHERE {
  ?ind rdf:type ?c .
  ?c rdfs:subClassOf* ontology:Person .
}
ORDER BY ?ind
"""

for r in g.query(query):
  print(r.ind)
# Visualize the results
#%%
## Validation: Do not remove
report.validate_07_02b(g, query)
#%% md
# **TASK 7.3:  List the name and type of those who know Rocky (in SPARQL only). Use name and type as variables in the query**
#%%
query = """
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ontology: <http://oeg.fi.upm.es/def/people#>

SELECT DISTINCT ?name ?type WHERE {
  ?s ontology:knows ontology:Rocky .
  ?s rdf:type ?type .
  OPTIONAL { ?s ontology:hasName ?n1 }
  OPTIONAL { ?s rdfs:label        ?n2 }
  BIND(COALESCE(?n1, ?n2) AS ?name)
}
ORDER BY ?name
"""

# TO DO
# Visualize the results
for r in g.query(query):
  print(r.name, r.type)

#%%
## Validation: Do not remove
report.validate_07_03(g, query)
#%% md
# **Task 7.4: List the name of those entities who have a colleague with a dog, or that have a collegue who has a colleague who has a dog (in SPARQL). Return the results in a variable called name**
#%%
query = """
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ontology: <http://oeg.fi.upm.es/def/people#>

SELECT DISTINCT ?name WHERE {
  { ?s ontology:hasColleague/ontology:ownsPet ?p .
    ?p rdf:type ontology:Animal . }

  UNION

  { ?s ontology:hasColleague/ontology:hasColleague/ontology:ownsPet ?p2 .
    ?p2 rdf:type ontology:Animal . }

  OPTIONAL { ?s ontology:hasName ?n1 }
  OPTIONAL { ?s rdfs:label        ?n2 }
  BIND(COALESCE(?n1, ?n2) AS ?name)
}
ORDER BY ?name
"""



for r in g.query(query):
  print(r.name)

# TO DO
# Visualize the results
#%%
## Validation: Do not remove
report.validate_07_04(g,query)
report.save_report("_Task_07")