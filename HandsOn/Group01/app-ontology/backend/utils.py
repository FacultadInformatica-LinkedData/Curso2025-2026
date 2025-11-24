# backend/utils.py - Utilidades y funciones auxiliares
import re
from typing import Optional, List, Dict, Any
from fastapi import HTTPException
import httpx

SPARQL_ENDPOINT = "http://localhost:3030/dataset/sparql"


def parse_point_wkt(wkt: str) -> Optional[Dict[str, float]]:
    """
    Parsea un POINT WKT y devuelve {lat, lng}
    Ejemplo: POINT (2.107241921905464 41.344677306491334)
    """
    try:
        pattern = r'POINT\s*\(\s*([\d.]+)\s+([\d.]+)\s*\)'
        match = re.search(pattern, wkt)
        if match:
            lon = float(match.group(1))
            lat = float(match.group(2))
            return {"lat": lat, "lng": lon}
        return None
    except Exception as e:
        print(f"Error parseando POINT WKT: {e}")
        return None


def parse_multilinestring_wkt(wkt: str) -> List[Dict[str, float]]:
    """
    Parsea un MULTILINESTRING WKT y devuelve array de coordenadas [lat, lng]
    Ejemplo: MULTILINESTRING ((2.168 41.373, 2.165 41.370, 2.163 41.368))
    """
    try:
        pattern = r'([\d.]+)\s+([\d.]+)'
        matches = re.findall(pattern, wkt)
        
        coordinates = []
        for lon, lat in matches:
            coordinates.append({
                "lat": float(lat),
                "lng": float(lon)
            })
        
        return coordinates
    except Exception as e:
        print(f"Error parseando WKT: {e}")
        return []


async def query_sparql(query: str, response_format: str = "application/sparql-results+json") -> Any:
    """Ejecuta una consulta SPARQL de forma asíncrona"""
    headers = {"Accept": response_format}
    params = {"query": query}
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            resp = await client.get(SPARQL_ENDPOINT, params=params, headers=headers)
            resp.raise_for_status()
            
            if "json" in resp.headers.get("content-type", ""):
                return resp.json()
            else:
                return resp.text
                
        except httpx.ConnectError:
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "No se puede conectar con Apache Jena Fuseki",
                    "details": f"Fuseki no está corriendo en {SPARQL_ENDPOINT}",
                    "solution": "Inicia Fuseki con: fuseki-server --update --mem /dataset"
                }
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail={
                    "error": "Timeout al conectar con Fuseki",
                    "details": "La consulta tardó demasiado tiempo",
                    "solution": "Verifica que Fuseki esté funcionando correctamente"
                }
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "Error al ejecutar la consulta SPARQL",
                    "details": str(e),
                    "endpoint": SPARQL_ENDPOINT
                }
            )
