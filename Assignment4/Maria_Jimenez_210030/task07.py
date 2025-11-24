# %% [markdown]
# **Task 07: Querying RDF(s)**

# %%
#!pip install rdflib
import urllib.request
url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"

# %%
from validation import Report

# %% [markdown]
# First let's read the RDF file

# %%
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
# Do not change the name of the variables
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
g.parse(github_storage+"/rdf/data06.ttl", format="turtle")
report = Report()

# %% [markdown]
# **TASK 7.1a: For all classes, list each classURI. If the class belogs to another class, then list its superclass.**
# **Do the exercise in RDFLib returning a list of Tuples: (class, superclass) called "result". If a class does not have a super class, then return None as the superclass**

# %%
# TO DO
# Visualize the results
result = [] #list of tuples

classes = set(g.subjects(RDF.type, RDFS.Class))

for c in classes:
    supercs = list(g.objects(c, RDFS.subClassOf))
    if supercs:
        for sc in supercs:
            result.append((c, sc))
    else:
        result.append((c, None))

for r in result:
  print(r)

# %%
## Validation: Do not remove
report.validate_07_1a(result)

# %% [markdown]
# **TASK 7.1b: Repeat the same exercise in SPARQL, returning the variables ?c (class) and ?sc (superclass)**

# %%
query =  """
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?c ?sc
WHERE {
  ?c rdf:type rdfs:Class .
  OPTIONAL { ?c rdfs:subClassOf ?sc . }
}
ORDER BY ?c ?sc
"""

for r in g.query(query):
  print(r.c, r.sc)


# %%
## Validation: Do not remove
report.validate_07_1b(query,g)

# %% [markdown]
# **TASK 7.2a: List all individuals of "Person" with RDFLib (remember the subClasses). Return the individual URIs in a list called "individuals"**
# 

# %%
ns = Namespace("http://oeg.fi.upm.es/def/people#")

# variable to return
individuals = []

person_class = ns.Person

# buscamos las subclases de person 
to_visit = [person_class]
visited = set()

while to_visit:
    cls = to_visit.pop()
    if cls in visited:
        continue
    visited.add(cls)
    for subclass in g.subjects(RDFS.subClassOf, cls):
        to_visit.append(subclass)

# sacamos los individuos
for cls in visited:
    for ind in g.subjects(RDF.type, cls):
        if ind not in individuals:
            individuals.append(ind)

# visualize results
for i in individuals:
  print(i)

# %%
# validation. Do not remove
report.validate_07_02a(individuals)

# %% [markdown]
# **TASK 7.2b: Repeat the same exercise in SPARQL, returning the individual URIs in a variable ?ind**

# %%
query =  """
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?ind
WHERE {
  ?ind rdf:type/rdfs:subClassOf* <http://oeg.fi.upm.es/def/people#Person> .
}
ORDER BY ?ind
"""

for r in g.query(query):
  print(r.ind)
# Visualize the results

# %%
## Validation: Do not remove
report.validate_07_02b(g, query)

# %% [markdown]
# **TASK 7.3:  List the name and type of those who know Rocky (in SPARQL only). Use name and type as variables in the query**

# %%
# TO DO
query =  """
SELECT DISTINCT ?name ?type
WHERE {
  VALUES ?nameProp {
    <http://oeg.fi.upm.es/def/people#name>
    <http://xmlns.com/foaf/0.1/name>
    <http://www.w3.org/2000/01/rdf-schema#label>
  }

  ?person <http://oeg.fi.upm.es/def/people#knows> <http://oeg.fi.upm.es/def/people#Rocky> .
  ?person ?nameProp ?name .
  ?person <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?type .
}
ORDER BY ?name ?type
"""

# Visualize the results
for r in g.query(query):
  print(r.name, r.type)


# %%
## Validation: Do not remove
report.validate_07_03(g, query)

# %% [markdown]
# **Task 7.4: List the name of those entities who have a colleague with a dog, or that have a collegue who has a colleague who has a dog (in SPARQL). Return the results in a variable called name**

# %%
query =  """
SELECT DISTINCT ?name
WHERE {
  # Nombres de las personas
  ?entity <http://www.w3.org/2000/01/rdf-schema#label> ?name .

  # Buscar los colegas de cada nombre
  ?entity ( <http://oeg.fi.upm.es/def/people#hasColleague>
          | ^<http://oeg.fi.upm.es/def/people#hasColleague> )
          /
          ( <http://oeg.fi.upm.es/def/people#hasColleague>
          | ^<http://oeg.fi.upm.es/def/people#hasColleague> )?  ?x .

  # Ver si el colega tiene una mascota        
  ?x   <http://oeg.fi.upm.es/def/people#ownsPet> ?pet .
}
ORDER BY ?name
"""

# TO DO
# Visualize the results
for r in g.query(query):
  print(r.name)

# %%
## Validation: Do not remove
report.validate_07_04(g,query)
report.save_report("_Task_07")


