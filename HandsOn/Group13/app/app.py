import streamlit as st
from rdflib import Graph, Namespace
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests
from itertools import islice
import locale
import urllib.parse
import folium
from streamlit_folium import folium_static
locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")

# ==========================================================
# FUNCIONES AUXILIARES
# ==========================================================

@st.cache_data
def cargar_y_extraer_datos(path):
    """Carga el RDF y extrae datos en una sola función cacheable."""
    # Cargar RDF
    g = Graph()
    g.parse(path, format="ttl")
    
    # Extraer datos
    ns1 = Namespace("http://example.org/def/base#")
    
    datos = []
    qids = set()


    # ==========================================================
    # EXTRAER DATOS CON SPARQL
    # ==========================================================

    query = """
    PREFIX ns1: <http://example.org/def/base#>

    SELECT ?accidente ?fecha ?distrito ?lat ?lng
    WHERE {
        ?accidente a ns1:Accident ;
                   ns1:hasDatetime ?fecha ;
                   ns1:hasDistrictName ?distrito ;
                   ns1:hasLat ?lat ;
                   ns1:hasLong ?lng .
    }
    """

    resultados = g.query(query)

    datos = []
    qids = set()

    # ==========================================================
    # EXTRAER DATOS CON SPARQL
    # ==========================================================

    query = """
    PREFIX ns1: <http://example.org/def/base#>

    SELECT ?accidente ?fecha ?distrito ?lat ?lng
    WHERE {
        ?accidente a ns1:Accident ;
                   ns1:hasDatetime ?fecha ;
                   ns1:hasDistrictName ?distrito ;
                   ns1:hasLat ?lat ;
                   ns1:hasLong ?lng .
    }
    """

    resultados = g.query(query)

    datos = []
    qids = set()

    # ==========================================================
    # EXTRAER DATOS CON SPARQL
    # ==========================================================

    query = """
    PREFIX ns1: <http://example.org/def/base#>

    SELECT ?accidente ?fecha ?distrito ?lat ?lng
    WHERE {
        ?accidente a ns1:Accident ;
                   ns1:hasDatetime ?fecha ;
                   ns1:hasDistrictName ?distrito ;
                   ns1:hasLat ?lat ;
                   ns1:hasLong ?lng .
    }
    """

    resultados = g.query(query)

    datos = []
    qids = set()

    # ==========================================================
    # EXTRAER DATOS CON SPARQL
    # ==========================================================

    query = """
    PREFIX ns1: <http://example.org/def/base#>

    SELECT ?accidente ?fecha ?distrito ?lat ?lng
    WHERE {
        ?accidente a ns1:Accident ;
                   ns1:hasDatetime ?fecha ;
                   ns1:hasDistrictName ?distrito ;
                   ns1:hasLat ?lat ;
                   ns1:hasLong ?lng .
    }
    """

    resultados = g.query(query)

    datos = []
    qids = set()

