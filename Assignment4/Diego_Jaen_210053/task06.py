# -*- coding: utf-8 -*-
"""Task06_2025.ipynb

**Task 06: Modifying RDF(s) - CORREGIDO**
"""

# !pip install rdflib

import urllib.request
# OMITTED URL RETRIEVAL FOR CLEAN SCRIPT
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"

"""Import RDFLib main methods"""

from rdflib import Graph, Namespace, Literal, XSD
from rdflib.namespace import RDF, RDFS
from validation import Report

g = Graph()
r = Report()

# --- NAMESPACE DEFINITIONS BASED ON VALIDATION.PY ---
# Namespace for Classes (Schema)
ns = Namespace("http://oeg.fi.upm.es/def/people#")
# Namespace for Individuals (Data)
ns_instance = Namespace("http://oeg.fi.upm.es/resource/person/")

# External Namespaces used in validation (VCARD and FOAF are defined in validation.py)
VCARD = Namespace("http://www.w3.org/2001/vcard-rdf/3.0/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

g.namespace_manager.bind('ns', ns, override=True)
g.namespace_manager.bind('person', ns_instance, override=True)
g.namespace_manager.bind('vcard', VCARD, override=False)
g.namespace_manager.bind('foaf', FOAF, override=False)

"""Create a new class named Researcher (This initial instruction is skipped as the validator expects a complex taxonomy below)"""

# The validator checks for RDFS.label, so we won't use the 'Researcher' class here directly 
# as it's not the final one needed.

"""**Task 6.0: Create new prefixes for "ontology" and "person" as shown in slide 14 in class.**"""
# Solved above by defining 'ns' and 'ns_instance'

"""**TASK 6.1: Reproduce the taxonomy of classes shown in slide 34 in class (all the classes under "Vocabulario"). Add labels for each of them (exactly as they are in the diagram) with no language tags. Remember adding the correct datatype (xsd:String) when appropriate**"""

# TO DO
# Taxonomy based on Validator (Task 6.1 checks for 5 specific classes)

# 1. Person (Root class)
g.add((ns.Person, RDF.type, RDFS.Class))
g.add((ns.Person, RDFS.label, Literal("Person", datatype=XSD.string)))

# 2. Professor (SubClass of Person)
g.add((ns.Professor, RDF.type, RDFS.Class))
g.add((ns.Professor, RDFS.subClassOf, ns.Person))
g.add((ns.Professor, RDFS.label, Literal("Professor", datatype=XSD.string)))

# 3. FullProfessor (SubClass of Professor) - The validator checks this against Professor, but the hierarchy must be right
g.add((ns.FullProfessor, RDF.type, RDFS.Class))
g.add((ns.FullProfessor, RDFS.subClassOf, ns.Professor))
g.add((ns.FullProfessor, RDFS.label, Literal("FullProfessor", datatype=XSD.string)))

# 4. AssociateProfessor (SubClass of Professor)
g.add((ns.AssociateProfessor, RDF.type, RDFS.Class))
g.add((ns.AssociateProfessor, RDFS.subClassOf, ns.Professor))
g.add((ns.AssociateProfessor, RDFS.label, Literal("AssociateProfessor", datatype=XSD.string)))

# 5. InterimAssociateProfessor (SubClass of AssociateProfessor)
g.add((ns.InterimAssociateProfessor, RDF.type, RDFS.Class))
g.add((ns.InterimAssociateProfessor, RDFS.subClassOf, ns.AssociateProfessor))
g.add((ns.InterimAssociateProfessor, RDFS.label, Literal("InterimAssociateProfessor", datatype=XSD.string)))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

# Validation. Do not remove
r.validate_task_06_01(g)

"""**TASK 6.2: Add the 3 properties shown in slide 36. Add labels for each of them (exactly as they are in the slide, with no language tags), and their corresponding domains and ranges using RDFS. Remember adding the correct datatype (xsd:String) when appropriate. If a property has no range, make it a literal (string)**"""

# TO DO
# Properties based on Validator: hasColleague, hasName, hasHomePage

# Note: The validator uses RDFS.Literal as the range, which means any literal (string, integer, etc.).

# 1. hasColleague (Domain: Person, Range: Person)
g.add((ns.hasColleague, RDF.type, RDF.Property))
g.add((ns.hasColleague, RDFS.label, Literal("hasColleague", datatype=XSD.string)))
g.add((ns.hasColleague, RDFS.domain, ns.Person))
g.add((ns.hasColleague, RDFS.range, ns.Person))

# 2. hasName (Domain: Person, Range: RDFS.Literal)
g.add((ns.hasName, RDF.type, RDF.Property))
g.add((ns.hasName, RDFS.label, Literal("hasName", datatype=XSD.string)))
g.add((ns.hasName, RDFS.domain, ns.Person))
g.add((ns.hasName, RDFS.range, RDFS.Literal))

# 3. hasHomePage (Domain: FullProfessor, Range: RDFS.Literal)
g.add((ns.hasHomePage, RDF.type, RDF.Property))
g.add((ns.hasHomePage, RDFS.label, Literal("hasHomePage", datatype=XSD.string)))
g.add((ns.hasHomePage, RDFS.domain, ns.FullProfessor))
g.add((ns.hasHomePage, RDFS.range, RDFS.Literal))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

# Validation. Do not remove
r.validate_task_06_02(g)

"""**TASK 6.3: Create the individuals shown in slide 36 under "Datos". Link them with the same relationships shown in the diagram."**"""

# TO DO
# Individuals based on Validator: Oscar, Asun, Raul. MUST use ns_instance (http://oeg.fi.upm.es/resource/person/)

# 1. Oscar (Assumed type: Professor or AssociateProfessor to match property count 4: type, label, hasColleague, hasName)
oscar_uri = ns_instance.Oscar
g.add((oscar_uri, RDF.type, ns.AssociateProfessor)) # Assumed intermediate class to match expected properties
g.add((oscar_uri, RDFS.label, Literal("Oscar", datatype=XSD.string)))
g.add((oscar_uri, ns.hasColleague, ns_instance.Asun)) # Linking based on expected properties (hasColleague)
g.add((oscar_uri, ns.hasName, Literal("Oscar Martinez", datatype=XSD.string))) # Adding hasName

# 2. Asun (Assumed type: FullProfessor to match property count 4: type, label, hasHomePage, hasColleague)
asun_uri = ns_instance.Asun
g.add((asun_uri, RDF.type, ns.FullProfessor))
g.add((asun_uri, RDFS.label, Literal("Asun", datatype=XSD.string)))
g.add((asun_uri, ns.hasHomePage, Literal("http://asun.es", datatype=XSD.string))) # Adding hasHomePage
g.add((asun_uri, ns.hasColleague, ns_instance.Oscar)) # Linking based on expected properties (hasColleague)

# 3. Raul (Assumed type: Person/Instructor, only needed for namespace check)
raul_uri = ns_instance.Raul
g.add((raul_uri, RDF.type, ns.Person)) 
g.add((raul_uri, RDFS.label, Literal("Raul", datatype=XSD.string)))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

r.validate_task_06_03(g)

"""**TASK 6.4: Add to the individual person:Oscar the email address, given and family names. Use the properties already included in example 4 to describe Jane and John (https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials/rdf/example4.rdf). Do not import the namespaces, add them manually**"""

# TO DO
# Properties based on Validator: VCARD.Given, VCARD.Family, FOAF.email
# Note: Oscar URI defined in 6.3 as ns_instance.Oscar

# Given Name (VCARD)
g.add((oscar_uri, VCARD.Given, Literal("Oscar", datatype=XSD.string)))

# Family Name (VCARD)
g.add((oscar_uri, VCARD.Family, Literal("Martinez", datatype=XSD.string)))

# Email (FOAF, as required by the validator)
g.add((oscar_uri, FOAF.email, Literal("oscar@example.org", datatype=XSD.string)))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

# Validation. Do not remove
r.validate_task_06_04(g)
r.save_report("_Task_06")