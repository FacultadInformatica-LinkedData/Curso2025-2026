from rdflib import Graph

g = Graph()
g.parse("output-with-links.nt", format="nt")
g.serialize("output-with-links.ttl", format="turtle")
