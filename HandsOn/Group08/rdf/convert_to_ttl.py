from rdflib import Graph

g = Graph()
g.parse("output.nt", format="nt")
g.serialize("output.ttl", format="turtle")
