# Self-assessment HO5 — Data Linking

**Grupo:** Group12  
**Miembro:** Fernando Delgado Merino (@fernan9976)  
**Dataset:** Inventario de zonas verdes del Ayuntamiento de Madrid (2024)  
**Fecha:** 26/10/2025  
**Profesor:** Daniel Garijo

---

## 1. Objetivo del Hands-on 5

El objetivo de este hands-on ha sido **enlazar** nuestro dataset RDF con recursos externos y actualizar el pipeline de generación de RDF para reflejar esos enlaces.

Esto incluye:
- Detectar qué entidades de nuestro modelo pueden vincularse con entidades ya existentes en la web de datos.
- Incorporar esos enlaces a nuestros datos limpios.
- Ajustar los mapeos RML.
- Regenerar el RDF con los enlaces.
- Escribir consultas SPARQL para verificar que el enlazado es correcto.

Esta práctica sigue el principio de los datos enlazados de 5★ propuesto por Tim Berners-Lee: publicar datos en formato abierto, con URIs estables, en RDF, y enlazarlos con otros datasets abiertos como Wikidata. :contentReference[oaicite:2]{index=2}

---

## 2. Identificación de entidades enlazables

Analizamos las clases de nuestra ontología y determinamos que:
- Cada zona verde (`gz:GreenZone`) tiene un campo `Distrito` (por ejemplo, "CENTRO").
- El distrito es una entidad administrativa oficial del Ayuntamiento de Madrid.  
- Es posible representarlo como un recurso propio (`gz:District`) y **enlazarlo con Wikidata**, donde ese distrito ya existe como entidad con identificador `Q1763376` para el distrito Centro de Madrid (definido en Wikidata como el primer distrito administrativo de la ciudad de Madrid). :contentReference[oaicite:3]{index=3}

Decisión:  
- Creamos URIs locales para cada distrito, por ejemplo:  
  `http://linkeddata.greenzonesmadrid.org/resource/district/CENTRO`
- Añadimos también una referencia externa (`owl:sameAs`) al recurso Wikidata:  
  `https://www.wikidata.org/entity/Q1763376`

Esto es exactamente el tipo de “linking a dataset externo” que pide la práctica.

---

## 3. Enriquecimiento del CSV (reconciliación)

Partimos del CSV ya limpio en HO4. Para HO5 hicimos:

- Añadimos la columna `DistrictURI` con la URI interna del distrito.
- Añadimos la columna `DistrictWikidata` con el identificador reconciliado en Wikidata.
- Mantenemos `ZoneURI` como identificador único de cada zona verde.

El resultado se guarda como:

- `csv/zonas-verdes-with-links.csv`

Ejemplo de columnas finales:
- `ZoneURI`
- `DistrictURI`
- `DistrictWikidata`
- `Distrito`
- `Subepígrafe`
- `Apartado`
- `FileNumber`
- `PropertyNature`
- `SituationTarget`
- `Destination`
- `Plot`

Este CSV actualizado es el que usamos de entrada para el nuevo mapeo RML.

Además se documentó el proceso en:
- `openrefine/operations-with-links.json`

Este fichero recoge las operaciones de OpenRefine: limpieza, normalización de valores, generación de URIs y asignación de IDs externos (Wikidata). Eso demuestra la parte de “Define Open Refine reconciliation services if needed / Reconcile data with the identified datasets”.

---

## 4. Actualización de la ontología

Se actualizó la ontología `gz-ontology.ttl` para incluir:
- La clase `gz:District`.
- La propiedad objeto `gz:inDistrict` (dominio `gz:GreenZone`, rango `gz:District`).

También se mantuvieron las propiedades de datos (`gz:district`, `gz:fileNumber`, `gz:plot`, etc.) definidas en HO4.

Esto permite modelar:
1. La zona verde como recurso.
2. Su distrito como recurso.
3. El enlace entre ambos recursos dentro de nuestro grafo.
4. El enlace de ese distrito local con Wikidata mediante `owl:sameAs`.

---

## 5. Actualización del mapeo RML

