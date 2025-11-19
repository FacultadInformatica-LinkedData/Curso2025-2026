from rdflib import Graph

def load_graph():
    g = Graph()
    g.parse("data/alertas-with-links.ttl", format="turtle")
    return g
