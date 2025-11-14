from rdflib import Graph

g = Graph()
g.parse("group08-output.nt", format="nt")
g.serialize("group08-output.ttl", format="turtle")
