# backend/app.py - FastAPI endpoints
from pathlib import Path
from typing import Optional, List
from collections import defaultdict, deque

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import httpx
from contextlib import asynccontextmanager

from utils import query_sparql, parse_point_wkt, parse_multilinestring_wkt, SPARQL_ENDPOINT

# Obtener la ruta absoluta del directorio frontend
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
RESOURCES_DIR = BASE_DIR / "resources"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código al iniciar
    yield
    # Código al cerrar (limpieza)
    pass


app = FastAPI(
    title="Metro Barcelona API",
    description="API REST para consultar datos del metro de Barcelona mediante SPARQL",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class SparqlQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Consulta SPARQL")
    format: str = Field(
        default="application/sparql-results+json",
        description="Formato de respuesta"
    )

class HealthResponse(BaseModel):
    backend: str
    sparql_endpoint: str
    sparql_status: str

class StationResponse(BaseModel):
    id: str
    name: str
    latitude: Optional[float]
    longitude: Optional[float]
    lines: List[str]

class LineResponse(BaseModel):
    id: str
    code: str
    name: str
    color: str
    auxColor: Optional[str]
    origin: Optional[str]
    destination: Optional[str]
    numStations: int

class ExampleQuery(BaseModel):
    name: str
    description: str
    query: str

class RouteRequest(BaseModel):
    origin: str = Field(..., description="Nombre de estación origen")
    destination: str = Field(..., description="Nombre de estación destino")


# Endpoints
@app.get("/", include_in_schema=False)
async def index():
    """Sirve la página principal"""
    return FileResponse(FRONTEND_DIR / "index.html")


@app.post("/api/query")
async def proxy_sparql(body: SparqlQueryRequest):
    """
    Ejecuta una consulta SPARQL y devuelve los resultados
    """
    result = await query_sparql(body.query, body.format)
    return result


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Verifica el estado del backend y del endpoint SPARQL"""
    status = {
        "backend": "ok",
        "sparql_endpoint": SPARQL_ENDPOINT,
        "sparql_status": "unknown"
    }
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(SPARQL_ENDPOINT.replace("/sparql", "/$/ping"))
            status["sparql_status"] = "connected" if resp.status_code == 200 else "unreachable"
    except:
        status["sparql_status"] = "unreachable"
    
    return status


@app.get("/api/stations", response_model=List[StationResponse])
async def get_stations():
    """Obtiene todas las estaciones con sus coordenadas y líneas"""
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX metro: <https://data.example.org/transport/bcn/metro/ontology#>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    
    SELECT ?station ?name ?geometry
           (GROUP_CONCAT(DISTINCT ?lineCode; separator=",") AS ?lines)
    WHERE {
      ?station rdf:type metro:Station .
      ?station rdfs:label ?name .
      OPTIONAL { ?station metro:hasGeometry ?geometry }
      OPTIONAL { 
        ?stationLine metro:relatesTo ?station .
        ?stationLine metro:onLine ?line .
        ?line metro:lineCode ?lineCode
      }
    }
    GROUP BY ?station ?name ?geometry
    """
    
    data = await query_sparql(query)
    
    stations = []
    for binding in data.get("results", {}).get("bindings", []):
        geometry_wkt = binding.get("geometry", {}).get("value", "")
        coords = parse_point_wkt(geometry_wkt)
        
        if coords:
            station = StationResponse(
                id=binding.get("station", {}).get("value", ""),
                name=binding.get("name", {}).get("value", ""),
                latitude=coords["lat"],
                longitude=coords["lng"],
                lines=binding.get("lines", {}).get("value", "").split(",") if binding.get("lines") else []
            )
            stations.append(station)
    
    return stations


@app.get("/api/lines", response_model=List[LineResponse])
async def get_lines():
    """Obtiene todas las líneas con información"""
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX metro: <https://data.example.org/transport/bcn/metro/ontology#>
    
    SELECT ?line ?lineCode ?lineName ?lineColor ?auxColor ?origin ?destination
           (COUNT(DISTINCT ?station) AS ?numStations)
    WHERE {
      ?line rdf:type metro:MetroLine .
      ?line metro:lineCode ?lineCode .
      OPTIONAL { ?line metro:lineName ?lineName }
      OPTIONAL { ?line metro:lineColor ?lineColor }
      OPTIONAL { ?line metro:auxiliaryColor ?auxColor }
      OPTIONAL { ?line metro:originStation ?origin }
      OPTIONAL { ?line metro:destinationStation ?destination }
      OPTIONAL {
        ?stationLine metro:onLine ?line .
        ?stationLine metro:relatesTo ?station
      }
    }
    GROUP BY ?line ?lineCode ?lineName ?lineColor ?auxColor ?origin ?destination
    ORDER BY ?lineCode
    """
    
    data = await query_sparql(query)
    
    lines = []
    for binding in data.get("results", {}).get("bindings", []):
        line = LineResponse(
            id=binding.get("line", {}).get("value", ""),
            code=str(binding.get("lineCode", {}).get("value", "")),
            name=binding.get("lineName", {}).get("value", ""),
            color="#" + binding.get("lineColor", {}).get("value", "999"),
            auxColor=binding.get("auxColor", {}).get("value"),
            origin=binding.get("origin", {}).get("value"),
            destination=binding.get("destination", {}).get("value"),
            numStations=int(binding.get("numStations", {}).get("value", 0))
        )
        lines.append(line)
    
    return lines


@app.get("/api/station/{station_id:path}")
async def get_station_details(station_id: str):
    """Obtiene detalles de una estación específica"""
    from urllib.parse import unquote
    station_uri = unquote(station_id)
    
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX metro: <https://data.example.org/transport/bcn/metro/ontology#>
    
    SELECT ?name ?geometry ?inaugurated
           (GROUP_CONCAT(DISTINCT ?lineCode; separator=",") AS ?lines)
    WHERE {{
      <{station_uri}> rdfs:label ?name .
      OPTIONAL {{ <{station_uri}> metro:hasGeometry ?geometry }}
      OPTIONAL {{ <{station_uri}> metro:inauguratedDate ?inaugurated }}
      OPTIONAL {{ 
        ?stationLine metro:relatesTo <{station_uri}> .
        ?stationLine metro:onLine ?line .
        ?line metro:lineCode ?lineCode
      }}
    }}
    GROUP BY ?name ?geometry ?inaugurated
    """
    
    data = await query_sparql(query)
    
    bindings = data.get("results", {}).get("bindings", [])
    if not bindings:
        raise HTTPException(status_code=404, detail="Station not found")
        
    binding = bindings[0]
    geometry_wkt = binding.get("geometry", {}).get("value", "")
    coords = parse_point_wkt(geometry_wkt)
    
    station = {
        "id": station_uri,
        "name": binding.get("name", {}).get("value", ""),
        "latitude": coords["lat"] if coords else None,
        "longitude": coords["lng"] if coords else None,
        "inaugurated": binding.get("inaugurated", {}).get("value", ""),
        "lines": binding.get("lines", {}).get("value", "").split(",") if binding.get("lines") else []
    }
    
    return station


@app.get("/api/line-geometries")
async def get_line_geometries():
    """Obtiene las geometrías de todas las líneas desde MULTILINESTRING WKT"""
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX metro: <https://data.example.org/transport/bcn/metro/ontology#>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    
    SELECT ?lineCode ?lineColor ?geometry
    WHERE {
      ?line rdf:type metro:MetroLine .
      ?line metro:lineCode ?lineCode .
      OPTIONAL { ?line metro:lineColor ?lineColor }
      OPTIONAL { ?line metro:hasGeometry ?geometry }
    }
    ORDER BY ?lineCode
    """
    
    data = await query_sparql(query)
    
    result = []
    for binding in data.get("results", {}).get("bindings", []):
        line_code = str(binding.get("lineCode", {}).get("value", ""))
        geometry_wkt = binding.get("geometry", {}).get("value", "")
        
        if not geometry_wkt:
            continue
        
        coordinates = parse_multilinestring_wkt(geometry_wkt)
        
        if coordinates:
            result.append({
                "code": line_code,
                "color": "#" + binding.get("lineColor", {}).get("value", "999"),
                "coordinates": coordinates
            })
    
    return result


@app.get("/api/line/{line_code}")
async def get_line_details(line_code: str):
    """Obtiene detalles de una línea específica incluyendo sus estaciones"""
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX metro: <https://data.example.org/transport/bcn/metro/ontology#>
    
    SELECT ?line ?lineColor ?auxColor ?origin ?destination ?stationName ?order
    WHERE {{
      ?line rdf:type metro:MetroLine .
      ?line metro:lineCode {line_code} .
      OPTIONAL {{ ?line metro:lineColor ?lineColor }}
      OPTIONAL {{ ?line metro:auxiliaryColor ?auxColor }}
      OPTIONAL {{ ?line metro:originStation ?origin }}
      OPTIONAL {{ ?line metro:destinationStation ?destination }}
      OPTIONAL {{
        ?stationLine metro:onLine ?line .
        ?stationLine metro:relatesTo ?station .
        ?stationLine metro:stationOrder ?order .
        ?station rdfs:label ?stationName
      }}
    }}
    ORDER BY ?order
    """
    
    data = await query_sparql(query)
    
    bindings = data.get("results", {}).get("bindings", [])
    if not bindings:
        raise HTTPException(status_code=404, detail="Line not found")
    
    line_info = {
        "code": line_code,
        "id": bindings[0].get("line", {}).get("value", ""),
        "color": "#" + bindings[0].get("lineColor", {}).get("value", "999"),
        "auxColor": bindings[0].get("auxColor", {}).get("value", ""),
        "origin": bindings[0].get("origin", {}).get("value", ""),
        "destination": bindings[0].get("destination", {}).get("value", ""),
        "stations": []
    }
    
    for binding in bindings:
        if binding.get("stationName"):
            line_info["stations"].append({
                "name": binding.get("stationName", {}).get("value", ""),
                "order": int(binding.get("order", {}).get("value", 0))
            })
    
    line_info["numStations"] = len(line_info["stations"])
    
    return line_info


@app.get("/api/examples", response_model=List[ExampleQuery])
async def get_examples():
    """Devuelve consultas SPARQL de ejemplo para el dominio de metro"""
    examples = [
        ExampleQuery(
            name="Todas las líneas de metro",
            description="Lista todas las líneas del metro de Barcelona",
            query="""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX metro: <https://data.example.org/transport/bcn/metro/ontology#>

                    SELECT ?etiqueta ?nombre ?descripcion WHERE {
                    ?linea rdf:type metro:MetroLine .
                    OPTIONAL { ?linea metro:lineEtiq ?etiqueta }
                    OPTIONAL { ?linea metro:lineCode ?codigo }
                    OPTIONAL { ?linea metro:lineName ?nombre }
                    OPTIONAL { ?linea metro:lineDescription ?descripcion }
                    }
                    ORDER BY ?codigo
                    LIMIT 50"""
        ),
        ExampleQuery(
            name="Estaciones por línea",
            description="Cuenta el número de estaciones por cada línea",
            query="""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX metro: <https://data.example.org/transport/bcn/metro/ontology#>

                    SELECT ?linea (COUNT(DISTINCT ?station) AS ?numEstaciones) WHERE {
                    ?line rdf:type metro:MetroLine .
                    ?line metro:lineEtiq ?linea .
                    ?stationLine metro:onLine ?line .
                    ?stationLine metro:relatesTo ?station .
                    }
                    GROUP BY ?linea
                    ORDER BY DESC(?numEstaciones)"""
        ),
        ExampleQuery(
            name="Estaciones con nombres",
            description="Lista estaciones con sus nombres, coordenadas y enlace a Wikidata",
            query="""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX metro: <https://data.example.org/transport/bcn/metro/ontology#>
                    PREFIX owl: <http://www.w3.org/2002/07/owl#>

                    SELECT ?estacion ?nombre ?wikidata WHERE {
                    ?estacion rdf:type metro:Station .
                    ?estacion rdfs:label ?nombre .
                    OPTIONAL { ?estacion owl:sameAs ?wikidata }
                    }
                    ORDER BY ?nombre"""
        ),
        ExampleQuery(
            name="Estaciones de intercambio",
            description="Encuentra estaciones que conectan múltiples líneas",
            query="""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX metro: <https://data.example.org/transport/bcn/metro/ontology#>

                    SELECT ?nombre (COUNT(DISTINCT ?line) AS ?numLineas) WHERE {
                    ?station rdf:type metro:Station .
                    ?station rdfs:label ?nombre .
                    ?stationLine metro:relatesTo ?station .
                    ?stationLine metro:onLine ?line .
                    }
                    GROUP BY ?nombre
                    HAVING (COUNT(DISTINCT ?line) > 1)
                    ORDER BY DESC(?numLineas)
                    LIMIT 20"""
        ),
        ExampleQuery(
            name="Detalles de una línea específica",
            description="Muestra información de la línea L1",
            query="""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX metro: <https://data.example.org/transport/bcn/metro/ontology#>
                    PREFIX owl: <http://www.w3.org/2002/07/owl#>

                    SELECT ?linea ?codigo ?color ?origen ?destino 
                           (SAMPLE(?wd) AS ?wikidata)
                    WHERE {
                    ?linea rdf:type metro:MetroLine .
                    ?linea metro:lineCode ?codigo .
                    OPTIONAL { ?linea metro:lineColor ?color }
                    OPTIONAL { ?linea metro:originStation ?origen }
                    OPTIONAL { ?linea metro:destinationStation ?destino }
                    OPTIONAL { ?linea owl:sameAs ?wd }
                    FILTER(?codigo = 4)
                    }
                    GROUP BY ?linea ?codigo ?color ?origen ?destino"""
        ),
        ExampleQuery(
            name="Contar instancias por clase",
            description="Estadísticas de tipos de recursos en el dataset",
            query="""SELECT ?class (COUNT(?s) AS ?count) WHERE {
                    ?s a ?class
                    }
                    GROUP BY ?class
                    ORDER BY DESC(?count)
                    LIMIT 20"""
        ),
        ExampleQuery(
            name="10 recursos con etiquetas",
            description="Muestra 10 recursos con sus etiquetas",
            query="""PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    SELECT ?s ?label WHERE {
                    ?s a ?type .
                    OPTIONAL { ?s rdfs:label ?label }
                    }
                    LIMIT 10"""
        )
    ]
    
    return examples


@app.get("/api/route")
async def find_route(origin: str = Query(...), destination: str = Query(...)):
    """
    Encuentra la ruta más corta entre dos estaciones
    """
    query = """
    PREFIX metro: <https://data.example.org/transport/bcn/metro/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    
    SELECT ?station ?stationName ?lineCode ?order ?lineGeometry ?stationGeometry
    WHERE {
      ?station a metro:Station ;
               rdfs:label ?stationName .
      ?accessPoint metro:relatesTo ?station ;
                   metro:onLine ?line ;
                   metro:stationOrder ?order .
      ?line metro:lineCode ?lineCode .
      OPTIONAL { ?line metro:hasGeometry ?lineGeometry }
      OPTIONAL { ?station metro:hasGeometry ?stationGeometry }
    }
    ORDER BY ?lineCode ?order
    """
    
    data = await query_sparql(query)
    
    # Construir grafo y estructuras de datos
    stations_by_name = defaultdict(list)
    station_names = {}
    station_coords = {}
    station_lines = defaultdict(set)
    line_stations = defaultdict(list)
    line_geometries = {}
    
    for binding in data.get("results", {}).get("bindings", []):
        station_uri = binding.get("station", {}).get("value", "")
        station_name = binding.get("stationName", {}).get("value", "")
        line_code = str(binding.get("lineCode", {}).get("value", ""))
        order = int(binding.get("order", {}).get("value", 0))
        line_geom = binding.get("lineGeometry", {}).get("value", "")
        station_geom = binding.get("stationGeometry", {}).get("value", "")
        
        stations_by_name[station_name].append(station_uri)
        station_names[station_uri] = station_name
        station_lines[station_name].add(line_code)
        line_stations[line_code].append((station_name, order, station_uri))
        
        if station_geom and station_uri not in station_coords:
            coords = parse_point_wkt(station_geom)
            if coords:
                station_coords[station_uri] = (coords['lat'], coords['lng'])
        
        if line_geom and line_code not in line_geometries:
            line_geometries[line_code] = line_geom
    
    # Verificar que origen y destino existen
    if origin not in stations_by_name:
        return {"found": False, "error": f"Estación origen '{origin}' no encontrada"}
    if destination not in stations_by_name:
        return {"found": False, "error": f"Estación destino '{destination}' no encontrada"}
    
    # Construir grafo
    graph = defaultdict(list)
    
    for line_code, stations in line_stations.items():
        unique_stations = {}
        for name, order, uri in stations:
            if name not in unique_stations or order < unique_stations[name][0]:
                unique_stations[name] = (order, uri)
        
        sorted_stations = sorted(unique_stations.items(), key=lambda x: x[1][0])
        
        for i in range(len(sorted_stations) - 1):
            name1, _ = sorted_stations[i]
            name2, _ = sorted_stations[i + 1]
            graph[name1].append((name2, line_code))
            graph[name2].append((name1, line_code))
    
    # BFS para encontrar ruta más corta
    queue = deque([(origin, [origin], [])])
    visited = {origin}
    
    while queue:
        current, path, lines = queue.popleft()
        
        if current == destination:
            # Construir respuesta
            route_stations = []
            route_segments = []
            
            for i, station_name in enumerate(path):
                station_uri = stations_by_name[station_name][0]
                route_stations.append({
                    "name": station_name,
                    "uri": station_uri
                })
                
                if i < len(path) - 1:
                    line_code = lines[i]
                    next_station_name = path[i + 1]
                    
                    current_uri = station_uri
                    next_uri = stations_by_name[next_station_name][0]
                    
                    current_coords = station_coords.get(current_uri)
                    next_coords = station_coords.get(next_uri)
                    
                    segment_info = {
                        "line_code": line_code,
                        "from_station": station_name,
                        "to_station": next_station_name
                    }
                    
                    if line_code in line_geometries and current_coords and next_coords:
                        segment_info["geometry"] = line_geometries[line_code]
                        segment_info["from_coords"] = current_coords
                        segment_info["to_coords"] = next_coords
                    
                    route_segments.append(segment_info)
            
            # Calcular transbordos
            transfers = []
            current_line = None
            for i, line_code in enumerate(lines):
                if current_line and current_line != line_code:
                    transfers.append({
                        "station": path[i],
                        "from_line": current_line,
                        "to_line": line_code
                    })
                current_line = line_code
            
            return {
                "found": True,
                "stations": route_stations,
                "lines": lines,
                "segments": route_segments,
                "transfers": transfers,
                "num_stations": len(route_stations),
                "num_transfers": len(transfers)
            }
        
        # Explorar vecinos
        for neighbor, line_code in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor], lines + [line_code]))
    
    return {
        "found": False,
        "error": "No se encontró ruta entre las estaciones"
    }


# Servir archivos de recursos (documentación)
app.mount("/resources", StaticFiles(directory=str(RESOURCES_DIR), html=True), name="resources")

# Servir archivos estáticos del frontend
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    print(f"🚇 Aplicación Grupo 01 - Metro Dataset (FastAPI)")
    print(f"📍 Backend: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print(f"🔗 SPARQL Endpoint: {SPARQL_ENDPOINT}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
