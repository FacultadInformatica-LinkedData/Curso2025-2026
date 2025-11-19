from flask import Flask, request, render_template_string
from rdflib import Graph
import json

# ============================================================
# 1) Load RDF graph (ontology + data WITH links)
# ============================================================

g = Graph()
g.parse("ontology/roadsafety-ontology.ttl", format="turtle")
g.parse("rdf/roadsafety-with-links.ttl", format="turtle")

print(f"Loaded triples: {len(g)}")

# Default query (accidents per district)
DEFAULT_QUERY = """
PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <https://schema.org/>

SELECT ?district ?label (COUNT(DISTINCT ?accident) AS ?numAccidents)
WHERE {
  ?accident rdf:type schema:Event ;
            schema:areaServed ?district .

  OPTIONAL { ?district rdfs:label ?label . }
}
GROUP BY ?district ?label
ORDER BY DESC(?numAccidents)
"""

# ============================================================
# Example SPARQL queries for the dropdown menu
# ============================================================

QUERY_EXAMPLES = {
    # 1) Basic ones
    "Accidents per district": DEFAULT_QUERY,

    "Top 20 accidents with most people involved": """
        PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX schema: <https://schema.org/>
        PREFIX ex:     <https://www.roadsafetydata.com/ontology#>

        SELECT ?accident (COUNT(DISTINCT ?person) AS ?numPersons)
        WHERE {
          ?accident rdf:type schema:Event ;
                    ex:involvesPerson ?person .
        }
        GROUP BY ?accident
        ORDER BY DESC(?numPersons)
        LIMIT 20
    """,

    "Vehicle types with owl:sameAs": """
        PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl:    <http://www.w3.org/2002/07/owl#>
        PREFIX schema: <https://schema.org/>

        SELECT ?vehType ?label ?sameAs
        WHERE {
          ?vehType rdf:type schema:Vehicle ;
                   owl:sameAs ?sameAs .
          OPTIONAL { ?vehType rdfs:label ?label . }
        }
        ORDER BY ?vehType
        LIMIT 20
    """,
    "Accidents with motorcyles involved": """PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX schema: <https://schema.org/>
        PREFIX ex:     <https://www.roadsafetydata.com/ontology#>

        SELECT ?district ?label (COUNT(DISTINCT ?acc) AS ?motorcycleAccidents)
        WHERE {
          ?acc a schema:Event ; schema:areaServed ?district ; ex:involvesPerson ?p .
          ?p ex:usesVehicleType ?veh .
          OPTIONAL { ?district rdfs:label ?label }
          OPTIONAL { ?veh rdfs:label ?vlabel }
          FILTER(LCASE(STR(?vlabel)) = "motorcycle")
        }
        GROUP BY ?district ?label
        ORDER BY DESC(?motorcycleAccidents)""",

    # 2) Accidents on a specific date
    "Accidents on 2025-01-01": """
        PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX schema: <https://schema.org/>

        SELECT ?accident ?date ?time
        WHERE {
          ?accident rdf:type schema:Event ;
                    schema:startDate ?date .
          OPTIONAL { ?accident schema:startTime ?time . }

          # Filter by date (yyyy-mm-dd prefix)
          FILTER(STRSTARTS(STR(?date), "2025-01-01"))
        }
        ORDER BY ?accident
        LIMIT 50
    """,

    # 3) Radars with high speed limit
    "Radars with speed limit ≥ 90": """
        PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX schema: <https://schema.org/>
        PREFIX ex:     <https://www.roadsafetydata.com/ontology#>

        SELECT ?radar ?road ?pk ?speed ?lon ?lat
        WHERE {
          ?radar rdf:type ex:SpeedCamera ;
                 ex:road ?road ;
                 ex:pk ?pk ;
                 ex:speedLimit ?speed .

          OPTIONAL { ?radar schema:longitude ?lon . }
          OPTIONAL { ?radar schema:latitude  ?lat . }

          FILTER(?speed >= 90)
        }
        ORDER BY ?road ?pk
        LIMIT 50
    """,

    # 4) Alcohol positives by age range
    "Positive alcohol tests by age range": """
        PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX schema: <https://schema.org/>
        PREFIX ex:     <https://www.roadsafetydata.com/ontology#>

        SELECT ?ageRange (COUNT(?person) AS ?numPersons)
        WHERE {
          ?person rdf:type schema:Person ;
                  ex:ageRange ?ageRange ;
                  ex:positiveAlcohol ?posAlcohol .

          FILTER(?posAlcohol = true)
        }
        GROUP BY ?ageRange
        ORDER BY ?ageRange
    """,
    # 3) Top 20 barrios más poblados (última fecha)
  "Top 20 neighbourhoods by population (latest)":
  """
  PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
  PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
  PREFIX schema: <https://schema.org/>
  PREFIX ex:     <https://www.roadsafetydata.com/ontology#>

  SELECT ?neighbourhood ?labelNeighbourhood ?district ?labelDistrict (SUM(?p) AS ?people) ?latestDate
  WHERE {
    { SELECT ?district (MAX(?d) AS ?latestDate)
      WHERE { ?obs a ex:PopulationObservation ; ex:forDistrict ?district ; schema:startDate ?d }
      GROUP BY ?district
    }
    ?obs a ex:PopulationObservation ;
         ex:forDistrict ?district ;
         ex:forNeighbourhood ?neighbourhood ;
         ex:peopleTotal ?p ;
         schema:startDate ?date .
    FILTER(?date = ?latestDate)
    OPTIONAL { ?district      rdfs:label ?labelDistrict }
    OPTIONAL { ?neighbourhood rdfs:label ?labelNeighbourhood }
  }
  GROUP BY ?neighbourhood ?labelNeighbourhood ?district ?labelDistrict ?latestDate
  ORDER BY DESC(?people)
  LIMIT 20
  """,

    # 5) SAMEAS – sex/gender values
    "Sex values with owl:sameAs": """
        PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl:    <http://www.w3.org/2002/07/owl#>
        PREFIX schema: <https://schema.org/>

        SELECT ?gender ?label ?sameAs
        WHERE {
          ?gender rdf:type schema:Enumeration ;
                  owl:sameAs ?sameAs .
          OPTIONAL { ?gender rdfs:label ?label . }
        }
        ORDER BY ?gender
    """,

    # 6) Population – sample of observations
    "Population observations (sample)": """
        PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX schema: <https://schema.org/>
        PREFIX ex:     <https://www.roadsafetydata.com/ontology#>

        SELECT ?obs ?district ?neighbourhood
               ?labelDistrict ?labelNeighbourhood
               ?people ?male ?female
        WHERE {
          ?obs rdf:type ex:PopulationObservation ;
               ex:forDistrict      ?district ;
               ex:forNeighbourhood ?neighbourhood ;
               ex:peopleTotal      ?people .

          OPTIONAL { ?district      rdfs:label ?labelDistrict . }
          OPTIONAL { ?neighbourhood rdfs:label ?labelNeighbourhood . }
          OPTIONAL { ?obs ex:peopleMale   ?male . }
          OPTIONAL { ?obs ex:peopleFemale ?female . }
        }
        LIMIT 20
    """,

    # 8) SAMEAS – links by class (summary)
    "owl:sameAs links by class": """
        PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl:  <http://www.w3.org/2002/07/owl#>

        SELECT ?class (COUNT(DISTINCT ?s) AS ?numResources)
        WHERE {
          ?s owl:sameAs ?o ;
             rdf:type   ?class .
        }
        GROUP BY ?class
        ORDER BY DESC(?numResources)
    """,
    #9) Accidents per district
    "Accident per district population": """
        PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX schema: <https://schema.org/>
        PREFIX ex:     <https://www.roadsafetydata.com/ontology#>

        SELECT ?district ?label ?peopleDistrict (COUNT(DISTINCT ?acc) AS ?nAccidentes)
        WHERE {
          {
            SELECT ?district (MAX(?p) AS ?peopleDistrict)
            WHERE {
              ?obs a ex:PopulationObservation ;
                  ex:forDistrict ?district ;
                  ex:peopleTotal ?p ;
                  schema:startDate ?pDate .
            }
            GROUP BY ?district
          }

          ?acc a schema:Event ; schema:areaServed ?district .
          OPTIONAL { ?district rdfs:label ?label }
        }
        GROUP BY ?district ?label ?peopleDistrict
        ORDER BY DESC(?nAccidentes)

    """, 
    #district with more accidents
    "District with more accidents": 
    """PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX schema: <https://schema.org/>

        SELECT ?district ?label (COUNT(DISTINCT ?accident) AS ?numAccidents)
        WHERE {
          ?accident rdf:type schema:Event ;
                    schema:areaServed ?district .

          OPTIONAL { ?district rdfs:label ?label }
        }
        GROUP BY ?district ?label
        ORDER BY DESC(?numAccidents)

        """, 
    "Radars per road (top)":
    """
      PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
      PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
      PREFIX schema: <https://schema.org/>
      PREFIX ex:     <https://www.roadsafetydata.com/ontology#>

      SELECT ?road ?label (COUNT(DISTINCT ?rad) AS ?numRadars)
      WHERE {
        ?rad a ex:SpeedCamera ; ex:road ?road .
        OPTIONAL { ?road rdfs:label ?label }
      }
      GROUP BY ?road ?label
      ORDER BY DESC(?numRadars) ?road
      LIMIT 30
      """
    , "Radars per responsible (top)":
    """
    PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX schema: <https://schema.org/>
    PREFIX ex:     <https://www.roadsafetydata.com/ontology#>

    SELECT ?resp ?name (COUNT(DISTINCT ?rad) AS ?numRadars)
    WHERE {
      ?rad a ex:SpeedCamera ;
           ex:responsible ?resp .
      OPTIONAL { ?resp schema:name ?name }
    }
    GROUP BY ?resp ?name
    ORDER BY DESC(?numRadars)
    LIMIT 30
    """
}

