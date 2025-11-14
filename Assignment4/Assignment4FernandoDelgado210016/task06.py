# -*- coding: utf-8 -*-
""" Task06_2025.py Modifying RDF(s) for Assignment 4 """

# !pip install rdflib  # comentado para entrega
import urllib.request
from rdflib import Graph, Namespace, Literal, XSD
from rdflib.namespace import RDF, RDFS
from validation import Report

# Create the graph
g = Graph()
r = Report()

# ----------------------------
# Namespaces
# ----------------------------
ontology = Namespace("http://oeg.fi.upm.es/def/people#")
VCARD = Namespace("http://www.w3.org/2001/vcard-rdf/3.0/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

# Bind namespaces
g.namespace_manager.bind('ontology', ontology, override=False)
g.namespace_manager.bind('vcard', VCARD, override=False)
g.namespace_manager.bind('foaf', FOAF, override=False)

# ----------------------------
# Task 6.1: Classes taxonomy
# ----------------------------
Person = ontology.Person
Professor = ontology.Professor
AssociateProfessor = ontology.AssociateProfessor
InterimAssociateProfessor = ontology.InterimAssociateProfessor
FullProfessor = ontology.FullProfessor

classes = [Person, Professor, AssociateProfessor, InterimAssociateProfessor, FullProfessor]

# Add classes and labels
for c in classes:
    g.add((c, RDF.type, RDFS.Class))
    g.add((c, RDFS.label, Literal(c.split("#")[-1], datatype=XSD.string)))

# Hierarchy
g.add((Professor, RDFS.subClassOf, Person))
g.add((AssociateProfessor, RDFS.subClassOf, Professor))
g.add((InterimAssociateProfessor, RDFS.subClassOf, AssociateProfessor))
g.add((FullProfessor, RDFS.subClassOf, Professor))

# Validation
r.validate_task_06_01(g)

# ----------------------------
# Task 6.2: Properties
# ----------------------------
hasColleague = ontology.hasColleague
hasName = ontology.hasName
hasHomePage = ontology.hasHomePage

# hasColleague
g.add((hasColleague, RDF.type, RDF.Property))
g.add((hasColleague, RDFS.domain, Person))
g.add((hasColleague, RDFS.range, Person))
g.add((hasColleague, RDFS.label, Literal("hasColleague", datatype=XSD.string)))

# hasName
g.add((hasName, RDF.type, RDF.Property))
g.add((hasName, RDFS.domain, Person))
g.add((hasName, RDFS.range, RDFS.Literal))
g.add((hasName, RDFS.label, Literal("hasName", datatype=XSD.string)))

# hasHomePage
g.add((hasHomePage, RDF.type, RDF.Property))
g.add((hasHomePage, RDFS.domain, FullProfessor))
g.add((hasHomePage, RDFS.range, RDFS.Literal))
g.add((hasHomePage, RDFS.label, Literal("hasHomePage", datatype=XSD.string)))


# Validation
r.validate_task_06_02(g)

# ----------------------------
# Task 6.3: Individuals
# ----------------------------
Oscar = Namespace("http://oeg.fi.upm.es/resource/person/").Oscar
Asun = Namespace("http://oeg.fi.upm.es/resource/person/").Asun
Raul = Namespace("http://oeg.fi.upm.es/resource/person/").Raul

# Oscar
g.add((Oscar, RDF.type, Professor))
g.add((Oscar, RDFS.label, Literal("Oscar", datatype=XSD.string)))
g.add((Oscar, hasColleague, Asun))
g.add((Oscar, hasName, Literal("Oscar", datatype=XSD.string)))

# Asun
g.add((Asun, RDF.type, AssociateProfessor))
g.add((Asun, RDFS.label, Literal("Asun", datatype=XSD.string)))
g.add((Asun, hasColleague, Raul))
g.add((Asun, hasHomePage, Literal("asun_homepage", datatype=XSD.string)))

# Raul
g.add((Raul, RDF.type, InterimAssociateProfessor))
g.add((Raul, RDFS.label, Literal("Raul", datatype=XSD.string)))
g.add((Raul, hasColleague, Oscar))

# Validation
r.validate_task_06_03(g)

# ----------------------------
# Task 6.4: Oscar VCARD/FOAF properties
# ----------------------------
g.add((Oscar, VCARD.Given, Literal("Oscar", datatype=XSD.string)))
g.add((Oscar, VCARD.Family, Literal("Corcho", datatype=XSD.string)))  # apellido esperado por la validación
g.add((Oscar, FOAF.email, Literal("oscar@email.com", datatype=XSD.string)))

# Validation
r.validate_task_06_04(g)

# ----------------------------
# Save report
# ----------------------------
r.save_report("_Task_06")
