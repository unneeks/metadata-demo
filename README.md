# Employee Delivery Data Product Demonstrator

This is a fully executable synthetic enterprise data platform demonstrator based on a metadata-centric Data Fabric architecture.

## Overview
It demonstrates how a business metric ("Rework Rate") in a Qlik Sense dashboard can be traced back through:
1. **Meaning** (Glossary)
2. **Context** (Ontology)
3. **Provenance** (Lineage)
4. **Trust** (Data Quality)

## Prerequisites
- Docker & Docker Compose
- Python 3.9+
- `make`

## Installation & Execution

1. **Setup Environment**:
   ```bash
   make setup
   ```
2. **Generate Synthetic Data**:
   ```bash
   make generate
   ```
   *This generates deterministic data based on seed 42 into `src/`.*
3. **Start Platform**:
   ```bash
   make start
   ```
4. **Stop Platform**:
   ```bash
   make stop
   ```
5. **Clean Data**:
   ```bash
   make clean
   ```

## Architecture
See `docs/architecture.md` for a full breakdown.
