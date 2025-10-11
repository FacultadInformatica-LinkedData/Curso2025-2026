# Hands-on assignment 1 – Self assessment

## Checklist

**The “dataset” directory:**

Contains the original CSV file

Contains the cleaned CSV file processed with OpenRefine

Contains the JSON file with the refinement history

**The "cleaning" process:**

Applied text transformation to convert all values to uppercase in columns V01-V24

Used OpenRefine operations documented in the JSON history file

Maintained data structure while standardizing text values

Technical details of the data processing
Original dataset: calair-tiemporeal.-updated.csv

Domain: Air quality/environmental monitoring data

Structure: Time-series data with hourly measurements (H01-H24) and validation flags (V01-V24)

Geographic scope: Municipalities in province 28 (likely Madrid, Spain)

**Data cleaning performed:**

Standardized validation flags (V01-V24 columns) to uppercase using value.toUppercase()

Applied consistent text transformation across all validation columns

Maintained error handling with "keep-original" strategy


**Files processed:**

✅ calair-tiemporeal.-updated.csv (original data)

✅ history.json (OpenRefine transformation history)

✅ Cleaned CSV file (result of applying JSON operations)


**Data quality improvements**

The text transformation ensures consistent validation flag values ("V" and "N" in uppercase), which improves data reliability for automated processing and analysis.


**Comments on the self-assessment**
The data processing successfully standardized the validation flags across all measurement columns while preserving the original data structure and numeric values. The OpenRefine operations were systematically applied and documented in the JSON history file.