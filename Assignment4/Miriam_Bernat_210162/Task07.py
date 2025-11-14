# %% [markdown]
# **Task 07: Querying RDF(s)**

# %%
# pip install rdflib
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
g.parse(github_storage+"/rdf/data06.ttl", format="TTL")
report = Report()

# %% [markdown]
# **TASK 7.1a: For all classes, list each classURI. If the class belogs to another class, then list its superclass.**
# **Do the exercise in RDFLib returning a list of Tuples: (class, superclass) called "result". If a class does not have a super class, then return None as the superclass**

# %%
# Find all classes and their superclasses
result = []

# Get all classes and check for their superclasses
for s, p, o in g:
    if p == RDF.type and o == RDFS.Class:
        # Found a class, now check if it has a superclass
        superclass = None
        for s2, p2, o2 in g:
            if s2 == s and p2 == RDFS.subClassOf:
                superclass = o2
                break
        result.append((s, superclass))

# Visualize the results
for r in result:
  print(r)

# %%
## Validation: Do not remove
report.validate_07_1a(result)

# %% [markdown]
# **TASK 7.1b: Repeat the same exercise in SPARQL, returning the variables ?c (class) and ?sc (superclass)**

# %%
query = """
SELECT DISTINCT ?c ?sc WHERE 
  {
    ?c rdf:type rdfs:Class .
    OPTIONAL { ?c rdfs:subClassOf ?sc }
  }
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

# Helper method
def get_all_subclasses(g, class_uri):
    """Get all subclasses of a class including the class itself"""
    all_classes = [class_uri]
    for s, p, o in g:
        if p == RDFS.subClassOf and o == class_uri:
            all_classes.extend(get_all_subclasses(g, s))
    return all_classes

# Get all classes that are Person or subclasses of Person
person_classes = get_all_subclasses(g, ns.Person)

# Find all individuals of these classes
for class_type in person_classes:
    for s, p, o in g:
        if p == RDF.type and o == class_type:
            if s not in individuals:
                individuals.append(s)

# visualize results
for i in individuals:
  print(i)

# %%
# validation. Do not remove
report.validate_07_02a(individuals)

# %% [markdown]
# **TASK 7.2b: Repeat the same exercise in SPARQL, returning the individual URIs in a variable ?ind**

# %%
query = """
PREFIX ns: <http://oeg.fi.upm.es/def/people#>
SELECT DISTINCT ?ind WHERE {
    ?ind rdf:type ?s .
    ?s rdfs:subClassOf* ns:Person .
}
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
query = """
PREFIX ns: <http://oeg.fi.upm.es/def/people#>
SELECT ?name ?type WHERE {
    ?entity ns:knows ns:Rocky .
    ?entity rdf:type ?type .
    ?entity rdfs:label ?name .
}
"""
# TO DO
# Visualize the results
for r in g.query(query):
  print(r.name, r.type)

# %%
## Validation: Do not remove
report.validate_07_03(g, query)

# %% [markdown]
# **Task 7.4: List the name of those entities who have a colleague with a dog, or that have a collegue who has a colleague who has a dog (in SPARQL). Return the results in a variable called name**

# %%
query = """
PREFIX ns: <http://oeg.fi.upm.es/def/people#>
SELECT DISTINCT ?name WHERE {
    ?entity rdfs:label ?name .
    {
        ?entity ns:hasColleague ?colleague .
        ?colleague ns:ownsPet ?pet .
    }
    UNION
    {
        ?entity ns:hasColleague ?colleague1 .
        ?colleague1 ns:hasColleague ?colleague2 .
        ?colleague2 ns:ownsPet ?pet .
    }
}
"""

for r in g.query(query):
  print(r.name)

# %%
## Validation: Do not remove
report.validate_07_04(g,query)
report.save_report("_Task_07")