# ==========================================================
    # EXTRAER DATOS CON SPARQL
    # ==========================================================

    query = """
    PREFIX ns1: <http://example.org/def/base#>

    SELECT ?accidente ?fecha ?distrito ?lat ?lng
    WHERE {
        ?accidente a ns1:Accident ;
                   ns1:hasDatetime ?fecha ;
                   ns1:hasDistrictName ?distrito ;
                   ns1:hasLat ?lat ;
                   ns1:hasLong ?lng .
    }
    """

    resultados = g.query(query)

    datos = []
    qids = set()

    for accidente, fecha_literal, distrito_uri, lat_literal, lng_literal in resultados:

        # Fecha ISO
        try:
            fecha = datetime.fromisoformat(str(fecha_literal).replace("Z", "+00:00"))
        except Exception:
            fecha = None

        # Coordenadas
        try:
            lat = float(str(lat_literal)) if lat_literal else None
            lng = float(str(lng_literal)) if lng_literal else None
        except Exception:
            lat, lng = None, None

        # Nombre distrito desde URI
        if distrito_uri:
            distrito_str = str(distrito_uri)
            if "/distrito/" in distrito_str:
                distrito_name = distrito_str.split("/distrito/")[-1]
                distrito_name = urllib.parse.unquote(distrito_name)
            else:
                qid = extraer_qid(distrito_uri)
                if qid:
                    qids.add(qid)
                distrito_name = qid
        else:
            distrito_name = None

        datos.append({
            "accidente": str(accidente),
            "fecha": fecha,
            "qid": extraer_qid(distrito_uri),
            "distrito_name": distrito_name,
            "raw_distrito": str(distrito_uri),
            "lat": lat,
            "lng": lng
        })


    df = pd.DataFrame(datos)

    # Resolver nombres desde Wikidata solo si hay QIDs (formato antiguo)
    if qids:
        mapping = obtener_nombres_wikidata(qids)
        df["distrito"] = df["qid"].map(mapping).fillna(df["distrito_name"])
    else:
        # Usar directamente el nombre del distrito extraído de la URI
        df["distrito"] = df["distrito_name"]

    return df


def extraer_qid(valor):
    #"Extrae QID de una URI o literal."
    if not valor:
        return None
    s = str(valor).strip()
    if "/wiki/" in s:
        s = s.split("/wiki/")[-1]
    if "/entity/" in s:
        s = s.split("/entity/")[-1]
    if s.startswith("Q") and s[1:].isdigit():
        return s
    parts = s.rstrip("/").split("/")
    if parts[-1].startswith("Q") and parts[-1][1:].isdigit():
        return parts[-1]
    return None


def chunked(iterable, size):
    it = iter(iterable)
    while True:
        batch = list(islice(it, size))
        if not batch:
            break
        yield batch


@st.cache_data
def obtener_nombres_wikidata(qids):
    #"Devuelve diccionario {QID: nombre} consultando Wikidata."
    qids = list({q for q in qids if q})
    if not qids:
        return {}

    mapping = {}
    base_url = "https://www.wikidata.org/w/api.php"
    headers = {"User-Agent": "TFG-Moodle/1.0 (educational-use)"}

    for batch in chunked(qids, 50):
        params = {
            "action": "wbgetentities",
            "ids": "|".join(batch),
            "format": "json",
            "props": "labels",
            "languages": "es|en",
        }
        try:
            r = requests.get(base_url, params=params, headers=headers, timeout=10)
            r.raise_for_status()
            entities = r.json().get("entities", {})
            for qid, ent in entities.items():
                labels = ent.get("labels", {})
                if "es" in labels:
                    mapping[qid] = labels["es"]["value"]
                elif "en" in labels:
                    mapping[qid] = labels["en"]["value"]
                elif labels:
                    mapping[qid] = next(iter(labels.values())).get("value", qid)
                else:
                    mapping[qid] = qid
        except Exception:
            for q in batch:
                mapping[q] = q

    return mapping


# ==========================================================
# PROCESAR RDF
# ==========================================================

# La función extraer_datos ahora está integrada en cargar_y_extraer_datos


# ==========================================================
# ANÁLISIS
# ==========================================================

@st.cache_data
def accidentes_por_hora(df):
    df = df.dropna(subset=["fecha"])
    df["hora"] = df["fecha"].dt.hour
    return df.groupby("hora").size().reset_index(name="Nº Accidentes").reset_index(drop=True)

@st.cache_data
def accidentes_por_mes(df):
    df = df.dropna(subset=["fecha"])
    # Obtener nombre del mes en español
    df["mes"] = df["fecha"].dt.strftime("%B").str.capitalize()
    
    # Definir orden cronológico
    meses_orden = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                   "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    df["mes"] = pd.Categorical(df["mes"], categories=meses_orden, ordered=True)
    
    return df.groupby("mes").size().reset_index(name="Nº Accidentes").reset_index(drop=True)

