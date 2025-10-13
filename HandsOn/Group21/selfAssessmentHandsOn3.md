# Hands-on assignment 3 – Self-assessment

## Checklist

**The “openrefine” directory:**
- [✔️] Contains three JSON files with all the cleaning and transformation operations:
  - `history_Accidentalidad.json`
  - `history_radares.json`
  - `history_poblacion.json`
- [✔️] The operations include trimming spaces, converting text to title case, normalizing accented characters, converting text to numbers or dates, and removing duplicates.
- [✔️] All transformations can be reproduced in OpenRefine to obtain the same cleaned datasets.

**The “csv” directory:**
- [✔️] Contains the updated and cleaned CSV files:
  - `2025-Accidentalidad-update.csv`
  - `RADARES-FIJOS-vDTT-update.csv`
  - `poblacion-1-enero-update.csv`
- [✔️] All files come from official open data of the **Madrid City Council (Datos Abiertos Madrid)**.
- [✔️] Duplicated rows and inconsistent formats were fixed.
- [✔️] Text columns such as `distrito`, `sexo`, and `tipo_accidente` were standardized.
- [✔️] Dates were converted to consistent formats (ISO or `dd/MM/yyyy`).
- [✔️] Numeric columns were converted from text when needed.

**The “selfAssessmentHandsOn3.md” file:**
- [✔️] Describes the cleaning and transformation process performed in OpenRefine.
- [✔️] Mentions that all datasets are now ready for RDF generation.
- [✔️] Confirms that all deliverables (JSON + CSV + MD) are included.

## Comments on the self-assessment
We worked with three open datasets from the Madrid City Council portal:  
- Traffic accidents (2025)  
- Fixed speed cameras (Radares fijos DGT)  
- Population by district (1 January)  

All datasets were cleaned and standardized using OpenRefine.  
Operations included removing duplicates, fixing text inconsistencies, normalizing names, converting data types, and ensuring coherence among datasets for future RDF linkage.
