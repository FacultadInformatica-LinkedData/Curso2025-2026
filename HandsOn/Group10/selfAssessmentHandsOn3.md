Every resource described in the CSV file:
- [V] Has a unique identifier in a column (not an auto-increased integer)
- [V] Is related to a class in the ontology

Every class in the ontology:
- [V] Is related to a resource described in the CSV file

Every column in the CSV file:
- [V] Is trimmed
- [V] Is properly encoded (e.g., dates, booleans)
- [V] Is related to a property in the ontology

Every property in the ontology:
- [V] Is related to a column in the CSV file