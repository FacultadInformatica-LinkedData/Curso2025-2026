# 🌿 BeSafe – Linked Data Web App  
### *Aplicación web para consultar nuestro RDF mediante SPARQL*  
**Grupo 10 – Semantic Web – UPM**

---

## 📌 1. ¿Qué es BeSafe?

**BeSafe** es una aplicación web sencilla (en **Streamlit**) que permite:

- Cargar el **RDF generado con RML/OpenRefine**
- Ejecutar **consultas SPARQL** sobre los datos
- Mostrar resultados en una interfaz clara
- Demostrar el uso de **Linked Data**, incluyendo enlaces `owl:sameAs` a Wikidata/DBpedia
- Servir como demo funcional en la **presentación final**

La aplicación funciona **100% en local**.

---

## 📂 2. Estructura del Proyecto

```text
BeSafe-Linked-Data/
│
├── data/
│ ├── alertas-with-links.ttl ← RDF REAL que usa la app
│ └── besafe-ontology.ttl ← ontología (documentación)
│
├── docs/
│ └── … ← mockups, requisitos, documentación
│
├── src/
│ ├── queries/
│ │ ├── internal.py ← consultas SPARQL al RDF local
│ │ └── wikidata.py ← consultas externas (opcional)
│ │
│ ├── utils/
│ │ ├── rdf_loader.py ← carga del grafo RDF con rdflib
│ │ └── alerts.py ← reglas de semáforo (opcional)
│ │
│ └── main.py ← pruebas desde terminal
│
├── streamlit_app/
│ └── Home.py ← interfaz web principal
│
├── requirements.txt ← dependencias
└── README.md ← este documento
```
---


## 🧪 3. Cómo ejecutar la aplicación

1. Instalar dependencias - ejecutar en terminal del proyecto raíz: **pip install -r requirements.txt**
2. Ejecutar Streamlit: **streamlit run streamlit_app/Home.py**
3. Se abrirá en el navegador



