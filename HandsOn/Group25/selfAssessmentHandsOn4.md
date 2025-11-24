# Self-Assesment Hands-On 4: Transformación de CSV a RDF con RML

**Grupo:** Group25
**Dataset:** Accidentes producidos en la comunidad de Madrid  

## Antes de comenzar
Hemos leído las especificaciones de RML , YARRML y cómo funciona las transformación a RDF.
Se ha descargado Python, definido un entorno virtual y también hemos descargado Morph-KGC

## Dataset y depuración
Hemos utilizado OpenRefine para hacer las siguientes operaciones:
 - Eliminación de double slash ("//")
 - Eliminación de barra invertida ("\")
 - Corrección del formato time de la columna de hora de nuestro dataset
## Proceso de definición de mapeos RML
Para la transformación, definimos mapeos RML siguiendo la estructura típica:
- Logical Source: definición de la fuente de datos CSV.
- Triples Map: mapeo de sujetos RDF a partir de filas.
- Subject Map y Predicate Object Map: para asignar URIs, propiedades y valores.

Hemos creado archivos mapping RML y YAML

## Retos encontrados
Nos enfrentamos a la gestión de valores complejos en columnas y la normalización de URIs para mantener la coherencia del dataset RDF. Ajustamos los mapeos para superar estas dificultades y asegurar resultados precisos.

## Verificación mediante SPARQL
Creamos consultas SPARQL específicas para validar que la transformación cumpliera con los criterios de correspondencia entre CSV y RDF, verificando integridad y completitud de los datos.

## Reflexión y aprendizaje
Esta experiencia nos permitió comprender la potencia y flexibilidad de RML para la transformación de datos heterogéneos. A futuro, se considera ampliar la cobertura semántica e integrar fuentes múltiples para enriquecer los datasets RDF generados.