app = Flask(__name__)

# ============================================================
# 2) Simple, clean HTML template (query panel arriba, resultados abajo)
# ============================================================

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Road Safety – SPARQL Demo</title>
  <style>
    * { box-sizing: border-box; }

    body {
      margin: 0;
      padding: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f3f4f6;
      color: #111827;
    }

    .page {
      max-width: 1100px;
      margin: 0 auto;
      padding: 24px 16px 40px;
    }

    header {
      margin-bottom: 18px;
      padding-bottom: 12px;
      border-bottom: 1px solid #d1d5db;
    }

    header h1 {
      margin: 0 0 4px;
      font-size: 1.5rem;
    }

    header p {
      margin: 2px 0;
      font-size: 0.9rem;
      color: #4b5563;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 3px 9px;
      border-radius: 999px;
      background: #e5f3ff;
      color: #1d4ed8;
      font-size: 0.75rem;
      margin-bottom: 6px;
    }

    /* Panel arriba, resultados abajo */
    .layout {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .card {
      background: #ffffff;
      border-radius: 8px;
      border: 1px solid #e5e7eb;
      padding: 14px 16px 16px;
      box-shadow: 0 4px 12px rgba(15,23,42,0.06);
    }

    .card h2 {
      margin: 0 0 6px;
      font-size: 1.05rem;
    }

    .card small {
      color: #6b7280;
      font-size: 0.8rem;
    }

    label {
      font-size: 0.85rem;
      color: #4b5563;
    }

    select {
      width: 100%;
      margin: 6px 0 10px;
      padding: 6px 9px;
      border-radius: 6px;
      border: 1px solid #d1d5db;
      background: #ffffff;
      color: #111827;
      font-size: 0.85rem;
      outline: none;
    }

    select:focus {
      border-color: #2563eb;
      box-shadow: 0 0 0 1px rgba(37,99,235,0.25);
    }

    textarea {
      width: 100%;
      height: 220px;
      margin-top: 6px;
      padding: 8px 9px;
      border-radius: 6px;
      border: 1px solid #d1d5db;
      background: #f9fafb;
      color: #111827;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: 0.8rem;
      resize: vertical;
      outline: none;
      line-height: 1.4;
    }

    textarea:focus {
      border-color: #2563eb;
      box-shadow: 0 0 0 1px rgba(37,99,235,0.25);
      background: #ffffff;
    }

    button {
      margin-top: 10px;
      padding: 6px 14px;
      border-radius: 999px;
      border: 1px solid #2563eb;
      background: #2563eb;
      color: white;
      font-size: 0.85rem;
      font-weight: 500;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    button span {
      font-size: 0.9rem;
    }

    button:hover {
      background: #1d4ed8;
      border-color: #1d4ed8;
    }

    .error {
      color: #b91c1c;
      margin-top: 10px;
      font-size: 0.82rem;
    }

    .meta {
      color: #6b7280;
      font-size: 0.8rem;
      margin-bottom: 8px;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 6px;
      font-size: 0.8rem;
    }

    th, td {
      border: 1px solid #e5e7eb;
      padding: 5px 6px;
      text-align: left;
      max-width: 260px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    th {
      background: #f9fafb;
      color: #374151;
      font-weight: 500;
      font-size: 0.78rem;
    }

    tbody tr:nth-child(even) {
      background: #f9fafb;
    }

    tbody tr:nth-child(odd) {
      background: #ffffff;
    }

    tbody tr:hover {
      background: #e5f3ff;
    }

    .results-card {
      max-height: 480px;
      overflow: auto;
    }
  </style>
  <script>
    const queries = {{ examples_json | safe }};
    function loadExample() {
      const select = document.getElementById("exampleSelect");
      const name = select.value;
      if (name && queries[name]) {
        document.getElementById("query").value = queries[name];
      }
    }
  </script>
</head>
<body>
  <div class="page">
    <header>
      <div class="badge">
        Road Safety Linked Data · SPARQL demo
      </div>
      <h1>Road Safety – SPARQL Demo</h1>
      <p>Ontology + RDF data for Madrid road safety, exposed as a local SPARQL playground.</p>
      <p>Loaded triples: <strong>{{ num_triples }}</strong></p>
    </header>

    <div class="layout">
      <!-- ARRIBA: Query builder -->
      <div class="card">
        <h2>Query panel</h2>
        <small>Select an example or edit the SPARQL query.</small>

        <div style="margin-top: 12px;">
          <label for="exampleSelect"><strong>Query examples</strong></label>
          <select id="exampleSelect" onchange="loadExample()">
            <option value="">-- Select an example --</option>
            {% for name in example_names %}
              <option value="{{ name }}">{{ name }}</option>
            {% endfor %}
          </select>
        </div>

        <form method="post">
          <label for="query">SPARQL query</label>
          <textarea id="query" name="query">{{ query_text }}</textarea>
          <button type="submit">
            <span>▶</span> Run query
          </button>
        </form>

        {% if error %}
          <p class="error"><strong>Error:</strong> {{ error }}</p>
        {% endif %}
      </div>

      <!-- ABAJO: Results -->
      <div class="card results-card">
        <h2>Results</h2>
        {% if headers %}
          <p class="meta">Returned rows: {{ row_count }}</p>
          <table>
            <thead>
              <tr>
                {% for h in headers %}
                  <th>{{ h }}</th>
                {% endfor %}
              </tr>
            </thead>
            <tbody>
              {% for row in rows %}
                <tr>
                  {% for cell in row %}
                    <td title="{{ cell }}">{{ cell }}</td>
                  {% endfor %}
                </tr>
              {% endfor %}
            </tbody>
          </table>
        {% else %}
          <p class="meta">
            No results yet. Pick an example above and click <strong>Run query</strong>.
          </p>
        {% endif %}
      </div>
    </div>
  </div>
</body>
</html>
"""

# ============================================================
# 3) Main view
# ============================================================

@app.route("/", methods=["GET", "POST"])
def index():
    # Default query text
    query_text = DEFAULT_QUERY
    headers = []
    rows = []
    error = None

    if request.method == "POST":
        query_text = request.form.get("query", "")
        try:
            results = g.query(query_text)
            headers = [str(v) for v in results.vars]
            for r in results:
                rows.append([str(c) if c is not None else "" for c in r])
        except Exception as e:
            error = str(e)

    return render_template_string(
        HTML_TEMPLATE,
        num_triples=len(g),
        query_text=query_text,
        headers=headers,
        rows=rows,
        row_count=len(rows),
        error=error,
        example_names=list(QUERY_EXAMPLES.keys()),
        examples_json=json.dumps(QUERY_EXAMPLES),
    )

# ============================================================
# 4) Run the app
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)
