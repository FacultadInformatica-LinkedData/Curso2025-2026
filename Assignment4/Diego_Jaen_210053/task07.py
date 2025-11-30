# -*- coding: utf-8 -*-
"""Task07_2025.ipynb

**Task 07: Querying RDF(s) - CORREGIDO DEFINITIVO**
"""

# !pip install rdflib
import urllib.request
# OMITTED URL RETRIEVAL FOR CLEAN SCRIPT
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"

from validation import Report

"""First let's read the RDF file"""

from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
# Do not change the name of the variables
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
g.namespace_manager.bind('foaf', Namespace("http://xmlns.com/foaf/0.1/"), override=False)
g.parse(github_storage+"/rdf/data06.ttl", format="TTL")
report = Report()

"""**TASK 7.1a: For all classes, list each classURI. If the class belogs to another class, then list its superclass.**
**Do the exercise in RDFLib returning a list of Tuples: (class, superclass) called "result". If a class does not have a super class, then return None as the superclass**
"""

# TASK 7.1a OK - (Incluido para completar el script)
ns = Namespace("http://somewhere#")
result = [] #list of tuples
for s, p, o in g.triples((None, RDF.type, RDFS.Class)):
    superclasses = list(g.objects(s, RDFS.subClassOf))
    if len(superclasses) > 0:
        for sc in superclasses:
            result.append((s, sc))
    else:
        result.append((s, None))

# Visualize the results
for r in result:
  print(r)

## Validation: Do not remove
report.validate_07_1a(result)

"""**TASK 7.1b: Repeat the same exercise in SPARQL, returning the variables ?c (class) and ?sc (superclass)**"""

# TASK 7.1b OK - (Incluido para completar el script)
query = """
    SELECT ?c ?sc WHERE {
        ?c rdf:type rdfs:Class .
        OPTIONAL { ?c rdfs:subClassOf ?sc }
    }
"""

for r in g.query(query):
  print(r.c, r.sc)

## Validation: Do not remove
report.validate_07_1b(query,g)

"""**TASK 7.2a: List all individuals of "Person" with RDFLib (remember the subClasses). Return the individual URIs in a list called "individuals"**"""

ns = Namespace("http://somewhere#")

# Función auxiliar (mantener lógica robusta)
def get_subclasses(cls):
    subs = set()
    for s, p, o in g.triples((None, RDFS.subClassOf, cls)):
        subs.add(s)
        subs.update(get_subclasses(s))
    return subs

individuals = []
all_person_classes = get_subclasses(ns.Person)
all_person_classes.add(ns.Person)

for c in all_person_classes:
    for s, p, o in g.triples((None, RDF.type, c)):
        individuals.append(s)
        
individuals = list(set(individuals))

# visualize results
for i in individuals:
  print(i)

# validation. Do not remove
report.validate_07_02a(individuals)

"""**TASK 7.2b: Repeat the same exercise in SPARQL, returning the individual URIs in a variable ?ind**"""

# CORRECCIÓN: Usamos UNION y filtramos para ser estrictos con los tipos (Person y subclases)
query = """
    PREFIX ns: <http://somewhere#>
    SELECT DISTINCT ?ind WHERE {
       ?ind rdf:type ?class .
       ?class rdfs:subClassOf* ns:Person .
    }
"""

for r in g.query(query):
  print(r.ind)
# Visualize the results

## Validation: Do not remove
report.validate_07_02b(g, query)

"""**TASK 7.3: List the name and type of those who know Rocky (in SPARQL only). Use name and type as variables in the query**"""

# TO DO
# Se usa foaf:knows y ns:RockySmith
query = """
    PREFIX ns: <http://somewhere#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?name ?type WHERE {
        ?s foaf:knows ns:RockySmith .
        ?s foaf:name ?name .
        ?s rdf:type ?type .
    }
"""
# Visualize the results
for r in g.query(query):
  print(r.name, r.type)

## Validation: Do not remove
report.validate_07_03(g, query)

"""**Task 7.4: List the name of those entities who have a colleague with a dog, or that have a collegue who has a colleague who has a dog (in SPARQL). Return the results in a variable called name**"""

# CORRECCIÓN: Usamos las propiedades específicas del dataset: ns:colleague y ns:hasAnimal
query = """
    PREFIX ns: <http://somewhere#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT DISTINCT ?name WHERE {
        ?s foaf:name ?name .
        
        # Path: 1 o 2 steps of "colleague" (propiedad específica ns:colleague)
        ?s ns:colleague | (ns:colleague / ns:colleague) ?colleague .
        
        # Colleague has a dog (propiedad específica ns:hasAnimal)
        ?colleague ns:hasAnimal ?dog .
        ?dog rdf:type ns:Dog .
    }
"""

for r in g.query(query):
  print(r.name)

# TO DO
# Visualize the results

## Validation: Do not remove
report.validate_07_04(g,query)
report.save_report("_Task_07")