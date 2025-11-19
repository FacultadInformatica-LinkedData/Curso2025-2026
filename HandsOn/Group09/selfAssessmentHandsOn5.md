# Hands-on Assignment 5 – Self Assessment

## Checklist

**Data linking:**

- [x] Identified which classes/entities in our dataset can be linked to external datasets.
- [x] Selected relevant external datasets (e.g., Wikidata, DBpedia, etc.).
- [x] Configured OpenRefine reconciliation services (via Wikidata or custom endpoint).
- [x] Reconciled entities and matched instances with external identifiers (IRIs from external datasets).
- [x] Reviewed and validated the reconciliation matches manually.
- [x] Exported the OpenRefine history operations file (`openrefine/*-with-links.json`).
- [x] Exported the updated dataset (`csv/*-with-links.csv`).

**RML mappings (updated):**

- [x] Updated the previous RML mapping file to include links to external datasets.
- [x] Ensured subject maps now include IRIs pointing to reconciled external resources when available.
- [x] Mapped `owl:sameAs` or other linking predicates where appropriate.
- [x] Verified that all classes and properties are still correctly aligned with the ontology.
- [x] Saved the updated mappings file (`mappings/*-with-links.rml`).

**RDF transformation:**

- [x] Executed the updated RML mappings using RMLMapper.
- [x] Generated RDF output in N-Triples or Turtle format (`rdf/*-with-links.ttl`).
- [x] Checked that links to external datasets are present in the RDF.
- [x] Validated that the RDF structure remains consistent.

**Queries:**

- [x] Created a SPARQL file with queries testing the linked data (`rdf/queries-with-links.sparql`).
- [x] Verified that linked entities are accessible (e.g., `?resource owl:sameAs ?externalResource`).
- [x] Ran analytics or integrity queries to confirm correct linking.

**Deliverables (all uploaded to GitHub):**

- [x] JSON OpenRefine operations: `openrefine/*-with-links.json`
- [x] Updated dataset CSV: `csv/*-with-links.csv`
- [x] Updated RML file: `mappings/*-with-links.rml`
- [x] RDF file with links: `rdf/*-with-links.ttl`
- [x] SPARQL queries file: `rdf/queries-with-links.sparql`
- [x] Self-assessment (this file): `selfAssessmentHandsOn5.md` in root directory