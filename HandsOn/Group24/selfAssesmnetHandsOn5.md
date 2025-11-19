# Hands-On 5 — Self-Assessment and Technical Report

## 1. Overview

In this hands-on, the goal was to practice the process of linking RDF data with external datasets and validating the resulting RDF through mappings and SPARQL queries.  
The work was performed using the datasets selected in previous assignments:

1. Urban trees and green zones in Madrid (Arbolado en zonas verdes, distritos y calles).  
2. Atmospheric pollution (NO₂ average levels in Spain).  
3. Environmental protection expenditure by enterprises (Spain).

The linking and RDF generation were done using OpenRefine for reconciliation and RMLMapper for transformation into RDF.  

---

## 2. Achievements

### Successful tasks

- Dataset preparation:  
  All datasets were previously cleaned and normalized using OpenRefine (Hands-On 3). Columns were standardized (no spaces, consistent encoding, correct CSV structure).

- RDF transformation for the tree dataset:  
  The Arbolado Madrid dataset was successfully mapped using a custom RML file.  
  The mapping generated valid RDF triples, and the corresponding `.ttl` output was produced without errors.  
  Each tree instance was represented as a resource with attributes such as species, district, and location.  

- Linking logic applied:  
  The column "District" in the tree dataset was linked conceptually to Wikidata entities representing Madrid districts, preparing the data for semantic enrichment.  
  Example: linking "Chamberí" → `<https://www.wikidata.org/entity/Q1027178>`.

- SPARQL testing:  
  Queries were prepared to check the resulting RDF data, confirming the correct structure and relationships for the Arbolado dataset.

---

## 3. Issues and Challenges

### 1. RMLMapper errors and file format issues

Several errors occurred during the RDF generation process for the NO₂ and Expenditure datasets.  
The main causes were:

- Encoding issues (UTF-8 BOM):  
  The RMLMapper parser rejected the `.rml` files with the message  
  `Expected ':' found '/' [line 1]`.  
  This happened because Windows editors (like Notepad or VSCode) saved the files with BOM encoding, which RMLMapper could not interpret correctly.

- Invisible characters or incorrect IRIs:  
  The parser also threw  
  `Not a valid (absolute) IRI: #MappingName`,  
  caused by relative IRIs not wrapped in `< >`.

- File path mismatches:  
  Some CSV paths inside the `.rml` did not match the actual file names (for example, `valor-medio-de-contaminacion-atmosferica-no2-with-links.csv`), resulting in  
  `FileNotFoundException`.  
  Once corrected, RMLMapper executed successfully but generated no output because of column mismatches.

---

### 2. Column mismatch and missing mappings

For the NO₂ dataset:
- The CSV header used column names like `No2_value` instead of `Concepto` or `Valor`.  
- The mapping expected different names, so RMLMapper did not find any data to transform, producing no TTL output but no explicit error.

For the Environmental Expenditure dataset:
- The mapping executed but also produced empty output, for similar reasons: inconsistent column names (`Año`, `Valor`, `Estado_dato`).

These problems could be solved by reconfiguring the RML mappings or normalizing the column headers in OpenRefine.

---

### 3. Linking limitations

Only the "Año" (Year) column could be reconciled with external data (for example, DBpedia or Wikidata year entities).  
Other potential linkable entities (like "Concepto" or "Territorio") were not suitable because:
- The datasets were national aggregates (no geographic disaggregation).  
- The concept identifiers were generic statistical labels without clear external URIs.

Therefore, the linking step was partially successful — conceptually correct but limited in actual links.

---

## 4. Lessons Learned

- RMLMapper requires clean Turtle syntax and absolutely valid IRIs.  
  Even a single unwrapped IRI or a BOM character at the beginning of a file can invalidate the whole mapping.

- Column names must exactly match between the CSV and the mapping (case-sensitive).  
  Verifying headers before running the mapping is critical.

- OpenRefine is essential for normalization and reconciliation before RDF conversion.  
  Using reconciliation services like Wikidata’s API can greatly improve the linking quality.

- Incremental testing (starting from a minimal working RML) helps detect syntax issues early.

---

## 5. Summary of Results

| Dataset | Linking Status | RDF Output | Notes |
|----------|----------------|-------------|--------|
| Urban Trees (Madrid) | Linked (Districts) | TTL generated successfully | RDF structure correct and validated |
| Atmospheric Pollution (NO₂) | Linked only by Year | No TTL output | Column mismatch and mapping issues |
| Environmental Expenditure (Spain) | Linked only by Year | No TTL output | Mapping executed but no triples produced |

---

## 6. Next Steps

- Re-test the NO₂ and Expenditure mappings after aligning the CSV headers and removing UTF-8 BOM characters.  
- Enrich the Madrid tree dataset with more external links (species, coordinates, etc.).  
- Validate RDF output using SHACL or SPARQL consistency checks.

---

## 7. Self-Assessment

| Criteria | Evaluation | Comments |
|-----------|-------------|-----------|
| Data analysis and cleaning | Completed | Datasets prepared in OpenRefine |
| Linking identification | Partial | Limited to Year field and conceptual district matching |
| RML mapping creation | Partial | Fully functional for tree dataset, partial for others |
| RDF transformation | Partial | Success for tree dataset only |
| SPARQL testing | Completed | Queries successfully executed for tree RDF |
| Reflection and documentation | Completed | Clear description of issues and solutions |

---

### Final remark

The linking process demonstrated the complexity of achieving semantic interoperability between heterogeneous datasets.  
Despite partial linking success, the group achieved a working RDF pipeline for one complete dataset and learned valuable lessons about encoding, mapping validation, and reconciliation techniques.
