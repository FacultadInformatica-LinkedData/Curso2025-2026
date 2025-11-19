from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef
g = Graph()
g.parse("MadridEvents-with-links.rdf.ttl", format="turtle")
mm = Namespace("http://movemadrid.org/ontology/movilidad#")

# LISTAR TODOS LOS DISTRITOS
print("\n🔹 LISTA DE DISTRITOS:\n" + "-"*80)
q1 = """
SELECT ?district ?label
WHERE {
  ?district a <http://movemadrid.org/ontology/movilidad#District> ;
            rdfs:label ?label .
}
ORDER BY ?label
"""
for row in g.query(q1):
    print(row["district"], "-", row["label"])

# LISTAR TODOS LOS BARRIOS CON SU DISTRITO
print("\n🔹 BARRIOS Y SU DISTRITO:\n" + "-"*80)
q2 = """
SELECT ?neighborhood ?nLabel ?district ?dLabel
WHERE {
  ?neighborhood a <http://movemadrid.org/ontology/movilidad#Neighborhood> ;
                rdfs:label ?nLabel ;
                <http://movemadrid.org/ontology/movilidad#inDistrict> ?district .
  ?district rdfs:label ?dLabel .
}
ORDER BY ?dLabel ?nLabel
"""
for row in g.query(q2):
    print(f"{row['nLabel']} → {row['dLabel']}")

# CONTEO DE ENTIDADES POR TIPO (District y Neighborhood)
print("\n🔹 CONTEO TOTAL DE ENTIDADES:\n" + "-"*80)
for entity_type in [mm.District, mm.Neighborhood]:
    q_count = f"""
    SELECT (COUNT(?s) AS ?count)
    WHERE {{ ?s a <{entity_type}>. }}
    """
    for row in g.query(q_count):
        print(f"{entity_type.split('#')[-1]}:", row["count"])
print("-"*80)

# DISTRITOS / BARRIOS CON ENLACE A WIKIDATA (owl:sameAs)
print("\n🔹 DISTRITOS/BARRIOS LINKEADOS A WIKIDATA:\n" + "-"*80)
q_linked = """
SELECT ?entity ?label ?wikidata
WHERE {
  ?entity a ?type ;
           rdfs:label ?label ;
           owl:sameAs ?wikidata .
  FILTER(CONTAINS(STR(?wikidata), "wikidata.org"))
}
ORDER BY ?label
"""
linked = list(g.query(q_linked))
if linked:
    for row in linked:
        print(f"{row['label']} → {row['wikidata']}")
else:
    print("⚠️ No se encontraron entidades con owl:sameAs hacia Wikidata.")
print("-"*80)

# DISTRITOS / BARRIOS SIN ENLACE owl:sameAs
print("\n🔹 ENTIDADES SIN SAMEAS:\n" + "-"*80)
q_no_linked = """
SELECT ?entity ?label
WHERE {
  ?entity a ?type ;
           rdfs:label ?label .
  FILTER NOT EXISTS { ?entity owl:sameAs ?wikidata }
}
ORDER BY ?label
"""
no_linked = list(g.query(q_no_linked))
if no_linked:
    for row in no_linked:
        print(row["entity"], "-", row["label"])
else:
    print("✅ Todas las entidades tienen enlace owl:sameAs.")
print("-"*80)

# EJEMPLO: CONSULTA DE UN DISTRITO Y SUS BARRIOS (PARA PRUEBA)
print("\n🔹 EJEMPLO: BARRIOS EN EL DISTRITO 'Ciudad Lineal'\n" + "-"*80)
q_example = """
SELECT ?nLabel
WHERE {
  ?n a <http://movemadrid.org/ontology/movilidad#Neighborhood> ;
      rdfs:label ?nLabel ;
      <http://movemadrid.org/ontology/movilidad#inDistrict> ?d .
  ?d rdfs:label "Ciudad Lineal" .
}
ORDER BY ?nLabel
"""
for row in g.query(q_example):
    print(row["nLabel"])
print("-"*80)