Creamos el archivo:
- `mappings/greenzones-with-links.rml`

Cambios clave frente a la versión anterior (`greenzones.rml`):
1. Definimos un `TriplesMap` para `gz:GreenZone`:
   - El sujeto de cada zona verde es `ZoneURI`.
   - Se generan todas las propiedades literales (`gz:fileNumber`, `gz:destination`, etc.).
   - Se añade la propiedad `gz:inDistrict` apuntando a `DistrictURI` como IRI.

2. Definimos un `TriplesMap` para `gz:District`:
   - El sujeto de cada distrito es `DistrictURI`.
   - Se declara como clase `gz:District`.
   - Se añade `rdfs:label` con el nombre del distrito.
   - Se añade `owl:sameAs https://www.wikidata.org/entity/{DistrictWikidata}` para enlazar con Wikidata.

Wikidata describe `Centro` (`Q1763376`) como el primer distrito administrativo de Madrid y lo modela como distrito urbano oficial. :contentReference[oaicite:4]{index=4}

Este paso cumple “Update the mappings and transform the data into RDF”.

---

## 6. Generación del RDF enlazado

Con el RML actualizado, generamos un nuevo grafo RDF en Turtle:

- `rdf/greenzones-with-links.ttl`

Este grafo incluye:
- Recursos de tipo `gz:GreenZone`, uno por cada fila del CSV.
- Recursos de tipo `gz:District`, uno por cada distrito.
- Para cada zona verde:
  - la relación `gz:inDistrict <.../district/CENTRO>`.
- Para cada distrito:
  - `owl:sameAs` apuntando al recurso de Wikidata (por ejemplo `https://www.wikidata.org/entity/Q1763376`).

Este `owl:sameAs` es lo que convierte nuestro grafo en **Linked Open Data de 5★**, porque:
1. Tenemos datos abiertos en formato estructurado.
2. En formato no propietario (CSV para la fuente).
3. Los publicamos como RDF con URIs.
4. Y además enlazamos nuestros URIs con URIs externos en la Web (Wikidata, que es un conjunto de datos abierto y enlazado). :contentReference[oaicite:5]{index=5}

---

## 7. Consultas SPARQL de validación

Creamos:
- `rdf/queries-with-links.sparql`

Las consultas hacen:
1. Contar cuántas `gz:GreenZone` existen.
2. Recuperar zonas verdes junto a su distrito enlazado y la etiqueta `rdfs:label` del distrito.
3. Verificar que el distrito enlazado tiene `owl:sameAs` (es decir, que realmente apunta a un recurso externo, en este caso de Wikidata).
4. Contar zonas verdes por distrito (agrupación por `gz:inDistrict`).
5. Filtrar todas las zonas del distrito CENTRO y mostrar su `gz:fileNumber` y `gz:destination`.

Estas consultas demuestran que:
- El linking está reflejado en el grafo.
- El grafo se puede navegar semánticamente.
- El enlace externo (`owl:sameAs`) está presente y utilizable.

---

## 8. Estructura final del repositorio (resumen)

El repositorio queda así:

```text
HandsOn/
└─ Group12/
   ├─ selfAssessmentHandsOn1.md
   ├─ selfAssessmentHandsOn2.md
   ├─ selfAssessmentHandsOn3.md
   ├─ selfAssessmentHandsOn4.md
   ├─ selfAssessmentHandsOn5.md
   ├─ README.md
   ├─ analysis.html
   ├─ requirements/
   │   ├─ applicationRequirements.html
   │   └─ datasetRequirements.html
   ├─ ontology/
   │   └─ gz-ontology.ttl
   ├─ openrefine/
   │   ├─ operations.json
   │   └─ operations-with-links.json
   ├─ csv/
   │   ├─ zonas-verdes-updated.csv
   │   └─ zonas-verdes-with-links.csv
   ├─ mappings/
   │   ├─ greenzones.rml
   │   └─ greenzones-with-links.rml
   └─ rdf/
       ├─ greenzones.ttl
       ├─ greenzones-with-links.ttl
       ├─ queries.sparql
       └─ queries-with-links.sparql
