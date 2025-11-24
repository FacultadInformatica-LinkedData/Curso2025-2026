#!/usr/bin/env python
# coding: utf-8

# **Task 07: Querying RDF(s)**

# In[1]:


#get_ipython().system('pip install rdflib')
import urllib.request
url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"


# In[2]:


from validation import Report


# First let's read the RDF file

# In[3]:


from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
# Do not change the name of the variables
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
g.parse(github_storage+"/rdf/data06.ttl", format="TTL")
report = Report()


# **TASK 7.1a: For all classes, list each classURI. If the class belogs to another class, then list its superclass.**
# **Do the exercise in RDFLib returning a list of Tuples: (class, superclass) called "result". If a class does not have a super class, then return None as the superclass**

# In[4]:


# TO DO
defined_classes = set(g.subjects(RDF.type, RDFS.Class))


result = []
for class_uri in sorted(defined_classes):
    super_classes = list(g.objects(class_uri, RDFS.subClassOf))
    if super_classes:
        # Puede haber múltiples superclases
        for parent in sorted(super_classes):
            result.append((class_uri, parent))
    else:
        result.append((class_uri, None))

# Visualize the results
for r in result:
  print(r)


# In[5]:


## Validation: Do not remove
report.validate_07_1a(result)


# **TASK 7.1b: Repeat the same exercise in SPARQL, returning the variables ?c (class) and ?sc (superclass)**

# In[6]:


#TO DO
query = """
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?c ?sc
WHERE {
  ?c rdf:type rdfs:Class .
  OPTIONAL { ?c rdfs:subClassOf ?sc . }
}
ORDER BY ?c ?sc
"""
# visualize results
for r in g.query(query):
  print(r.c, r.sc)


# In[7]:


## Validation: Do not remove
report.validate_07_1b(query,g)


# **TASK 7.2a: List all individuals of "Person" with RDFLib (remember the subClasses). Return the individual URIs in a list called "individuals"**
# 

# In[8]:


#TO DO
ns = Namespace("http://oeg.fi.upm.es/def/people#")

person_classes = set([ns.Person])
to_visit = [ns.Person]

while to_visit:
    cls = to_visit.pop()
    for sub in g.subjects(RDFS.subClassOf, cls):
        if sub not in person_classes:
            person_classes.add(sub)
            to_visit.append(sub)
# variable to return
individuals_set = set()
for cls in person_classes:
    for inst in g.subjects(RDF.type, cls):
        individuals_set.add(inst)

# Variable a devolver (lista). 
individuals = sorted(individuals_set)
# visualize results
for i in individuals:
  print(i)


# In[9]:


# validation. Do not remove
report.validate_07_02a(individuals)


# **TASK 7.2b: Repeat the same exercise in SPARQL, returning the individual URIs in a variable ?ind**

# In[10]:


#TO DO

query = """
PREFIX ns:   <http://oeg.fi.upm.es/def/people#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?ind
WHERE {
  ?ind rdf:type ?cls .
  ?cls rdfs:subClassOf* ns:Person .
}
ORDER BY ?ind
"""
# Visualize the results
for r in g.query(query):
  print(r.ind)


# In[11]:


## Validation: Do not remove
report.validate_07_02b(g, query)


# **TASK 7.3:  List the name and type of those who know Rocky (in SPARQL only). Use name and type as variables in the query**

# In[12]:


# TO DO

query = """
PREFIX ns:   <http://oeg.fi.upm.es/def/people#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?name ?type
WHERE {
  ?x ns:knows ns:Rocky .
  ?x rdf:type ?type .
  OPTIONAL { ?x ns:hasName ?n1 . }
  OPTIONAL { ?x rdfs:label ?n2 . }
  BIND(COALESCE(?n1, ?n2) AS ?name)
}
ORDER BY ?name ?type
"""
# Visualize the results
for r in g.query(query):
  print(r.name, r.type)


# In[13]:


## Validation: Do not remove
report.validate_07_03(g, query)


# **Task 7.4: List the name of those entities who have a colleague with a dog, or that have a collegue who has a colleague who has a dog (in SPARQL). Return the results in a variable called name**

# In[14]:


# TO DO
query = """
PREFIX ns:   <http://oeg.fi.upm.es/def/people#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?name
WHERE {
  {
    # 1 salto: colega con perro
    ?person ns:hasColleague ?col .
    ?col ns:ownsPet ?pet .
    ?pet rdf:type ns:Animal .
  }
  UNION
  {
    # 2 saltos: colega de colega con perro
    ?person ns:hasColleague ?col1 .
    ?col1 ns:hasColleague ?col2 .
    ?col2 ns:ownsPet ?pet2 .
    ?pet2 rdf:type ns:Animal .
  }

  # Nombre por hasName o label
  OPTIONAL { ?person ns:hasName ?n1 . }
  OPTIONAL { ?person rdfs:label ?n2 . }
  BIND(COALESCE(?n1, ?n2) AS ?name)
}
ORDER BY ?name
"""


# Visualize the results

for r in g.query(query):
  print(r.name)


# In[15]:


## Validation: Do not remove
report.validate_07_04(g,query)
report.save_report("_Task_07")


