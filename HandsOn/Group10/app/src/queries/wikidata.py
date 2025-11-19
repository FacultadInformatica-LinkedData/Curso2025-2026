from SPARQLWrapper import SPARQLWrapper, JSON

def fetch_wikidata_stations():
    endpoint = SPARQLWrapper("https://query.wikidata.org/sparql")

    query = """
    SELECT ?station ?stationLabel ?lat ?lon WHERE {
      ?station wdt:P625 ?coord .
      ?station wdt:P131 wd:Q2807 .   # Madrid
      SERVICE wikibase:label { bd:serviceParam wikibase:language "es". }
      BIND(geof:latitude(?coord) AS ?lat)
      BIND(geof:longitude(?coord) AS ?lon)
    }
    """

    endpoint.setQuery(query)
    endpoint.setReturnFormat(JSON)
    data = endpoint.query().convert()

    results = []
    for r in data["results"]["bindings"]:
        results.append({
            "uri": r["station"]["value"],
            "label": r["stationLabel"]["value"],
            "lat": float(r["lat"]["value"]),
            "lon": float(r["lon"]["value"]),
        })

    return results
