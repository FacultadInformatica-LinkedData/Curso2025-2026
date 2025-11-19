from rdflib import Graph

g = Graph()
g.parse("MadridEvents.rdf.ttl", format="turtle")
print(f"Loaded RDF with {len(g)} triples\n")


query1 = """
PREFIX mm:  <http://movemadrid.org/ontology/movilidad#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>

SELECT ?event ?title ?starts ?ends ?facilityName ?districtLabel
WHERE {
  ?event a mm:Event ;
         mm:eventTitle ?title .
  OPTIONAL { ?event mm:startsOnDate ?starts . }
  OPTIONAL { ?event mm:endsOnDate   ?ends   . }
  OPTIONAL {
    ?event mm:eventFacility ?facility .
    ?facility mm:facilityName ?facilityName .
    OPTIONAL {
      ?facility mm:facilityDistrict ?district .
      ?district rdfs:label ?districtLabel .
    }
  }
}
LIMIT 10
"""

query2 = """
PREFIX mm:  <http://movemadrid.org/ontology/movilidad#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>

SELECT ?event ?title ?starts
WHERE {
  ?event a mm:Event ;
         mm:eventTitle ?title ;
         mm:freeEvent ?free .
  OPTIONAL { ?event mm:startsOnDate ?starts . }
  FILTER(xsd:boolean(?free) = true)
}
LIMIT 10
"""

query3 = """
PREFIX mm:  <http://movemadrid.org/ontology/movilidad#>

SELECT ?eventType (COUNT(?event) AS ?count)
WHERE {
  ?event a mm:Event ;
         mm:eventType ?eventType .
}
GROUP BY ?eventType
ORDER BY DESC(?count)
"""

query4 = """
PREFIX mm:  <http://movemadrid.org/ontology/movilidad#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?event ?title ?starts ?facilityName
WHERE {
  ?event a mm:Event ;
         mm:eventTitle ?title .
  OPTIONAL { ?event mm:startsOnDate ?starts . }
  OPTIONAL {
    ?event mm:eventFacility ?facility .
    ?facility mm:facilityName ?facilityName ;
              mm:facilityDistrict ?district .
    ?district rdfs:label ?districtLabel .
    FILTER(LCASE(STR(?districtLabel)) = "arganzuela")
  }
}
ORDER BY ?starts
LIMIT 10
"""

queries = [query1, query2, query3, query4]
names = ["Eventos básicos", "Eventos gratuitos", "Eventos por tipo", "Eventos en Arganzuela"]

for name, q in zip(names, queries):
    print(f"\n🔹 {name}:\n")
    results = g.query(q)
    for row in results:
        print(row)
    print("-" * 80)