#%% md
# **Task 06: Modifying RDF(s)**
#%%
import urllib.request
url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"
#%% md
# Import RDFLib main methods
#%%
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS
from Assignment4.Diego_Ortega_Martinez_707214.validation import Report
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
r = Report()
#%% md
# Create a new class named Researcher
#%%
ns = Namespace("http://mydomain.org#")
g.add((ns.Researcher, RDF.type, RDFS.Class))
for s, p, o in g:
  print(s,p,o)
#%% md
# **Task 6.0: Create new prefixes for "ontology" and "person" as shown in slide 14 of the Slidedeck 01a.RDF(s)-SPARQL shown in class.**
#%%
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

g = Graph()


person     = Namespace("http://oeg.fi.upm.es/resource/person/")
organization = Namespace("http://oeg.fi.upm.es/resource/organization/")
ontology   = Namespace("http://oeg.fi.upm.es/def/people#")


g.namespace_manager.bind("person", person, override=False)
g.namespace_manager.bind("organization", organization, override=False)   # optional
g.namespace_manager.bind("ontology", ontology, override=False)
g.namespace_manager.bind("rdf", RDF); g.namespace_manager.bind("rdfs", RDFS)
g.namespace_manager.bind("xsd", XSD)


g.add((person.Raul, ontology.hasFullName, Literal("Raúl García Castro")))
g.add((person.Raul, ontology.hasBirthDate, Literal("1975-12-26", datatype=XSD.date)))
g.add((person.Raul, ontology.isMemberOf, organization.OEG))
g.add((person.Raul, ontology.hasWebPage, URIRef("http://oeg.fi.upm.es/")))

ttl = g.serialize(format="turtle")
print(ttl.decode() if isinstance(ttl, (bytes, bytearray)) else ttl)
#%% md
# **TASK 6.1: Reproduce the taxonomy of classes shown in slide 34 in class (all the classes under "Vocabulario", Slidedeck: 01a.RDF(s)-SPARQL). Add labels for each of them as they are in the diagram (exactly) with no language tags. Remember adding the correct datatype (xsd:String) when appropriate**
# 
#%%
from rdflib import Literal
from rdflib.namespace import RDF, RDFS, XSD


for cls, parent in [
    ("Person", None),
    ("Professor", "Person"),
    ("AssociateProfessor", "Professor"),
    ("FullProfessor", "Professor"),
    ("InterimAssociateProfessor", "AssociateProfessor"),
]:
    c = ontology[cls]
    g.add((c, RDF.type, RDFS.Class))
    g.add((c, RDFS.label, Literal(cls, datatype=XSD.string)))
    if parent:
        g.add((c, RDFS.subClassOf, ontology[parent]))

for s, p, o in g:
    print(s, p, o)

#%%
# Validation. Do not remove
r.validate_task_06_01(g)
#%% md
# **TASK 6.2: Add the 3 properties shown in slide 36. Add labels for each of them (exactly as they are in the slide, with no language tags), and their corresponding domains and ranges using RDFS. Remember adding the correct datatype (xsd:String) when appropriate. If a property has no range, make it a literal (string)**
#%%
from rdflib import Literal
from rdflib.namespace import RDF, RDFS, XSD

p = ontology.hasColleague

g.remove((p, RDFS.domain, None))
g.remove((p, RDFS.range,  None))
g.remove((p, RDF.type,    None))
g.remove((p, RDFS.label,  None))

g.add((p, RDF.type, RDF.Property))
g.add((p, RDFS.label,  Literal("hasColleague", datatype=XSD.string)))
g.add((p, RDFS.domain, ontology.Person))
g.add((p, RDFS.range,  ontology.Person))

for s, p, o in g:
    print(s, p, o)

#%%
# Validation. Do not remove
r.validate_task_06_02(g)
#%% md
# **TASK 6.3: Create the individuals shown in slide 36 under "Datos". Link them with the same relationships shown in the diagram."**
#%%
from rdflib import Namespace, Literal
from rdflib.namespace import RDF, RDFS, XSD


person       = Namespace("http://oeg.fi.upm.es/resource/person/")
organization = Namespace("http://oeg.fi.upm.es/resource/organization/")
ontology     = Namespace("http://oeg.fi.upm.es/def/people#")

g.namespace_manager.bind("person", person, override=True)
g.namespace_manager.bind("organization", organization, override=True)
g.namespace_manager.bind("ontology", ontology, override=True)


for i in (person.Oscar, person.Asun, person.Raul):
    g.remove((i, None, None))


g.add((person.Oscar, RDF.type, ontology.Person))
g.add((person.Oscar, RDFS.label, Literal("Oscar", datatype=XSD.string)))

g.add((person.Asun,  RDF.type, ontology.FullProfessor))
g.add((person.Asun,  RDFS.label, Literal("Asun", datatype=XSD.string)))

g.add((person.Raul,  RDF.type, ontology.InterimAssociateProfessor))
g.add((person.Raul,  RDFS.label, Literal("Raul", datatype=XSD.string)))


g.add((person.Oscar, ontology.hasName,
       Literal("Óscar Corcho García", datatype=XSD.string)))

g.add((person.Asun, ontology.hasHomePage,
       Literal("http://oeg.fi.upm.es/", datatype=XSD.string)))

g.add((person.Oscar, ontology.hasColleague, person.Asun))
g.add((person.Asun,  ontology.hasColleague, person.Raul))

# Visualize the results
for s, p, o in g:
  print(s,p,o)
#%%
r.validate_task_06_03(g)
#%% md
# **TASK 6.4: Add to the individual person:Oscar the email address, given and family names. Use the properties already included in example 4 to describe Jane and John (https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials/rdf/example4.rdf). Do not import the namespaces, add them manually**
# 
#%%
from rdflib import Namespace, Literal
from rdflib.namespace import XSD

# Namespaces manuell anlegen (wie in example4.rdf)
foaf  = Namespace("http://xmlns.com/foaf/0.1/")
vcard = Namespace("http://www.w3.org/2001/vcard-rdf/3.0/")

# (optional für schöne Turtle-Ausgabe)
g.namespace_manager.bind("foaf", foaf, override=False)
g.namespace_manager.bind("vcard-rdf", vcard, override=False)

# Werte für Oscar setzen (Strings ohne Sprach-Tag)
g.add((person.Oscar, foaf.email,     Literal("oscar@example.com", datatype=XSD.string)))
g.add((person.Oscar, vcard.Given,    Literal("Oscar",             datatype=XSD.string)))
g.add((person.Oscar, vcard.Family,   Literal("Corcho",            datatype=XSD.string)))
# Visualize the results
for s, p, o in g:
  print(s,p,o)
#%%
# Validation. Do not remove
r.validate_task_06_04(g)
r.save_report("_Task_06")
#%% md
# 