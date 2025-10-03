# Self-assessment — Hands-on 1

**Group**: GroupXX  
**Date**: 2025-10-02

## Deliverables checklist
- [x] `README.md` with members (placeholders if needed).
- [x] CSVs in `csv/` (samples included) and a script for full downloads.
- [x] `requirements/datasetRequirements.html` with the R1–R6 evaluation.
- [x] `requirements/applicationRequirements.html` with requirements and mockups.
- [x] This self-assessment document.

## Degree of compliance
- **R1–R4**: Satisfied for the three selected datasets (smart city domain, CSV, open license CC BY 4.0, linkable using geography/IDs).
- **R5** (documentation): Satisfied — dataset pages describe fields and resources.
- **R6** (multiple sources): Satisfied — three sources combined (air, traffic, Bicing).

## Decisions and rationale
- We chose **Barcelona** because Open Data BCN offers high-quality, continuous releases, with **CSV** downloads and clear **CC BY 4.0** licensing.
- The three domains (air, traffic, Bicing) complement each other for a citizen use case (“healthy route”).

## Limitations and future work
- Full CSVs are large; we version **samples** and provide a download script.
- Future: normalize segment identifiers, enrich with neighborhood/district boundaries, and deploy an RDF graph + SPARQL endpoint.
