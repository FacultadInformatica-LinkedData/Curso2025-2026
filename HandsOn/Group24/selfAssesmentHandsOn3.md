 Hands-On 3 — Self-Assessment

## Group: 24
---

## Task summary
In this third hands-on exercise, we worked with **OpenRefine** to clean, normalize, and prepare our selected CSV datasets for RDF transformation.  
We imported the three datasets used in previous assignments:

1. **Urban Tree Inventory — Green Areas, Districts of Madrid (2024)**  
2. **Environmental Protection Expenditure — Total Industry (Spain)**  
3. **Average Atmospheric Pollution — NO₂ (Spain)**  

Each dataset was cleaned to ensure data consistency, improve interoperability, and facilitate the conversion to RDF.

---

## Main cleaning and transformation steps

### Dataset 1: Urban Tree Inventory (Madrid)
- Removed empty rows and unused columns.  
- Trimmed whitespace and standardized capitalization (e.g., district names to Title Case).  
- Clustered and merged similar species names using the *Key collision* method.  
- Renamed columns to use consistent and machine-friendly labels (`Nº_Unidades 2024` → `Num_Unidades_2024`).  
- Converted numeric columns to the proper data type.  

**Files generated:**
- `csv/arbolado-zonas-verdes-madrid-updated.csv`  
- `openrefine/arbolado-zonas-verdes-madrid-operations.json`

---

### Dataset 2: Environmental Protection Expenditure (Spain)
- Removed blank rows.  
- Converted “Valor” and “Año” columns to numeric values.  
- Renamed columns to standardized English equivalents (`Concepto` → `Concept`, `Valor` → `Value`).  
- Ensured all years follow a valid range (2008–2023).  

**Files generated:**
- `csv/gasto-de-las-empresas-en-proteccion-ambiental-total-industria-updated.csv`  
- `openrefine/gasto-de-las-empresas-en-proteccion-ambiental-total-industria-operations.json`

---

### Dataset 3: Average Atmospheric Pollution — NO₂
- Removed rows with missing or invalid values.  
- Renamed columns for RDF compatibility (`Año` → `Year`, `Valor` → `Value`, `Territorio` → `Territory`).  
- Converted “Year” and “Value” columns to numeric data types.  
- Checked and unified units (µg/m³).  

**Files generated:**
- `csv/valor-medio-de-contaminacion-atmosferica-dioxido-de-nitrogeno-no2-updated.csv`  
- `openrefine/valor-medio-de-contaminacion-atmosferica-dioxido-de-nitrogeno-no2-operations.json`

---

## Tools and reasoning
- **OpenRefine** was used because it allows a reproducible, structured workflow for cleaning and transforming tabular data.  
- Each transformation was exported as a JSON history file to ensure transparency and reproducibility.  
- Column normalization and data-type consistency are crucial before generating RDF graphs, as they minimize parsing and linking errors.

---

## Reflections
- The *clustering* and *facet* features in OpenRefine were particularly useful to detect inconsistencies.  
- Many datasets contained small formatting issues (extra spaces, mixed capitalization) that could break URI generation.  
- Cleaning data before RDF conversion ensures smoother linking with external datasets like GeoNames or Wikidata.

---

## Next steps
- Use the cleaned datasets to generate RDF according to the ontology defined in Hands-On 2.  
- Validate the RDF with SHACL or other quality tools.  
- Explore linking tree data and air quality by district for the application development phase.

---

**Final note:**  
All updated CSVs and JSON operation files are available in the group repository under `/csv` and `/openrefine` respectively.
