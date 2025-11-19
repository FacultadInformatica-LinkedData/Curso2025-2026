#!pip install rdflib
#from google.colab import files
#uploaded = files.upload() #this was run on jupyter notebook

from rdflib import Graph, Namespace
g = Graph()
g.parse("BikeParkingmapping_withLinks.rdf.ttl", format="turtle")

mm = Namespace("http://movemadrid.org/ontology/movilidad#")


print("querie con distritos")
q_district = """
PREFIX mm: <http://movemadrid.org/ontology/movilidad#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?parking ?lat ?long ?districtLiteral ?districtWD
WHERE {
  ?parking a mm:BicycleParking ;
           mm:bicycleParkingLatitude ?lat ;
           mm:bicycleParkingLongitude ?long ;
           mm:facilityDistrict ?districtLiteral ;
           mm:facilityDistrict ?districtWD .
  FILTER(isLiteral(?districtLiteral))
  FILTER(isIRI(?districtWD))
}
LIMIT 10
"""
for row in g.query(q_district):
    print(f"{row['parking']} → ({row['lat']}, {row['long']}) → {row['districtLiteral']} / {row['districtWD']}")

print("querie con barrios")
q_neighborhood = """
PREFIX mm: <http://movemadrid.org/ontology/movilidad#>
SELECT ?parking ?lat ?long ?neighborhoodLiteral ?neighborhoodWD
WHERE {
  ?parking a mm:BicycleParking ;
           mm:bicycleParkingLatitude ?lat ;
           mm:bicycleParkingLongitude ?long ;
           mm:facilityNeighborhood ?neighborhoodLiteral ;
           mm:facilityNeighborhood ?neighborhoodWD .
  FILTER(isLiteral(?neighborhoodLiteral))
  FILTER(isIRI(?neighborhoodWD))
}
LIMIT 10
"""
for row in g.query(q_neighborhood):
    print(f"{row['parking']} → ({row['lat']}, {row['long']}) → {row['neighborhoodLiteral']} / {row['neighborhoodWD']}")

print("querie con distritos y barrios")
q_both = """
PREFIX mm: <http://movemadrid.org/ontology/movilidad#>
SELECT ?parking ?lat ?long ?districtLiteral ?districtWD ?neighborhoodLiteral ?neighborhoodWD
WHERE {
  ?parking a mm:BicycleParking ;
           mm:bicycleParkingLatitude ?lat ;
           mm:bicycleParkingLongitude ?long ;
           mm:facilityDistrict ?districtLiteral ;
           mm:facilityDistrict ?districtWD ;
           mm:facilityNeighborhood ?neighborhoodLiteral ;
           mm:facilityNeighborhood ?neighborhoodWD .
  FILTER(isLiteral(?districtLiteral))
  FILTER(isIRI(?districtWD))
  FILTER(isLiteral(?neighborhoodLiteral))
  FILTER(isIRI(?neighborhoodWD))
}
LIMIT 10
"""
for row in g.query(q_both):
    print(f"{row['parking']} → ({row['lat']}, {row['long']}) → {row['districtLiteral']} / {row['districtWD']} → {row['neighborhoodLiteral']} / {row['neighborhoodWD']}")
