from utils.rdf_loader import load_graph

PREFIX = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX vocab: <http://example.org/vocab#>
"""

def get_measurements():
    """
    Obtiene las primeras 200 mediciones de calidad del aire (solo hora H01).
    Consulta básica para verificar que el RDF se carga correctamente.
    """
    g = load_graph()

    query = PREFIX + """
    SELECT ?estacion ?fecha ?magnitud ?valor
    WHERE {
        ?m a vocab:MedicionAire ;
           vocab:estacion ?estacion ;
           vocab:fecha ?fecha ;
           vocab:magnitud ?magnitud ;
           vocab:H01 ?valor .
    }
    LIMIT 200
    """

    results = []
    for row in g.query(query):
        results.append({
            "estacion": str(row.estacion),
            "fecha": str(row.fecha),
            "magnitud": str(row.magnitud),
            "valor": float(row.valor),
        })
    return results


def get_measurements_by_station_and_date(estacion=None, fecha=None):
    """
    Obtiene mediciones de calidad del aire filtradas por estación y/o fecha.
    
    Args:
        estacion (str, optional): ID de la estación (ej: "11", "102")
        fecha (str, optional): Fecha en formato ISO (ej: "2025-07-07T00:00:00Z")
    
    Returns:
        list: Lista de diccionarios con las mediciones y todas las horas (H01-H24)
    
    Ejemplos:
        get_measurements_by_station_and_date(estacion="11")
        get_measurements_by_station_and_date(fecha="2025-07-07T00:00:00Z")
        get_measurements_by_station_and_date(estacion="11", fecha="2025-07-07T00:00:00Z")
    """
    g = load_graph()
    
    # Construir filtros dinámicos
    filters = []
    if estacion:
        filters.append(f'?estacion = "{estacion}"')
    if fecha:
        filters.append(f'?fecha = "{fecha}"^^xsd:dateTime')
    
    filter_clause = "FILTER (" + " && ".join(filters) + ")" if filters else ""
    
    query = PREFIX + """
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    SELECT ?estacion ?fecha ?magnitud ?puntoMuestreo
           ?h01 ?h02 ?h03 ?h04 ?h05 ?h06 ?h07 ?h08 ?h09 ?h10 ?h11 ?h12
           ?h13 ?h14 ?h15 ?h16 ?h17 ?h18 ?h19 ?h20 ?h21 ?h22 ?h23 ?h24
    WHERE {
        ?m a vocab:MedicionAire ;
           vocab:estacion ?estacion ;
           vocab:fecha ?fecha ;
           vocab:magnitud ?magnitud .
        
        OPTIONAL { ?m vocab:puntoMuestreo ?puntoMuestreo }
        OPTIONAL { ?m vocab:H01 ?h01 }
        OPTIONAL { ?m vocab:H02 ?h02 }
        OPTIONAL { ?m vocab:H03 ?h03 }
        OPTIONAL { ?m vocab:H04 ?h04 }
        OPTIONAL { ?m vocab:H05 ?h05 }
        OPTIONAL { ?m vocab:H06 ?h06 }
        OPTIONAL { ?m vocab:H07 ?h07 }
        OPTIONAL { ?m vocab:H08 ?h08 }
        OPTIONAL { ?m vocab:H09 ?h09 }
        OPTIONAL { ?m vocab:H10 ?h10 }
        OPTIONAL { ?m vocab:H11 ?h11 }
        OPTIONAL { ?m vocab:H12 ?h12 }
        OPTIONAL { ?m vocab:H13 ?h13 }
        OPTIONAL { ?m vocab:H14 ?h14 }
        OPTIONAL { ?m vocab:H15 ?h15 }
        OPTIONAL { ?m vocab:H16 ?h16 }
        OPTIONAL { ?m vocab:H17 ?h17 }
        OPTIONAL { ?m vocab:H18 ?h18 }
        OPTIONAL { ?m vocab:H19 ?h19 }
        OPTIONAL { ?m vocab:H20 ?h20 }
        OPTIONAL { ?m vocab:H21 ?h21 }
        OPTIONAL { ?m vocab:H22 ?h22 }
        OPTIONAL { ?m vocab:H23 ?h23 }
        OPTIONAL { ?m vocab:H24 ?h24 }
        
        """ + filter_clause + """
    }
    ORDER BY ?fecha ?estacion ?magnitud
    LIMIT 500
    """
    
    results = []
    for row in g.query(query):
        # Construir diccionario con todas las horas
        measurement = {
            "estacion": str(row.estacion),
            "fecha": str(row.fecha),
            "magnitud": str(row.magnitud),
            "puntoMuestreo": str(row.puntoMuestreo) if row.puntoMuestreo else None,
        }
        
        # Añadir valores horarios (convertir a float si existen)
        for i in range(1, 25):
            hora_var = f"h{i:02d}"
            hora_value = getattr(row, hora_var, None)
            measurement[f"H{i:02d}"] = float(hora_value) if hora_value else None
        
        results.append(measurement)
    
    return results


def get_ozone_episodes(fecha_inicio=None, fecha_fin=None):
    """
    Obtiene episodios de ozono (activaciones del protocolo por alta contaminación).
    
    Args:
        fecha_inicio (str, optional): Filtrar desde esta fecha (formato ISO, ej: "2025-07-08T00:00:00Z")
        fecha_fin (str, optional): Filtrar hasta esta fecha (formato ISO)
    
    Returns:
        list: Lista de diccionarios con información de cada episodio de ozono
    
    Ejemplos:
        get_ozone_episodes()  # Todos los episodios
        get_ozone_episodes(fecha_inicio="2025-07-08T00:00:00Z")
        get_ozone_episodes(fecha_inicio="2025-07-01T00:00:00Z", fecha_fin="2025-07-31T23:59:59Z")
    """
    g = load_graph()
    
    # Construir filtros dinámicos, considerando que las fechas son opcionales, evitando crear 4 consultas separadas
    filters = []
    if fecha_inicio:
        filters.append(f'?fechaInicio >= "{fecha_inicio}"^^xsd:dateTime')
    if fecha_fin:
        filters.append(f'?fechaFin <= "{fecha_fin}"^^xsd:dateTime')
    
    filter_clause = "FILTER (" + " && ".join(filters) + ")" if filters else ""
    
    # Usar GROUP_CONCAT para agrupar múltiples medidas de población en una sola fila
    query = PREFIX + """
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    SELECT ?episodio ?fechaInicio ?fechaFin ?escenario 
           (GROUP_CONCAT(?medida; separator=" | ") AS ?medidaPoblacion)
    WHERE {
        ?episodio a vocab:EpisodioOzono ;
                  vocab:inicio ?fechaInicio ;
                  vocab:fin ?fechaFin .
        
        OPTIONAL { ?episodio vocab:escenario ?escenario }
        OPTIONAL { ?episodio vocab:medidaPoblacion ?medida }
        
        """ + filter_clause + """
    }
    GROUP BY ?episodio ?fechaInicio ?fechaFin ?escenario
    ORDER BY DESC(?fechaInicio)
    """
    
    results = []
    for row in g.query(query):
        results.append({
            "episodio_uri": str(row.episodio),
            "fecha_inicio": str(row.fechaInicio),
            "fecha_fin": str(row.fechaFin),
            "escenario": str(row.escenario) if row.escenario else None,
            "medida_poblacion": str(row.medidaPoblacion) if row.medidaPoblacion else None,
        })
    
    return results

# Enlaces de magnitudes (gases) a Wikidata
MAGNITUD_LINKS = {
    "1":  "https://www.wikidata.org/wiki/Q5282",     # SO2
    "6":  "https://www.wikidata.org/wiki/Q2025",     # CO
    "7":  "https://www.wikidata.org/wiki/Q207843",   # NO
    "8":  "https://www.wikidata.org/wiki/Q207895",   # NO2
    "9":  "https://www.wikidata.org/wiki/Q48035980", # PM10
    "10": "https://www.wikidata.org/wiki/Q48035814", # PM2.5
    "12": "https://www.wikidata.org/wiki/Q36933",    # O3
    "14": "https://www.wikidata.org/wiki/Q2270",     # Benceno
}

# Enlaces de estaciones a Wikidata (las que has pasado)
ESTACION_LINKS = {

    "1":  "https://www.wikidata.org/wiki/Q8841582",      # Pº. Recoletos (001)
    "2":  "https://www.wikidata.org/wiki/Q7203711",      # Glta. de Carlos V (002)
    "4":  "https://www.wikidata.org/wiki/Q776249",       # Plaza España (004)
    "6":  "https://www.wikidata.org/wiki/Q52084168",     # Pza. Dr. Marañón (006)
    "7":  "https://www.wikidata.org/wiki/Q16620302",     # Pza. M. de Salamanca (007)
    "8":  "https://www.wikidata.org/wiki/Q5397501",      # Escuelas Aguirre (008)
    "9":  "https://www.wikidata.org/wiki/Q30148071",     # Pza. Luca de Tena (009)
    "11": "https://www.wikidata.org/wiki/Q30467128",     # Av. Ramón y Cajal (011)
    "12": "https://www.wikidata.org/wiki/Q2056869",      # Pza. Manuel Becerra (012)
    "14": "https://www.wikidata.org/wiki/Q136805046",    # Pza. Fdez. Ladreda (014)
    "15": "https://www.wikidata.org/wiki/Q2463399",      # Pza. Castilla (015)
    "16": "https://www.wikidata.org/wiki/Q2481371",      # Arturo Soria (016)
    "17": "https://www.wikidata.org/wiki/Q2480338",      # Villaverde Alto (017)
    "19": "https://www.wikidata.org/wiki/Q136805075",    # Huerta Castañeda (019)
    "21": "https://www.wikidata.org/wiki/Q26791536",     # Pza. Cristo Rey (021)
    "22": "https://www.wikidata.org/wiki/Q26737156",     # Pº. Pontones (022)
    "23": "https://www.wikidata.org/wiki/Q2424746",      # Final C/ Alcalá (023)
    "24": "https://www.wikidata.org/wiki/Q568579",       # Casa de Campo (024)
    "25": "https://www.wikidata.org/wiki/Q5847173",      # Santa Eugenia (025)
    "26": "https://www.wikidata.org/wiki/Q136805083",    # Urb. Embajada (Barajas) (026)
    "27": "https://www.wikidata.org/wiki/Q2474414",      # Barajas (027)
    "35": "https://www.wikidata.org/wiki/Q6080406",      # Plaza del Carmen (035)
    "36": "https://www.wikidata.org/wiki/Q2076109",      # Moratalaz (036)
    "38": "https://www.wikidata.org/wiki/Q2420839",      # Cuatro Caminos (038)
    "39": "https://www.wikidata.org/wiki/Q2463533",      # Barrio del Pilar (039)
    "40": "https://www.wikidata.org/wiki/Q5548317",      # Vallecas (040)
    "47": "https://www.wikidata.org/wiki/Q2479775",      # Méndez Álvaro (047)
    "48": "https://www.wikidata.org/wiki/Q1473674",      # Pº. Castellana (048)
    "49": "https://www.wikidata.org/wiki/Q2056874",      # Retiro (049)
    "50": "https://www.wikidata.org/wiki/Q2463399",      # Pza. Castilla (050) — igual que 15
    "54": "https://www.wikidata.org/wiki/Q3847485",      # Ensanche de Vallecas (054)
    "55": "https://www.wikidata.org/wiki/Q136805083",    # Urb. Embajada (Barajas) (055) — igual que 26
    "56": "https://www.wikidata.org/wiki/Q782113",       # Plaza Elíptica (056)
    "57": "https://www.wikidata.org/wiki/Q3076623",      # Sanchinarro (057)
    "58": "https://www.wikidata.org/wiki/Q3314337",      # El Pardo (058)
    "59": "https://www.wikidata.org/wiki/Q1583169",      # Juan Carlos I (059)
    "60": "https://www.wikidata.org/wiki/Q608766",       # Tres Olivos (060)
    "102": "https://www.wikidata.org/wiki/Q56191300",    # J.M.D. Moratalaz
    "103": "https://www.wikidata.org/wiki/Q56190652",    # J.M.D. Villaverde
    "104": "https://www.wikidata.org/wiki/Q136805096",   # E.D.A.R. La China
    "106": "https://www.wikidata.org/wiki/Q136804907",   # Centro Mpal. De Acústica
    "107": "https://www.wikidata.org/wiki/Q56190091",    # J.M.D. Hortaleza
    "108": "https://www.wikidata.org/wiki/Q2058663",     # Peñagrande
    "109": "https://www.wikidata.org/wiki/Q56164429",    # J.M.D. Chamberí
    "110": "https://www.wikidata.org/wiki/Q56164302",    # J.M.D. Centro
    "111": "https://www.wikidata.org/wiki/Q56192459",    # J.M.D. Chamartín
    "112": "https://www.wikidata.org/wiki/Q56191978",    # J.M.D. Vallecas 1
    "113": "https://www.wikidata.org/wiki/Q56191848",    # J.M.D. Vallecas 2
    "114": "https://www.wikidata.org/wiki/Q4043800",     # Matadero 01
    "115": "https://www.wikidata.org/wiki/Q105776403",   # Matadero 02
}


def get_measurements_with_linked_data(estacion=None, magnitud=None, limit=100):
    """
    Obtiene mediciones de calidad del aire junto con sus enlaces a recursos externos (owl:sameAs).
    Demuestra el concepto de Linked Data conectando con Wikidata.

    Args:
        estacion (str, optional): ID de la estación para filtrar (ej: "36", "60")
        magnitud (str, optional): Código de magnitud para filtrar (ej: "10" para partículas)
        limit (int, optional): Número máximo de resultados (default: 100)

    Returns:
        list[dict]: mediciones + enlaces
    """
    g = load_graph()

    # Construir filtros dinámicos (igual que versión original)
    filters = []
    if estacion:
        filters.append(f'?estacion = "{estacion}"')
    if magnitud:
        filters.append(f'?magnitud = "{magnitud}"')

    filter_clause = "FILTER (" + " && ".join(filters) + ")" if filters else ""

    query = PREFIX + """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    SELECT ?medicion ?estacion ?fecha ?magnitud ?puntoMuestreo ?enlaceExterno
    WHERE {
        ?medicion a vocab:MedicionAire ;
                  vocab:estacion ?estacion ;
                  vocab:fecha ?fecha ;
                  vocab:magnitud ?magnitud .

        OPTIONAL { ?medicion vocab:puntoMuestreo ?puntoMuestreo }

        # owl:sameAs conecta nuestra medición con recursos de Wikidata (Linked Data)
        OPTIONAL { ?medicion owl:sameAs ?enlaceExterno }

        """ + filter_clause + """
    }
    ORDER BY ?fecha ?estacion
    LIMIT """ + str(limit) + """
    """

    results = []
    for row in g.query(query):
        # Valores base (lo de siempre)
        estacion_val = str(row.estacion)
        magnitud_val = str(row.magnitud)

        item = {
            "medicion": str(row.medicion),
            "estacion": estacion_val,
            "fecha": str(row.fecha),
            "magnitud": magnitud_val,
            "punto": str(row.puntoMuestreo) if row.puntoMuestreo else None,
            # Enlace original de la medición
            "link_medicion": str(row.enlaceExterno) if row.enlaceExterno else None,
            # NUEVO: enlaces enriquecidos
            "link_magnitud": MAGNITUD_LINKS.get(magnitud_val),
            "link_estacion": ESTACION_LINKS.get(estacion_val),
        }

        results.append(item)

    return results






def get_aggregated_statistics(estacion=None, magnitud=None, fecha=None):
    """
    Obtiene estadísticas agregadas de calidad del aire (promedio, máximo, mínimo, conteo).
    Demuestra el uso de funciones de agregación en SPARQL: AVG, MAX, MIN, COUNT.
    
    Args:
        estacion (str, optional): ID de la estación para filtrar (ej: "11", "36")
        magnitud (str, optional): Código de magnitud para filtrar (ej: "10", "12")
        fecha (str, optional): Fecha para filtrar (formato ISO)
    
    Returns:
        list: Lista de diccionarios con estadísticas agregadas por estación y magnitud
    
    Ejemplos:
        get_aggregated_statistics()  # Todas las estadísticas
        get_aggregated_statistics(estacion="11")  # Estadísticas de una estación
        get_aggregated_statistics(magnitud="10")  # Estadísticas de una magnitud
    """
    g = load_graph()
    
    # Construir filtros dinámicos
    filters = []
    if estacion:
        filters.append(f'?estacion = "{estacion}"')
    if magnitud:
        filters.append(f'?magnitud = "{magnitud}"')
    if fecha:
        filters.append(f'?fecha = "{fecha}"^^xsd:dateTime')
    
    filter_clause = "FILTER (" + " && ".join(filters) + ")" if filters else ""
    
    # Consulta de agregación con AVG, MAX, MIN, COUNT
    query = PREFIX + """
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    SELECT ?estacion ?magnitud
           (COUNT(?m) AS ?total_mediciones)
           (AVG(?valor) AS ?promedio)
           (MAX(?valor) AS ?maximo)
           (MIN(?valor) AS ?minimo)
    WHERE {
        ?m a vocab:MedicionAire ;
           vocab:estacion ?estacion ;
           vocab:fecha ?fecha ;
           vocab:magnitud ?magnitud ;
           vocab:H01 ?valor .
        
        """ + filter_clause + """
    }
    GROUP BY ?estacion ?magnitud
    ORDER BY ?estacion ?magnitud
    """
    
    results = []
    for row in g.query(query):
        results.append({
            "estacion": str(row.estacion),
            "magnitud": str(row.magnitud),
            "total_mediciones": int(row.total_mediciones) if row.total_mediciones else 0,
            "promedio": round(float(row.promedio), 2) if row.promedio else None,
            "maximo": float(row.maximo) if row.maximo else None,
            "minimo": float(row.minimo) if row.minimo else None,
        })
    
    return results


def get_available_stations():
    """
    Obtiene la lista de estaciones únicas disponibles en el dataset,
    combinando:
      - Estaciones que aparecen en las mediciones del RDF
      - Estaciones presentes en el diccionario ESTACION_LINKS
    Devuelve una lista de IDs de estaciones ordenadas numéricamente.
    """
    g = load_graph()

    query = PREFIX + """
    SELECT DISTINCT ?estacion
    WHERE {
        ?m a vocab:MedicionAire ;
           vocab:estacion ?estacion .
    }
    ORDER BY ?estacion
    """

    # Estaciones que vienen del RDF
    stations = set()
    for row in g.query(query):
        stations.add(str(row.estacion))

    # Añadimos también las que están en el diccionario de enlaces
    stations.update(ESTACION_LINKS.keys())

    # Ordenar numéricamente si se puede; si no, alfabéticamente
    try:
        stations_sorted = sorted(stations, key=lambda x: int(x))
        return stations_sorted
    except ValueError:
        return sorted(stations)



def get_available_magnitudes():
    """
    Obtiene la lista de magnitudes (contaminantes) únicas disponibles en el dataset.
    Útil para poblar desplegables en la interfaz.
    
    Returns:
        list: Lista de códigos de magnitud ordenados numéricamente
    """
    g = load_graph()
    
    query = PREFIX + """
    SELECT DISTINCT ?magnitud
    WHERE {
        ?m a vocab:MedicionAire ;
           vocab:magnitud ?magnitud .
    }
    ORDER BY ?magnitud
    """
    
    magnitudes = []
    for row in g.query(query):
        magnitudes.append(str(row.magnitud))
    
    # Ordenar numéricamente (en caso de que sean números)
    try:
        magnitudes_sorted = sorted(magnitudes, key=lambda x: int(x))
        return magnitudes_sorted
    except ValueError:
        # Si no son todos números, devolver ordenación alfabética
        return sorted(magnitudes)

