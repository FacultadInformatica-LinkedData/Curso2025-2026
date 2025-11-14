from rdflib import Graph

# Load RDF data
g = Graph()
g.parse("rdf/group08-output.ttl", format="turtle")
print("Triples loaded:", len(g))

# 1. Count resources with labels
print("\n1. Resources with labels:")
q1 = """
SELECT (COUNT(DISTINCT ?s) AS ?withLabel)
WHERE { ?s rdfs:label ?label . }
"""
for row in g.query(q1, initNs={'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'}):
    print(row)

# 2. Sample labels by class
print("\n2. Sample labels by class:")
q2 = """
SELECT ?class ?label
WHERE {
  ?s a ?class ;
     rdfs:label ?label .
}
LIMIT 10
"""
for row in g.query(q2, initNs={'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'}):
    print(row)

# 3. Count individuals without labels
print("\n3. Individuals without labels:")
q3 = """
SELECT (COUNT(DISTINCT ?s) AS ?withoutLabel)
WHERE {
  ?s a ?class .
  FILTER NOT EXISTS { ?s rdfs:label ?label }
}
"""
for row in g.query(q3, initNs={'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'}):
    print(row)

# 4. Label distribution by class
print("\n4. Label distribution by class:")
q4 = """
SELECT ?class (COUNT(DISTINCT ?s) AS ?count)
WHERE {
  ?s a ?class ;
     rdfs:label ?label .
}
GROUP BY ?class
ORDER BY DESC(?count)
"""
for row in g.query(q4, initNs={'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'}):
    print(row)

# 5. Check label readability (contains 'traffic')
print("\n5. Sample labels containing 'traffic':")
q5 = """
SELECT ?s ?label
WHERE {
  ?s rdfs:label ?label .
  FILTER(CONTAINS(LCASE(STR(?label)), "traffic"))
}
LIMIT 5
"""
for row in g.query(q5, initNs={'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'}):
    print(row)
