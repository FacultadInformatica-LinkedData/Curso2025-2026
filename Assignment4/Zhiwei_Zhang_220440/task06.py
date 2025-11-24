#!/usr/bin/env python
# coding: utf-8

# **Task 06: Modifying RDF(s)**

# In[12]:


#get_ipython().system('pip install rdflib')
import urllib.request
url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"


# Import RDFLib main methods

# In[13]:


from rdflib import Graph, Namespace, Literal, XSD
from rdflib.namespace import RDF, RDFS
from validation import Report
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
r = Report()


# Create a new class named Researcher

# In[14]:


ns = Namespace("http://mydomain.org#")
g.add((ns.Researcher, RDF.type, RDFS.Class))
for s, p, o in g:
  print(s,p,o)


# **Task 6.0: Create new prefixes for "ontology" and "person" as shown in slide 14 of the Slidedeck 01a.RDF(s)-SPARQL shown in class.**

# In[15]:


# this task is validated in the next step
ontology = Namespace("http://oeg.fi.upm.es/def/people#")
person = Namespace("http://oeg.fi.upm.es/resource/person/")

g.namespace_manager.bind('ontology', ontology, override=False)
g.namespace_manager.bind('person', person, override=False)


# **TASK 6.1: Reproduce the taxonomy of classes shown in slide 34 in class (all the classes under "Vocabulario", Slidedeck: 01a.RDF(s)-SPARQL). Add labels for each of them as they are in the diagram (exactly) with no language tags. Remember adding the correct datatype (xsd:String) when appropriate**
# 

# In[16]:


# TO DO


g.add((ontology.Person, RDF.type, RDFS.Class))
g.add((ontology.Professor, RDF.type, RDFS.Class))
g.add((ontology.AssociateProfessor, RDF.type, RDFS.Class))
g.add((ontology.FullProfessor, RDF.type, RDFS.Class))
g.add((ontology.InterimAssociateProfessor, RDF.type, RDFS.Class))
 
g.add((ontology.Professor, RDFS.subClassOf, ontology.Person))
g.add((ontology.AssociateProfessor, RDFS.subClassOf, ontology.Professor))
g.add((ontology.FullProfessor, RDFS.subClassOf, ontology.Professor))
g.add((ontology.InterimAssociateProfessor, RDFS.subClassOf, ontology.AssociateProfessor))

g.add((ontology.Person, RDFS.label, Literal("Person", datatype=XSD.string)))
g.add((ontology.Professor, RDFS.label, Literal("Professor", datatype=XSD.string)))
g.add((ontology.AssociateProfessor, RDFS.label, Literal("AssociateProfessor", datatype=XSD.string)))
g.add((ontology.FullProfessor, RDFS.label, Literal("FullProfessor", datatype=XSD.string)))
g.add((ontology.InterimAssociateProfessor, RDFS.label, Literal("InterimAssociateProfessor", datatype=XSD.string)))

# Visualize the results
for s, p, o in g:
  print(s,p,o)


# In[17]:


# Validation. Do not remove
r.validate_task_06_01(g)


# **TASK 6.2: Add the 3 properties shown in slide 36. Add labels for each of them (exactly as they are in the slide, with no language tags), and their corresponding domains and ranges using RDFS. Remember adding the correct datatype (xsd:String) when appropriate. If a property has no range, make it a literal (string)**

# In[18]:


# TO DO

g.add((ontology.hasName, RDF.type, RDF.Property))
g.add((ontology.hasName, RDFS.label, Literal("hasName", datatype=XSD.string)))
g.add((ontology.hasName, RDFS.domain, ontology.Person))
g.add((ontology.hasName, RDFS.range, RDFS.Literal))

g.add((ontology.hasColleague, RDF.type, RDF.Property))
g.add((ontology.hasColleague, RDFS.label, Literal("hasColleague", datatype=XSD.string)))
g.add((ontology.hasColleague, RDFS.domain, ontology.Person))
g.add((ontology.hasColleague, RDFS.range, ontology.Person))

g.add((ontology.hasHomePage, RDF.type, RDF.Property))
g.add((ontology.hasHomePage, RDFS.label, Literal("hasHomePage", datatype=XSD.string)))
g.add((ontology.hasHomePage, RDFS.domain, ontology.FullProfessor))
g.add((ontology.hasHomePage, RDFS.range, RDFS.Literal))


# Visualize the results
for s, p, o in g:
  print(s,p,o)


# In[19]:


# Validation. Do not remove
r.validate_task_06_02(g)


# **TASK 6.3: Create the individuals shown in slide 36 under "Datos". Link them with the same relationships shown in the diagram."**

# In[20]:


# TO DO
g.add((person.Asun,  RDF.type, ontology.FullProfessor))
g.add((person.Asun,  RDFS.label, Literal("Asun", datatype=XSD.string)))
g.add((person.Asun, ontology.hasHomePage, Literal("http://oeg.fi.upm.es/", datatype=XSD.string)))

g.add((person.Raul,  RDF.type, ontology.InterimAssociateProfessor))
g.add((person.Raul,  RDFS.label, Literal("Raul", datatype=XSD.string)))

g.add((person.Oscar, RDF.type, ontology.AssociateProfessor))
g.add((person.Oscar, RDFS.label, Literal("Oscar", datatype=XSD.string)))
g.add((person.Oscar, ontology.hasName, Literal("Oscar Corcho García", datatype=XSD.string)))

g.add((person.Oscar, ontology.hasColleague, person.Asun))
g.add((person.Asun, ontology.hasColleague, person.Raul))


# Visualize the results
for s, p, o in g:
  print(s,p,o)


# In[21]:


r.validate_task_06_03(g)


# **TASK 6.4: Add to the individual person:Oscar the email address, given and family names. Use the properties already included in example 4 to describe Jane and John (https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials/rdf/example4.rdf). Do not import the namespaces, add them manually**
# 

# In[22]:


# TO DO

foaf = Namespace("http://xmlns.com/foaf/0.1/")
vcard = Namespace("http://www.w3.org/2001/vcard-rdf/3.0/")

# Añadir a person:Oscar
g.add((person.Oscar, foaf.email, Literal("mailto:ocorcho@fi.upm.es")))
g.add((person.Oscar, vcard.Given, Literal("Oscar", datatype=XSD.string)))
g.add((person.Oscar, vcard.Family, Literal("Corcho", datatype=XSD.string)))

# Visualize the results
for s, p, o in g:
  print(s,p,o)


# In[23]:


# Validation. Do not remove
r.validate_task_06_04(g)
r.save_report("_Task_06")


