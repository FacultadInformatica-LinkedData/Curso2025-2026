import streamlit as st
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery
import pandas as pd
from urllib.parse import unquote
import re
import time
from SPARQLWrapper import SPARQLWrapper, JSON



#source app/venv/bin/activate
#streamlit run app/app_streamlit.py

st.set_page_config(
    page_title="Barcelona Activities Explorer",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
     /* Ocultar el panel superior de configuración */
    #MainMenu {visibility: hidden;}
    
    /* Ocultar el footer "Made with Streamlit" */
    footer {visibility: hidden;}
    
    /* Ocultar la barra superior con los botones de configuración */
    .stToolbar {display: none;}
    
    /* Ocultar el botón de hamburguesa del menú */
    button[title="View fullscreen"] {display: none;}
    
    /* Ocultar la barra de herramientas superior */
    header[data-testid="stHeader"] {display: none;}
    
    .main > div {
        padding-top: 0.1rem;
    }
    /* Tema oscuro principal */
    .stApp {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1f1f1f 100%);
    }
    
    /* Tarjetas con efecto glassmorphism */
    .query-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        margin: 15px 0;
    }
    
    /* Métricas con degradado en escala de grises */
    .metric-card {
        background: linear-gradient(135deg, #3a3a3a 0%, #4a4a4a 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
        transition: transform 0.3s;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        background: linear-gradient(135deg, #4a4a4a 0%, #5a5a5a 100%);
    }
    
    /* Títulos elegantes */
    h1, h2, h3 {
        color: #e0e0e0;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    /* Botones elegantes en escala de grises */
    .stButton>button {
        background: linear-gradient(135deg, #505050 0%, #606060 100%);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(255, 255, 255, 0.2);
        background: linear-gradient(135deg, #606060 0%, #707070 100%);
    }
    
    /* Sidebar oscuro */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a1a 0%, #252525 100%);
    }
    
    /* Radio buttons personalizados */
    .stRadio > label {
        color: #e0e0e0;
        font-weight: 500;
    }
    
    /* Texto general */
    p, label, span {
        color: #c0c0c0;
    }
    
    /* Divisores */
    hr {
        border-color: rgba(255, 255, 255, 0.1);
    }
    
    /* Expander oscuro */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        color: #e0e0e0;
    }
    
    /* DataFrames */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    /* Selectbox y inputs */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.2);
    }
    </style>
""", unsafe_allow_html=True)


#Si s parece una URI, devolver la parte local (después de / o #)
def _shorten_uri(s):
    if s.startswith('http://') or s.startswith('https://'):
        parts = re.split(r'[#/]', s)
        if parts:
            return parts[-1]
    return s


@st.cache_resource
def load_graph():
    """Carga el grafo RDF (con caché para mejor rendimiento)"""
    g = Graph()
    githubStorage = "https://raw.githubusercontent.com/Istrar/Curso2025-2026/refs/heads/master/HandsOn/Group02/rdf"
    try:
        g.parse(githubStorage + "/knowledge-graph-with-links.ttl", format="turtle")
        return g, None
    except Exception as e:
        return None, str(e)


def execute_query(g, query):
    #Ejecuta una query SPARQL y devuelve un DataFrame
    try:
        res = g.query(prepareQuery(query))
        rows = list(res)
        if not rows:
            return pd.DataFrame(), None

        # Obtener nombres de variables
        headers = [str(v) for v in getattr(res, 'vars', [])]

        # Procesar resultados
        data = []
        for r in rows:
            row_data = []
            for x in r:
                if x is not None:
                    s = str(x)
                    try:
                        s = unquote(s)
                    except:
                        pass
                    s = _shorten_uri(s)
                    row_data.append(s)
                else:
                    row_data.append("")
            data.append(row_data)

        df = pd.DataFrame(data, columns=headers)
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)


def execute_wikidata_query(sparql_query):
    """Ejecuta una query SPARQL en Wikidata y devuelve un DataFrame"""
    attempts = 3
    backoff = 1.0
    last_err = None
    for attempt in range(attempts):
        try:
            sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
            sparql.setQuery(sparql_query)
            sparql.setReturnFormat(JSON)
            sparql.addCustomHttpHeader(
                "User-Agent", "BarcelonaActivitiesExplorer/1.0")

            results = sparql.query().convert()

            if not results.get("results", {}).get("bindings"):
                return pd.DataFrame(), None
            # si hay resultados
            bindings = results["results"]["bindings"]
            headers = list(bindings[0].keys()) if bindings else []

            data = []
            for binding in bindings:
                row = []
                for header in headers:
                    value = binding.get(header, {}).get("value", "")
                    # Acortar URIs si es necesario
                    value = _shorten_uri(value) if value else ""
                    row.append(value)
                data.append(row)

            df = pd.DataFrame(data, columns=headers)
            return df, None
        except Exception as e:
            last_err = e
            # Si no es el último intento, esperar con backoff y reintentar
            if attempt < attempts - 1:
                time.sleep(backoff)
                backoff *= 2
                continue
            else:
                return pd.DataFrame(), str(last_err)


def execute_combined_query(g, rdf_query, wikidata_query_template, input_variable, debug=False):
    """
    Ejecuta una query RDF, luego usa sus resultados como input para Wikidata con procesamiento por batches,
    y devuelve AMBOS DataFrames: el RDF original y el combinado RDF+Wikidata

    Args:
        g: Grafo RDF
        rdf_query: Query SPARQL para el RDF local
        wikidata_query_template: Template de query Wikidata con placeholder {values}
        input_variable: Variable del resultado RDF a usar como input
        wikidata_input_var: Variable en la query Wikidata donde insertar los valores (debe ser 'searchTerm')
        merge_key: Tupla (col_rdf, col_wikidata) para hacer el merge. Si es None, usa searchTerm
        debug: Si es True, retorna también las queries generadas para cada batch

    Returns:
        (df_rdf_original, df_combined, error, batch_info): DataFrame RDF original, DataFrame combinado, mensaje de error, info de batches
    """
    # Ejecutar query RDF
    df_rdf, error = execute_query(g, rdf_query)
    if error:
        return df_rdf if df_rdf is not None else pd.DataFrame(), None, error, None

    if df_rdf.empty:
        return df_rdf, None, "Query RDF no devolvió resultados", None

    # Extraer valores únicos de la columna especificada
    if input_variable not in df_rdf.columns:
        return df_rdf, df_rdf, f"Variable '{input_variable}' no encontrada en resultados RDF", None

    input_values = df_rdf[input_variable].dropna().unique()

    if len(input_values) == 0:
        return df_rdf, df_rdf, "No hay valores únicos para consultar en Wikidata", None

    # 4. PROCESAMIENTO POR BATCHES para evitar timeouts
    batch_size = 10
    max_values = min(len(input_values), 200)  # Limitar a 200 valores máximo
    batches = [input_values[i:i+batch_size]
               for i in range(0, max_values, batch_size)]

    df_wikidata_list = []
    errors = []
    batch_queries = []  # Para almacenar las queries generadas (debug)

    for idx, batch in enumerate(batches):
        # Construir VALUES clause para este batch
        # Si el valor parece una URI de Wikidata o un QID, usar formato wd:Q123
        # Si no, usar como string entrecomillado
        formatted_values = []
        for v in batch:
            v_str = str(v)
            # Detectar URIs completas de Wikidata (http://www.wikidata.org/entity/Q...)
            if 'wikidata.org/entity/' in v_str:
                qid = v_str.split('/')[-1]
                formatted_values.append(f'wd:{qid}')
            # Detectar QIDs ya acortados (Q seguido de números)
            elif re.match(r'^Q\d+$', v_str):
                formatted_values.append(f'wd:{v_str}')
            else:
                # String normal, entrecomillar
                formatted_values.append(f'"{v_str.replace("\"", "\\\"")}"')
        
        batch_values_clause = " ".join(formatted_values)
        wikidata_query = wikidata_query_template.replace(
            "{values}", batch_values_clause)

        # Guardar query generada para debug
        batch_queries.append({
            'batch_num': idx + 1,
            'values_count': len(batch),
            'values': list(batch),
            'query': wikidata_query
        })

        # Ejecutar query para este batch
        df_batch, error_wd = execute_wikidata_query(wikidata_query)

        if error_wd:
            errors.append(error_wd)
        elif df_batch is not None and not df_batch.empty:
            df_wikidata_list.append(df_batch)

        # Pausa cortés entre requests
        if len(batches) > 1:
            time.sleep(0.8)

    # Concatenar resultados de todos los batches
    if not df_wikidata_list:
        error_msg = f"Wikidata no devolvió resultados. Errores: {'; '.join(errors)}" if errors else "Wikidata no devolvió resultados"
        return df_rdf, df_rdf, error_msg, batch_queries if debug else None

    df_wikidata = pd.concat(df_wikidata_list, ignore_index=True, sort=False)
    df_wikidata = df_wikidata.drop_duplicates()


    # Renombrar searchTerm a la variable del RDF para hacer merge
    df_wikidata_renamed = df_wikidata.copy()
    df_wikidata_renamed.rename(
        columns={'searchTerm': input_variable}, inplace=True)
    # Añadir prefijo wd_ a todas las columnas de Wikidata excepto la de join
    cols_to_rename = {
        col: f'wd_{col}' for col in df_wikidata_renamed.columns if col != input_variable}
    df_wikidata_renamed.rename(columns=cols_to_rename, inplace=True)
    # Hacer merge usando INNER JOIN para mantener todas las filas RDF
    df_combined = pd.merge(df_rdf, df_wikidata_renamed,
                           on=input_variable, how='inner', suffixes=('', '_dup'))
    df_combined = df_combined.loc[:, ~
                                  df_combined.columns.str.endswith('_dup')]
    
    # Eliminar filas duplicadas que se generan cuando Wikidata devuelve múltiples resultados por entidad
    rdf_columns = list(df_rdf.columns)
    df_combined = df_combined.drop_duplicates(subset=rdf_columns, keep='first')
    
    # Reemplazar NaN/None por cadenas vacías
    df_combined = df_combined.fillna('')
    return df_rdf, df_combined, None, batch_queries if debug else None

# Definir las queries (10 queries)
QUERIES = {
    1: {
        "nombre": "Actividades con aforo >= 100",
        "description": "Todas las actividades con aforo >= 100 concultando su título, tipo, precio, fechas, aforo y organizador",
        "tipo": "simple",
        "query": '''
        PREFIX att: <http://data.barcelona.cat/att/>
        PREFIX rel: <http://data.barcelona.cat/rel/>
        PREFIX node: <http://data.barcelona.cat/node/>
        
        SELECT ?actividad ?titulo ?tipo ?precio ?fechaInicio ?fechaFin ?aforo ?organizador
        WHERE {
          ?actividad a node:Actividad ;
                    att:titulo ?titulo ;
                    att:precio ?precio ;
                    att:fechaInicio ?fechaInicio ;
                    att:fechaFin ?fechaFin ;
                    att:tipo ?tipo ;
                    att:aforo ?aforo ;
          			rel:isHosted ?organizador ;
                    # Filtra solo actividades con aforo mayor o igual a 100
                    FILTER (?aforo >= 100) .
        }
        # Ordena los resultados por fecha de inicio
        ORDER BY ?fechaInicio
        '''
    },
    2: {
        "nombre": "Información de los organizadores de actividades con aforo >= 100",
        "description": "Dado el set de actividades con aforo >= 100, se pregunta el nombre y el tipo del organizador",
        "tipo": "combinada",
        "query_rdf": '''
        PREFIX att: <http://data.barcelona.cat/att/>
        PREFIX rel: <http://data.barcelona.cat/rel/>
        PREFIX node: <http://data.barcelona.cat/node/>
        
        SELECT ?actividad ?titulo ?tipo ?precio ?fechaInicio ?fechaFin ?aforo ?organizador ?orgWikidata
        WHERE {
          ?actividad a node:Actividad ;
                    att:titulo ?titulo ;
                    att:precio ?precio ;
                    att:fechaInicio ?fechaInicio ;
                    att:fechaFin ?fechaFin ;
                    att:tipo ?tipo ;
                    att:aforo ?aforo ;
                    rel:isHosted ?organizador ;
                    FILTER (?aforo >= 100) .
          # Obtiene el URI de Wikidata del organizador
          ?organizador owl:sameAs ?orgWikidata .
        }
        ORDER BY ?fechaInicio
        LIMIT 80
        ''',
        "query_wikidata": '''
        SELECT ?searchTerm ?nombreOrganizador ?tipoOrganizador
        WHERE {
          VALUES ?searchTerm { {values} }

           # Obtiene el nombre del organizador
           ?searchTerm rdfs:label ?nombreOrganizador .
           FILTER (LANG(?nombreOrganizador) = "en")

           # Obtiene el tipo de organizador (P31: instance of)
           OPTIONAL {
           ?searchTerm wdt:P31 ?organizadorEntity. 
           ?organizadorEntity rdfs:label ?tipoOrganizador .
           FILTER (LANG(?tipoOrganizador) = "en")
           } 
        }
        ''',
        "input_var": "orgWikidata",
        "wikidata_var": "searchTerm"
    },
    3: {
        "nombre": "Filtrado por tipo (ayuntamiento) de los organizadores de actividades con aforo >= 100",
        "description": "Dado el set de actividades con aforo >= 100, se selecciona aquellos que son ayuntamientos y se pregunta el nombre, la direccion del edificio del ayuntamiento y su estilo arquitectonico",
        "tipo": "combinada",
        "query_rdf": '''
        PREFIX att: <http://data.barcelona.cat/att/>
        PREFIX rel: <http://data.barcelona.cat/rel/>
        PREFIX node: <http://data.barcelona.cat/node/>
        
        SELECT ?actividad ?titulo ?tipo ?precio ?fechaInicio ?fechaFin ?aforo ?organizador ?orgWikidata
        WHERE {
          ?actividad a node:Actividad ;
                    att:titulo ?titulo ;
                    att:precio ?precio ;
                    att:fechaInicio ?fechaInicio ;
                    att:fechaFin ?fechaFin ;
                    att:tipo ?tipo ;
                    att:aforo ?aforo ;
                    rel:isHosted ?organizador ;
                    FILTER (?aforo >= 100) .
          # Obtiene el enlace a Wikidata del organizador
          ?organizador owl:sameAs ?orgWikidata .
        }
        ORDER BY ?fechaInicio
        LIMIT 200
        ''',
        "query_wikidata": '''
        SELECT ?searchTerm ?nombreOrganizador ?direccion ?estilo
        WHERE {
            VALUES ?searchTerm { {values} }

            # Filtra por tipo ayuntamiento (Q22996476)
            ?searchTerm wdt:P31 wd:Q22996476 .
            ?searchTerm rdfs:label ?nombreOrganizador .
            FILTER ( LANG ( ?nombreOrganizador ) = "en" ) 

            # Obtiene la sede del ayuntamiento (P159: headquarters location)
            ?searchTerm wdt:P159 ?edificioEntity .

            # Obtiene la dirección del edificio (P2795: street address)
            ?edificioEntity wdt:P2795 ?direccion .

            # Obtiene el estilo arquitectónico (P149: architectural style)
            ?edificioEntity wdt:P149 ?estiloEntity .
            ?estiloEntity rdfs:label ?estilo .
            FILTER ( LANG ( ?estilo ) = "en" )
        }
        ''',
        "input_var": "orgWikidata",
        "wikidata_var": "searchTerm"
    },
    4: {
        "nombre": "Comarcas",
        "description": "Devuelve las comarcas ordenadas por nombre",
        "tipo": "simple",
        "query": '''        
        PREFIX node: <http://data.barcelona.cat/node/>
        PREFIX rel: <http://data.barcelona.cat/rel/>

        SELECT ?comarca ?orgWikidata
        WHERE {
          ?municipio rel:isContained ?comarca .
    		?comarca owl:sameAs ?orgWikidata .
        }
        ORDER BY ?nombre
        '''
    },
    5: {
        "nombre": "Información Geográfica y Demográfica de Comarcas",
        "description": "Consulta datos detallados de las comarcas: nombre, capital, punto más alto, área y población obtenidos de Wikidata",
        "tipo": "combinada",
        "query_rdf": '''
        PREFIX node: <http://data.barcelona.cat/node/>
        PREFIX rel: <http://data.barcelona.cat/rel/>


        SELECT ?comarca ?orgWikidata
        WHERE {
          ?municipio rel:isContained ?comarca .
    		?comarca owl:sameAs ?orgWikidata .
    
        }
        ORDER BY ?nombre
        ''',
        "query_wikidata": '''
        SELECT ?nombreComarca ?capital ?puntoMasAlto ?area ?poblacion
        WHERE {
            VALUES ?searchTerm { {values} }

            # Nombre de la comarca
            OPTIONAL {
            ?searchTerm rdfs:label ?nombreComarca .
            FILTER ( LANG ( ?nombreComarca ) = "en" ) 
            }

            # Capital de la comarca (P36: capital)
            OPTIONAL { 
            ?searchTerm wdt:P36 ?capitalEntity .
            ?capitalEntity rdfs:label ?capital .
            FILTER ( LANG ( ?capital ) = "en" ) 
            }

            # Punto más alto (P610: highest point)
            OPTIONAL { 
            ?searchTerm wdt:P610 ?puntoMasAltoEntity .
            ?puntoMasAltoEntity rdfs:label ?puntoMasAlto .
            FILTER ( LANG ( ?puntoMasAlto ) = "en" ) 
            }

            # Población (P1082: population)
            ?searchTerm wdt:P1082 ?poblacion .

            # Área (P2046: area)
            ?searchTerm wdt:P2046 ?area .
            
        }
        ''',
        "input_var": "orgWikidata",
        "wikidata_var": "searchTerm"
    },
    6: {
        "nombre": "Población de Municipios por Género",
        "description": "Obtiene estadísticas demográficas de municipios donde se realizan actividades: población total, masculina, femenina y número de hogares",
        "tipo": "combinada",
        "query_rdf": '''
        PREFIX rel: <http://data.barcelona.cat/rel/>
        SELECT ?municipio ?orgWikidata
        WHERE {
          ?actividad rel:placed ?municipio .
          # Obtiene el enlace a Wikidata del municipio
          ?municipio owl:sameAs ?orgWikidata .
        }
        LIMIT 300
        ''',
        "query_wikidata": '''
        SELECT ?searchTerm ?nombreOrganizador ?poblacion ?poblacionMasculina ?poblacionFemenina ?households
        WHERE {
          VALUES ?searchTerm { {values} }

           # Población total (P1082: population)
           ?searchTerm wdt:P1082 ?poblacion . 

           # Población masculina (P1540: male population)
           OPTIONAL { 
           ?searchTerm wdt:P1540 ?poblacionMasculina . 
           }

           # Población femenina (P1539: female population)
           OPTIONAL { 
           ?searchTerm wdt:P1539 ?poblacionFemenina . 
           }

           # Número de hogares (P1538: number of households)
           OPTIONAL { 
           ?searchTerm wdt:P1538 ?households . 
           }
           
        }
        ''',
        "input_var": "orgWikidata",
        "wikidata_var": "searchTerm"
    },
    7: {
        "nombre": "Autoridades y Lenguas Oficiales de Municipios",
        "description": "Consulta información política de municipios con actividades: presidente actual e idiomas oficiales",
        "tipo": "combinada",
        "query_rdf": '''
        PREFIX rel: <http://data.barcelona.cat/rel/>

        SELECT ?municipio ?orgWikidata
        WHERE {
        ?actividad rel:placed ?municipio .
        # Obtiene el enlace a Wikidata del municipio
        ?municipio owl:sameAs ?orgWikidata .
        }
        LIMIT 200
        ''',
        "query_wikidata": '''
                
        SELECT ?searchTerm ?presidente ?idiomaOficial 
        WHERE {
            VALUES ?searchTerm { {values} }

            # Jefe de gobierno actual (P6: head of government)
            ?searchTerm wdt:P6 ?presidenteEntity . 
            ?presidenteEntity rdfs:label ?presidente .
            FILTER(LANG(?presidente) = "en")

            # Idioma oficial (P37: official language)
            OPTIONAL { 
            ?searchTerm wdt:P37 ?idiomaOficialEntity . 
            ?idiomaOficialEntity rdfs:label ?idiomaOficial .
            FILTER(LANG(?idiomaOficial) = "en")
            } 
        }
        ''',
        "input_var": "orgWikidata",
        "wikidata_var": "searchTerm"
    },
    8: {
        "nombre": "Información Geográfica de Municipios",
        "description": "Obtiene datos geográficos de municipios con actividades: país, capital, área, fronteras, zona horaria, coordenadas y elevación",
        "tipo": "combinada",
        "query_rdf": '''
        PREFIX rel: <http://data.barcelona.cat/rel/>
        
        SELECT ?municipio ?orgWikidata
        WHERE {
        ?actividad rel:placed ?municipio .
        # Obtiene el enlace a Wikidata del municipio
        ?municipio owl:sameAs ?orgWikidata .
        }
        LIMIT 200
        ''',
        "query_wikidata": '''
        SELECT ?searchTerm ?nombreMunicipio ?pais ?capital ?area ?frontera ?zonaHoraria ?coordenadas ?elevacion
        WHERE {
            VALUES ?searchTerm { {values} }

            # Nombre del municipio
            ?searchTerm rdfs:label ?nombreMunicipio . 
            FILTER(LANG(?nombreMunicipio)="en") 

            # País al que pertenece (P17: country)
            ?searchTerm wdt:P17 ?paisEntity . 
            ?paisEntity rdfs:label ?pais . 
            FILTER(LANG(?pais)="en") 

            # Capital (P36: capital)
            OPTIONAL { 
            ?searchTerm wdt:P36 ?capitalEntity . 
            ?capitalEntity rdfs:label ?capital . 
            FILTER(LANG(?capital)="en") 
            }


            # Área en km2 (P2046: area)
            OPTIONAL {
            ?searchTerm wdt:P2046 ?area . 
            }

            # Territorios fronterizos (P47: shares border with)
            OPTIONAL { 
            ?searchTerm wdt:P47 ?fronteraEntity . 
            ?fronteraEntity rdfs:label ?frontera . 
            FILTER(LANG(?frontera)="en") 
            }

            # Zona horaria (P421: located in time zone)
            OPTIONAL { 
            ?searchTerm wdt:P421 ?zonaHorariaEntity . 
            ?zonaHorariaEntity rdfs:label ?zonaHoraria . 
            FILTER(LANG(?zonaHoraria)="en") 
            }

            # Coordenadas geográficas (P625: coordinate location)
            ?searchTerm wdt:P625 ?coordenadas .

            # Elevación sobre el nivel del mar (P2044: elevation above sea level)
            OPTIONAL { 
            ?searchTerm wdt:P2044 ?elevacion . 
            }
        }
        ''',
        "input_var": "orgWikidata",
        "wikidata_var": "searchTerm"
    }
}


def main():
    # Título principal
        # Inicializar session state
    if 'query_num' not in st.session_state:
        st.session_state.query_num = 1
    if 'resultados' not in st.session_state:
        st.session_state.resultados = None
    if 'resultados_combinados' not in st.session_state:
        st.session_state.resultados_combinados = None
    if 'query_ejecutada' not in st.session_state:
        st.session_state.query_ejecutada = None
    if 'batch_info' not in st.session_state:
        st.session_state.batch_info = None
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: 0; font-size: 3em;'>
            Barcelona Activities Explorer
        </h1>
        <p style='text-align: center; color: #a0a0a0; font-size: 1.2em; margin-top: 10px;'>
            Explorador de Actividades Culturales de Barcelona SPARQL
        </p>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Cargar el grafo
    with st.spinner("Cargando datos del grafo RDF..."):
        g, error = load_graph()

    if error:
        st.error(f"Error al cargar el grafo: {error}")
        st.stop()

    if g is None:
        st.error("No se pudo cargar el grafo")
        st.stop()

    # Sidebar para selección de query
    with st.sidebar:
        # Selector con slider (compacto y elegante)
        st.markdown("#### Selecciona una Query")
        
        # Botones en una sola columna
        if st.button("Query 1", use_container_width=True, type="primary" if st.session_state.query_num == 1 else "secondary"):
            st.session_state.query_num = 1
        if st.button("Query 2", use_container_width=True, type="primary" if st.session_state.query_num == 2 else "secondary"):
            st.session_state.query_num = 2
        if st.button("Query 3", use_container_width=True, type="primary" if st.session_state.query_num == 3 else "secondary"):
            st.session_state.query_num = 3
        if st.button("Query 4", use_container_width=True, type="primary" if st.session_state.query_num == 4 else "secondary"):
            st.session_state.query_num = 4
        if st.button("Query 5", use_container_width=True, type="primary" if st.session_state.query_num == 5 else "secondary"):
            st.session_state.query_num = 5
        if st.button("Query 6", use_container_width=True, type="primary" if st.session_state.query_num == 6 else "secondary"):
            st.session_state.query_num = 6
        if st.button("Query 7", use_container_width=True, type="primary" if st.session_state.query_num == 7 else "secondary"):
            st.session_state.query_num = 7
        if st.button("Query 8", use_container_width=True, type="primary" if st.session_state.query_num == 8 else "secondary"):
            st.session_state.query_num = 8

        
        query_num = st.session_state.query_num
        
        # Mostrar info de la query seleccionada
        st.info(f"**{QUERIES[query_num]['nombre']}**") 

    # Contenido principal
    st.markdown(f"## Query {query_num}: {QUERIES[query_num]['nombre']}")

    # Determinar tipo de query
    query_config = QUERIES[query_num]
    es_combinada = query_config.get("tipo") == "combinada"

    if es_combinada:
        st.info("Esta es una query combinada: primero consulta el RDF local, luego enriquece con datos de Wikidata")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Query RDF")
            st.code(query_config["query_rdf"],
                    language="sparql", line_numbers=True)
        with col2:
            st.markdown("#### Query Wikidata")
            st.code(query_config["query_wikidata"],
                    language="sparql", line_numbers=True)
    else:
        with st.container():
            st.code(query_config["query"],
                    language="sparql", line_numbers=True)


    # Botones de acción
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        ejecutar = st.button("Ejecutar Query", width="stretch", type="primary")

    # Solo ejecutar si se presiona el botón
    if ejecutar:
        st.session_state.query_ejecutada = query_num

        if es_combinada:
            # Ejecutar query combinada usando la función centralizada
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.info(
                "Ejecutando query encadenada: RDF local → Wikidata")
            progress_bar.progress(20)

            # Llamar a la función centralizada
            df_rdf, df_combined, error_msg, batch_info = execute_combined_query(
                g,
                query_config.get("query_rdf", ""),
                query_config.get("query_wikidata", ""),
                query_config.get("input_var", "titulo")
            )

            progress_bar.progress(90)

            # Guardar resultados
            st.session_state.resultados = df_rdf if df_rdf is not None and not df_rdf.empty else None
            st.session_state.resultados_combinados = df_combined if df_combined is not None and not df_combined.empty else df_rdf
            st.session_state.batch_info = batch_info  # Guardar info de batches

            # Mostrar resultado
            if error_msg:
                status_text.warning(f"⚠️ {error_msg}")
            else:
                # Calcular cuántas filas tienen datos de Wikidata
                if df_combined is not None and not df_combined.empty:
                    wd_cols = [
                        col for col in df_combined.columns if col.startswith('wd_')]
                    if wd_cols:
                        matches = df_combined[wd_cols].notna().any(
                            axis=1).sum()
                        batches_msg = f", {len(batch_info)} batches ejecutados" if batch_info else ""
                        status_text.success(
                            f"Query completada: {len(df_rdf)} filas RDF, {matches} enriquecidas con Wikidata{batches_msg}")
                    else:
                        status_text.success(
                            f"Query RDF completada: {len(df_rdf)} resultados")
                else:
                    status_text.success(
                        f"Query RDF completada: {len(df_rdf)} resultados")

            progress_bar.progress(100)
        else:
            # Ejecutar query simple
            with st.spinner("Ejecutando consulta SPARQL..."):
                df, error = execute_query(g, query_config["query"])

            if error:
                st.error(f"Error al ejecutar la query: {error}")
                st.session_state.resultados = None
                st.session_state.resultados_combinados = None
            elif df.empty:
                st.warning("La consulta no devolvió resultados")
                st.session_state.resultados = None
                st.session_state.resultados_combinados = None
            else:
                st.session_state.resultados = df
                st.session_state.resultados_combinados = None

    # Mostrar resultados solo si existen
    if st.session_state.resultados is not None and st.session_state.query_ejecutada == query_num:
        df = st.session_state.resultados

        st.markdown("---")

        # PRIMERA TABLA: Datos RDF Local
        st.markdown("## Resultados RDF Local")

        # Mostrar métricas RDF
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
                <div class='metric-card'>
                    <h2 style='margin: 0; font-size: 2.5em;'>{len(df)}</h2>
                    <p style='margin: 5px 0 0 0; font-size: 1.1em;'>Filas</p>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div class='metric-card'>
                    <h2 style='margin: 0; font-size: 2.5em;'>{len(df.columns)}</h2>
                    <p style='margin: 5px 0 0 0; font-size: 1.1em;'>Columnas</p>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                <div class='metric-card'>
                    <h2 style='margin: 0; font-size: 2.5em;'>RDF</h2>
                    <p style='margin: 5px 0 0 0; font-size: 1.1em;'>Local</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Opciones de visualización RDF
        view_option = st.radio(
            "",
            ["Tabla Interactiva", "JSON", "Datos Raw"],
            horizontal=True,
            key="view_rdf"
        )

        if view_option == "Tabla Interactiva":
            st.dataframe(
                df,
                width="stretch",
                height=min(500, (len(df) + 1) * 35 + 3)
            )
        elif view_option == "JSON":
            st.json(df.to_dict(orient='records'))
        else:
            st.text(df.to_string())

        # Botones de exportación RDF
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥   Descargar CSV",
                data=csv,
                file_name=f"query_{query_num}_rdf_{QUERIES[query_num]['nombre'].replace(' ', '_')}.csv",
                mime="text/csv",
                width="stretch"
            )

        with col2:
            json_str = df.to_json(orient='records', indent=2)
            st.download_button(
                label="📥 Descargar JSON",
                data=json_str,
                file_name=f"query_{query_num}_rdf_{QUERIES[query_num]['nombre'].replace(' ', '_')}.json",
                mime="application/json",
                width="stretch"
            )

        # SEGUNDA TABLA: Datos Combinados (solo para queries combinadas)
        if es_combinada and st.session_state.resultados_combinados is not None:
            df_combined = st.session_state.resultados_combinados

            st.markdown("---")
            st.markdown("## Resultados Combinados (RDF + Wikidata)")

            # Identificar columnas de Wikidata (las que empiezan con 'wd_')
            wd_cols = [
                col for col in df_combined.columns if col.startswith('wd_')]

            if wd_cols:
                st.info(
                    f"Datos RDF enriquecidos con **{len(wd_cols)}** campos adicionales de Wikidata: {', '.join(wd_cols)}")

            # Mostrar métricas combinadas
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                    <div class='metric-card'>
                        <h2 style='margin: 0; font-size: 2.5em;'>{len(df_combined)}</h2>
                        <p style='margin: 5px 0 0 0; font-size: 1.1em;'>Filas</p>
                    </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                    <div class='metric-card'>
                        <h2 style='margin: 0; font-size: 2.5em;'>{len(df_combined.columns)}</h2>
                        <p style='margin: 5px 0 0 0; font-size: 1.1em;'>Columnas</p>
                    </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                    <div class='metric-card'>
                        <h2 style='margin: 0; font-size: 2.5em;'>RDF+WD</h2>
                        <p style='margin: 5px 0 0 0; font-size: 1.1em;'>Combinado</p>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Opciones de visualización Combinados
            view_option_combined = st.radio(
                "",
                ["Tabla Interactiva", "JSON", "Datos Raw"],
                horizontal=True,
                key="view_combined"
            )

            if view_option_combined == "Tabla Interactiva":
                st.dataframe(
                    df_combined,
                    width="stretch",
                    height=min(500, (len(df_combined) + 1) * 35 + 3)
                )
            elif view_option_combined == "JSON":
                st.json(df_combined.to_dict(orient='records'))
            else:
                st.text(df_combined.to_string())

            # Botones de exportación Combinados
            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                csv_combined = df_combined.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv_combined,
                    file_name=f"query_{query_num}_combinado_{QUERIES[query_num]['nombre'].replace(' ', '_')}.csv",
                    mime="text/csv",
                    width="stretch"
                )

            with col2:
                json_str_combined = df_combined.to_json(
                    orient='records', indent=2)
                st.download_button(
                    label="📥 Descargar JSON",
                    data=json_str_combined,
                    file_name=f"query_{query_num}_combinado_{QUERIES[query_num]['nombre'].replace(' ', '_')}.json",
                    mime="application/json",
                    width="stretch"
                )


if __name__ == "__main__":
    main()