@st.cache_data
def accidentes_por_dia_mes(df, mes_seleccionado):
    df = df.dropna(subset=["fecha"])
    df["mes"] = df["fecha"].dt.month
    df["día"] = df["fecha"].dt.day

    # Filtrar por mes seleccionado
    df_mes = df[df["mes"] == mes_seleccionado]

    # Número de días del mes seleccionado
    import calendar
    dias_mes = calendar.monthrange(2025, mes_seleccionado)[1]

    # Todos los días del mes
    todos_dias = pd.DataFrame({"día": range(1, dias_mes + 1)})

    # Contar accidentes por día
    df_dia = df_mes.groupby("día").size().reset_index(name="Nº Accidentes")

    # Combinar para incluir días sin accidentes
    df_dia = todos_dias.merge(df_dia, on="día", how="left").fillna(0)
    df_dia["Nº Accidentes"] = df_dia["Nº Accidentes"].astype(int)

    return df_dia

@st.cache_data
def accidentes_por_distrito(df):
    df = df.dropna(subset=["distrito"])
    return df.groupby("distrito").size().reset_index(name="Nº Accidentes").reset_index(drop=True)


# ==========================================================
# ANÁLISIS GEOGRÁFICO
# ==========================================================

def crear_mapa_accidentes(df, max_points=1000):
    
    # Crear clave única para el cache basada en los parámetros
    cache_key = f"mapa_accidentes_{len(df)}_{max_points}"
    
    # Solo crear el mapa si no existe en session_state o si los parámetros cambiaron
    if cache_key not in st.session_state:
        # Filtrar accidentes con coordenadas válidas, distrito y fecha
        df_geo = df.dropna(subset=["lat", "lng", "distrito", "fecha"])

        if df_geo.empty:
            st.session_state[cache_key] = None
            return None
        
        # Limitar puntos para rendimiento
        if len(df_geo) > max_points:
            df_geo = df_geo.sample(n=max_points, random_state=42)
        
        # Centrar el mapa en Madrid
        madrid_center = [40.4168, -3.7038]
        
        # Crear mapa base
        m = folium.Map(
            location=madrid_center,
            zoom_start=11
        )
        
        # Añadir marcadores para cada accidente
        for idx, row in df_geo.iterrows():
            # Formatear fecha de manera segura
            if pd.notna(row['fecha']):
                fecha_str = row['fecha'].strftime('%d/%m/%Y %H:%M')
            else:
                fecha_str = 'Fecha no disponible'
            
            # Crear popup con texto simple
            # Extraer expid del URI del accidente
            expid = row['accidente'].split('/')[-1] if row['accidente'] else 'N/A'
            
            popup_text = f"""Accidente de Tráfico
ID: {expid}
Distrito: {row['distrito'] or 'No especificado'}
Fecha: {fecha_str}"""
            
            # Crear marcador con popup simple
            folium.CircleMarker(
                location=[row["lat"], row["lng"]],
                popup=popup_text,
                tooltip=f"Accidente en {row['distrito'] or 'Distrito desconocido'}",
                radius=5,
                color="#d32f2f",
                fill=True,
                fillColor="#ff5252",
                weight=2,
                fillOpacity=0.7,
                opacity=0.9
            ).add_to(m)
        
        # Guardar en session_state
        st.session_state[cache_key] = m
    
    return st.session_state[cache_key]


# ==========================================================
# INTERFAZ STREAMLIT
# ==========================================================

