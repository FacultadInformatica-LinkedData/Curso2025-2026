from rdflib import Graph
g = Graph()
g.parse("PublicParking_with-links.rdf.ttl", format="turtle")  # tu RDF corregido
print(f"Triples cargados: {len(g)}\n")

# QUERY 1 – Lista de aparcamientos con nombre
query1 = """
PREFIX mm: <http://movemadrid.org/ontology/movilidad#>

SELECT ?parking ?name
WHERE {
  ?parking a mm:CarParking ;
           mm:carParkingName ?name .
}
ORDER BY ?name
"""

print("--- QUERY 1: Aparcamientos con nombre ---")
for row in g.query(query1):
    print(f"{row.parking} → {row.name}")
print("\n")

# QUERY 2 – Nombre, coordenadas y link
query2 = """
PREFIX mm: <http://movemadrid.org/ontology/movilidad#>

SELECT ?parking ?name ?lat ?long ?link
WHERE {
  ?parking a mm:CarParking ;
           mm:carParkingName ?name .
  OPTIONAL { ?parking mm:carParkingLatitude ?lat . }
  OPTIONAL { ?parking mm:carParkingLongitude ?long . }
  OPTIONAL { ?parking mm:carParkingLink ?link . }
}
ORDER BY ?name
"""

print("--- QUERY 2: Coordenadas y link ---")
for row in g.query(query2):
    print(f"{row.name} | lat={row.lat} | long={row.long} | link={row.link}")
print("\n")

# QUERY 3 – Aparcamientos por distrito
query3 = """
PREFIX mm: <http://movemadrid.org/ontology/movilidad#>

SELECT ?parking ?name ?district
WHERE {
  ?parking a mm:CarParking ;
           mm:carParkingName ?name ;
           mm:facilityDistrict ?district .
  FILTER(str(?district) = "USERA")
}
ORDER BY ?name
"""

print("--- QUERY 3: Aparcamientos en USERA ---")
for row in g.query(query3):
    print(f"{row.name} ({row.district})")
print("\n")

# QUERY 4 – Extraer número de plazas desde la descripción
query4 = """
PREFIX mm: <http://movemadrid.org/ontology/movilidad#>

SELECT ?parking ?name ?desc
WHERE {
  ?parking a mm:CarParking ;
           mm:carParkingName ?name ;
           mm:carParkingDescription ?desc .
  FILTER(CONTAINS(?desc, "Plazas:"))
}
LIMIT 10
"""

print("--- QUERY 4: Número de plazas ---")
for row in g.query(query4):
    print(f"{row.name}: {row.desc}")
print("\n")

# QUERY A – Aparcamientos con barrios y links a Wikidata
query_a = """
PREFIX mm: <http://movemadrid.org/ontology/movilidad#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?parking ?name ?neighborhood ?neighborhoodWD
WHERE {
  ?parking a mm:CarParking ;
           mm:carParkingName ?name ;
           mm:facilityNeighborhood ?neighborhood .
  OPTIONAL { ?parking owl:sameAsNeighborhood ?neighborhoodWD }
}
ORDER BY ?neighborhood
"""

print("--- QUERY A: Aparcamientos con barrios y Wikidata ---")
for row in g.query(query_a):
    print(f"{row.name} | Barrio local: {row.neighborhood} | Barrio Wikidata: {row.neighborhoodWD}")
print("\n")

# QUERY B – Aparcamientos con distrito y links a Wikidata
query_b = """
PREFIX mm: <http://movemadrid.org/ontology/movilidad#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?parking ?name ?district ?districtWD
WHERE {
  ?parking a mm:CarParking ;
           mm:carParkingName ?name ;
           mm:facilityDistrict ?district .
  OPTIONAL { ?parking owl:sameAsDistrict ?districtWD }
}
ORDER BY ?district
"""

print("--- QUERY B: Aparcamientos con distrito y Wikidata ---")
for row in g.query(query_b):
    print(f"{row.name} | Distrito local: {row.district} | Distrito Wikidata: {row.districtWD}")
print("\n")

# QUERY C – Aparcamientos con barrio y distrito y ambos Wikidata
query_c = """
PREFIX mm: <http://movemadrid.org/ontology/movilidad#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?parking ?name ?neighborhood ?district ?neighborhoodWD ?districtWD
WHERE {
  ?parking a mm:CarParking ;
           mm:carParkingName ?name ;
           mm:facilityNeighborhood ?neighborhood ;
           mm:facilityDistrict ?district .
  OPTIONAL { ?parking owl:sameAsNeighborhood ?neighborhoodWD }
  OPTIONAL { ?parking owl:sameAsDistrict ?districtWD }
}
ORDER BY ?district ?neighborhood
"""

print("--- QUERY C: Aparcamientos con barrio y distrito y ambos Wikidata ---")
for row in g.query(query_c):
    print(f"{row.name} | Barrio: {row.neighborhood} → {row.neighborhoodWD} | Distrito: {row.district} → {row.districtWD}")
