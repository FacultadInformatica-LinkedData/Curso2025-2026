from SPARQLWrapper import SPARQLWrapper, JSON


# =========================
# CONFIGURACIÓN
# =========================

SPARQL_ENDPOINT = "http://localhost:7200/repositories/Group14"

PREFIXES = """
PREFIX cal: <http://datos.madrid.es/Calidad_Aire#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""

# UTILIDAD SPARQL
def run_query(query: str):
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    results = sparql.query().convert()
    return results["results"]["bindings"]

# OPCIONES GLOBALES
def leer_opcion(texto="Elige una opción"):
    print("\n  0 - Volver atrás")
    print("  99 - Volver al inicio")
    print("  100 - Salir del programa")
    return input(f"\n{texto}: ").strip()

# ESTACIONES
def listar_estaciones():
    query = PREFIXES + """
    SELECT DISTINCT ?codigo ?nombre ?estacionURI ?link
    WHERE {
        ?estacionURI a cal:Estacion ;
        cal:ESTACION ?codigo .
        OPTIONAL { ?estacionURI cal:NOMBRE_ESTACION ?nombre . }
        OPTIONAL { ?estacionURI cal:DIR_ESTACION_LINK ?link . }
    }
    ORDER BY xsd:integer(?codigo)
    """
    rows = run_query(query)

    estaciones = []
    for row in rows:
        codigo = row["codigo"]["value"]
        nombre = row.get("nombre", {}).get("value", "(sin nombre)")
        uri = row["estacionURI"]["value"]
        link = row.get("link", {}).get("value", "-")
        estaciones.append((codigo, nombre, uri, link))

    return estaciones

def seleccionar_estacion_por_codigo(estaciones):
    while True:
        print("\n=== Estaciones disponibles ===\n")
        for codigo, nombre, _, link in estaciones:
            print(f"  Código {codigo} - {nombre}  ({link})")

        index_por_codigo = {
            codigo: (codigo, nombre, uri)
            for codigo, nombre, uri, _ in estaciones
        }

        eleccion = leer_opcion("Introduce el CÓDIGO de la estación")

        if eleccion == "100":
            exit()
        if eleccion == "99":
            return "INICIO"
        if eleccion == "0":
            return None

        if eleccion in index_por_codigo:
            return index_por_codigo[eleccion]

        print("Ese código no existe.")

# GASES
def obtener_gases_estacion(estacion_uri: str):
    query = PREFIXES + f"""
    SELECT ?no2 ?so2 ?pm10 ?pm25 ?o3 ?btx
    WHERE {{
        OPTIONAL {{ <{estacion_uri}> cal:NO2   ?no2  }}
        OPTIONAL {{ <{estacion_uri}> cal:SO2   ?so2  }}
        OPTIONAL {{ <{estacion_uri}> cal:PM10  ?pm10 }}
        OPTIONAL {{ <{estacion_uri}> cal:PM2_5 ?pm25 }}
        OPTIONAL {{ <{estacion_uri}> cal:O3    ?o3   }}
        OPTIONAL {{ <{estacion_uri}> cal:BTX   ?btx  }}
    }}
    """
    rows = run_query(query)
    if not rows:
        return {}

    row = rows[0]

    def get(name):
        return row[name]["value"] if name in row else None

    return {
        "NO2": get("no2"),
        "SO2": get("so2"),
        "PM10": get("pm10"),
        "PM2.5": get("pm25"),
        "O3": get("o3"),
        "BTX": get("btx"),
    }

def imprimir_gases_estacion(codigo, nombre, gases):
    print(f"\n=== Capacidades de la estación {codigo} - {nombre} ===\n")

    for gas, valor in gases.items():
        texto = valor if valor else "no especificado"
        print(f"  {gas}: {texto}")

    print()

# PUNTOS DE MUESTREO
def obtener_puntos_muestreo_estacion(uri_estacion: str):
    query = PREFIXES + f"""
    SELECT DISTINCT ?punto
    WHERE {{
        ?medicion a cal:Medicion ;
                cal:estaEnEstacion <{uri_estacion}> ;
                cal:PUNTO_MUESTREO ?punto .
    }}
    ORDER BY ?punto
    """
    rows = run_query(query)
    return [row["punto"]["value"] for row in rows]

def seleccionar_punto_muestreo(puntos):
    while True:
        print("\n=== Puntos de muestreo ===\n")
        for i, p in enumerate(puntos, start=1):
            print(f"  {i}. {p}")

        eleccion = leer_opcion("Elige un punto")

        if eleccion == "100":
            exit()
        if eleccion == "99":
            return "INICIO"
        if eleccion == "0":
            return None

        try:
            idx = int(eleccion)
            if 1 <= idx <= len(puntos):
                return puntos[idx - 1]
        except:
            pass

        print("Opción inválida.")

# FILAS DE MEDICIÓN
def obtener_filas_medicion(uri_estacion, punto_muestreo):
    query = PREFIXES + f"""
    SELECT DISTINCT ?medicion ?ano ?mes ?dia ?magnitud
    WHERE {{
        ?medicion a cal:Medicion ;
                cal:estaEnEstacion <{uri_estacion}> ;
                cal:PUNTO_MUESTREO "{punto_muestreo}" ;
                cal:ANO ?ano ;
                cal:MES ?mes ;
                cal:DIA ?dia ;
                cal:MAGNITUD ?magnitud .
    }}
    ORDER BY ?ano ?mes ?dia ?magnitud
    """
    rows = run_query(query)
    return [(row["medicion"]["value"],
            row["ano"]["value"],
            row["mes"]["value"],
            row["dia"]["value"],
            row["magnitud"]["value"])
            for row in rows]

def seleccionar_fila_medicion(filas):
    while True:
        print("\n=== Filas disponibles ===\n")
        for i, (_, ano, mes, dia, magnitud) in enumerate(filas, start=1):
            print(f"  {i}. {dia}/{mes}/{ano} | Magnitud: {magnitud}")

        eleccion = leer_opcion("Selecciona una fila")

        if eleccion == "100":
            exit()
        if eleccion == "99":
            return "INICIO"
        if eleccion == "0":
            return None

        try:
            idx = int(eleccion)
            if 1 <= idx <= len(filas):
                return filas[idx - 1]
        except:
            pass

        print("Opción inválida.")

# DETALLES DE MEDICIÓN
def obtener_detalle_medicion(medicion_uri: str):
    query = PREFIXES + f"""
    SELECT ?ano ?mes ?dia ?magnitud
        ?h01 ?h02 ?h03 ?h04 ?h05 ?h06 ?h07 ?h08 ?h09 ?h10 ?h11 ?h12
        ?h13 ?h14 ?h15 ?h16 ?h17 ?h18 ?h19 ?h20 ?h21 ?h22 ?h23 ?h24
        ?v01 ?v02 ?v03 ?v04 ?v05 ?v06 ?v07 ?v08 ?v09 ?v10 ?v11 ?v12
        ?v13 ?v14 ?v15 ?v16 ?v17 ?v18 ?v19 ?v20 ?v21 ?v22 ?v23 ?v24
    WHERE {{
        <{medicion_uri}>
            cal:ANO ?ano ;
            cal:MES ?mes ;
            cal:DIA ?dia ;
            cal:MAGNITUD ?magnitud .
        OPTIONAL {{ <{medicion_uri}> cal:H01 ?h01 }}
        OPTIONAL {{ <{medicion_uri}> cal:H02 ?h02 }}
        OPTIONAL {{ <{medicion_uri}> cal:H03 ?h03 }}
        OPTIONAL {{ <{medicion_uri}> cal:H04 ?h04 }}
        OPTIONAL {{ <{medicion_uri}> cal:H05 ?h05 }}
        OPTIONAL {{ <{medicion_uri}> cal:H06 ?h06 }}
        OPTIONAL {{ <{medicion_uri}> cal:H07 ?h07 }}
        OPTIONAL {{ <{medicion_uri}> cal:H08 ?h08 }}
        OPTIONAL {{ <{medicion_uri}> cal:H09 ?h09 }}
        OPTIONAL {{ <{medicion_uri}> cal:H10 ?h10 }}
        OPTIONAL {{ <{medicion_uri}> cal:H11 ?h11 }}
        OPTIONAL {{ <{medicion_uri}> cal:H12 ?h12 }}
        OPTIONAL {{ <{medicion_uri}> cal:H13 ?h13 }}
        OPTIONAL {{ <{medicion_uri}> cal:H14 ?h14 }}
        OPTIONAL {{ <{medicion_uri}> cal:H15 ?h15 }}
        OPTIONAL {{ <{medicion_uri}> cal:H16 ?h16 }}
        OPTIONAL {{ <{medicion_uri}> cal:H17 ?h17 }}
        OPTIONAL {{ <{medicion_uri}> cal:H18 ?h18 }}
        OPTIONAL {{ <{medicion_uri}> cal:H19 ?h19 }}
        OPTIONAL {{ <{medicion_uri}> cal:H20 ?h20 }}
        OPTIONAL {{ <{medicion_uri}> cal:H21 ?h21 }}
        OPTIONAL {{ <{medicion_uri}> cal:H22 ?h22 }}
        OPTIONAL {{ <{medicion_uri}> cal:H23 ?h23 }}
        OPTIONAL {{ <{medicion_uri}> cal:H24 ?h24 }}
        OPTIONAL {{ <{medicion_uri}> cal:V01 ?v01 }}
        OPTIONAL {{ <{medicion_uri}> cal:V02 ?v02 }}
        OPTIONAL {{ <{medicion_uri}> cal:V03 ?v03 }}
        OPTIONAL {{ <{medicion_uri}> cal:V04 ?v04 }}
        OPTIONAL {{ <{medicion_uri}> cal:V05 ?v05 }}
        OPTIONAL {{ <{medicion_uri}> cal:V06 ?v06 }}
        OPTIONAL {{ <{medicion_uri}> cal:V07 ?v07 }}
        OPTIONAL {{ <{medicion_uri}> cal:V08 ?v08 }}
        OPTIONAL {{ <{medicion_uri}> cal:V09 ?v09 }}
        OPTIONAL {{ <{medicion_uri}> cal:V10 ?v10 }}
        OPTIONAL {{ <{medicion_uri}> cal:V11 ?v11 }}
        OPTIONAL {{ <{medicion_uri}> cal:V12 ?v12 }}
        OPTIONAL {{ <{medicion_uri}> cal:V13 ?v13 }}
        OPTIONAL {{ <{medicion_uri}> cal:V14 ?v14 }}
        OPTIONAL {{ <{medicion_uri}> cal:V15 ?v15 }}
        OPTIONAL {{ <{medicion_uri}> cal:V16 ?v16 }}
        OPTIONAL {{ <{medicion_uri}> cal:V17 ?v17 }}
        OPTIONAL {{ <{medicion_uri}> cal:V18 ?v18 }}
        OPTIONAL {{ <{medicion_uri}> cal:V19 ?v19 }}
        OPTIONAL {{ <{medicion_uri}> cal:V20 ?v20 }}
        OPTIONAL {{ <{medicion_uri}> cal:V21 ?v21 }}
        OPTIONAL {{ <{medicion_uri}> cal:V22 ?v22 }}
        OPTIONAL {{ <{medicion_uri}> cal:V23 ?v23 }}
        OPTIONAL {{ <{medicion_uri}> cal:V24 ?v24 }}
    }}
    """
    rows = run_query(query)
    return rows[0] if rows else None


def imprimir_detalle_medicion(detalle):
    if not detalle:
        print("\nNo se han encontrado datos para esa medición.\n")
        return

    val = lambda v: detalle[v]["value"] if v in detalle else "-"

    print("\n=== Detalle de la medición ===\n")
    print(f"Fecha: {val('dia')}/{val('mes')}/{val('ano')}")
    print(f"Magnitud: {val('magnitud')}\n")

    print("Horas y Validaciones (HXX || VXX):\n")
    for h in range(1, 25):
        h_val = val(f"h{h:02d}")
        v_val = val(f"v{h:02d}")
        print(f"  H{h:02d}: {h_val}  ||  V{h:02d}: {v_val}")

    print()


# MAIN
def main():
    print("Conectando a GraphDB...\n")

    while True:
        print("\n=== INICIO ===\n")

        estaciones = listar_estaciones()
        if not estaciones:
            print("No se han encontrado estaciones.")
            return

        seleccion_est = seleccionar_estacion_por_codigo(estaciones)
        if seleccion_est is None:
            continue  # volver al inicio

        codigo, nombre_estacion, estacion_uri = seleccion_est

        gases = obtener_gases_estacion(estacion_uri)
        imprimir_gases_estacion(codigo, nombre_estacion, gases)

        puntos = obtener_puntos_muestreo_estacion(estacion_uri)
        punto = seleccionar_punto_muestreo(puntos)
        if punto is None:
            continue

        filas = obtener_filas_medicion(estacion_uri, punto)
        fila = seleccionar_fila_medicion(filas)
        if fila is None:
            continue

        medicion_uri, _, _, _, _ = fila

        detalle = obtener_detalle_medicion(medicion_uri)
        imprimir_detalle_medicion(detalle)

        print("\n0. Volver al inicio")
        print("100. Salir")

        op = input("\nElige una opción: ").strip()
        if op == "100":
            print("Saliendo...")
            return


if __name__ == "__main__":
    main()
    