def main():
    st.markdown(
    "<h1 style='text-align: center;'>Análisis de Accidentes de Tráfico Madrid 2025</h1>",
    unsafe_allow_html=True
)

    df = cargar_y_extraer_datos("accidentes-rdf-with-links-with-latlong.ttl")

    if "active_analysis" not in st.session_state:
        st.session_state.active_analysis = None



    st.write("### Selecciona el tipo de análisis:")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        btn_hora = st.button("Por hora", use_container_width=True)
    with col2:
        btn_mes = st.button("Por mes", use_container_width=True)
    with col3:
        btn_dia = st.button("Por día", use_container_width=True)
    with col4:
        btn_distrito = st.button("Por distrito", use_container_width=True)
    with col5:
        btn_mapa = st.button("Mapa", use_container_width=True)

    if btn_hora:
        st.session_state.active_analysis = "hora"
    if btn_mes:
        st.session_state.active_analysis = "mes"
    if btn_dia:
        st.session_state.active_analysis = "dia"
    if btn_distrito:
        st.session_state.active_analysis = "distrito"
    if btn_mapa:
        st.session_state.active_analysis = "mapa"

    if st.session_state.active_analysis == "hora":
        df_h = accidentes_por_hora(df)
        fig = px.bar(df_h, x="hora", y="Nº Accidentes",
                     title="Accidentes por hora",
                     labels={"hora": "Hora", "Nº Accidentes": "Número de accidentes"})
        fig.update_xaxes(
            tickmode='array',
            tickvals=list(range(0, 24, 2)),
            ticktext=[str(h) for h in range(0, 24, 2)]
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_h, hide_index=True)

    elif st.session_state.active_analysis == "mes":
        df_m = accidentes_por_mes(df)
        fig = px.bar(df_m, x="mes", y="Nº Accidentes",
                     title="Accidentes por mes",
                     labels={"mes": "Mes", "Nº Accidentes": "Número de accidentes"})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_m, hide_index=True)

    elif st.session_state.active_analysis == "dia":
        meses_orden = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                       "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        mes_nombre = st.selectbox("Selecciona el mes:", meses_orden, key="mes_dia")
        mes_num = meses_orden.index(mes_nombre) + 1

        df_dia = accidentes_por_dia_mes(df, mes_num)
        fig = px.bar(df_dia, x="día", y="Nº Accidentes",
                     title=f"Accidentes por día de {mes_nombre} 2025",
                     labels={"día": "Día del mes", "Nº Accidentes": "Número de accidentes"})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_dia, hide_index=True)

    elif st.session_state.active_analysis == "distrito":
        df_d = accidentes_por_distrito(df)
        fig = px.bar(df_d, x="distrito", y="Nº Accidentes",
                     title="Accidentes por distrito",
                     labels={"distrito": "Distrito", "Nº Accidentes": "Número de accidentes"})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_d, hide_index=True)

    elif st.session_state.active_analysis == "mapa":
        st.subheader("Mapa Interactivo de Accidentes de Tráfico")
        
        # Filtrar datos con coordenadas válidas
        df_geo = df.dropna(subset=["lat", "lng"])
        total_con_coords = len(df_geo)
        total_accidentes = len(df)
        
        if total_con_coords > 0:
            # Controles del mapa
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("Regenerar Mapa", use_container_width=True):
                    # Limpiar todos los mapas del cache
                    keys_to_remove = [k for k in st.session_state.keys() if k.startswith('mapa_accidentes_')]
                    for key in keys_to_remove:
                        del st.session_state[key]
            
            # Slider en toda la anchura
            max_points = st.slider(
                "Máx. puntos a mostrar", 
                min_value=100, 
                max_value=total_con_coords, 
                value=min(1000, total_con_coords), 
                step=100,
                help="Limitar puntos mejora el rendimiento"
            )
            
            # Crear y mostrar mapa
            with st.spinner("Cargando mapa..."):
                mapa = crear_mapa_accidentes(df_geo, max_points)
            
            if mapa:
                # Mostrar mapa usando folium_static (no interactivo pero estable)
                folium_static(mapa, width=700, height=500)
            else:
                st.error("No se pudo crear el mapa")
        else:
            st.warning("No hay datos de coordenadas disponibles para mostrar en el mapa")

if __name__ == "__main__":
    main()