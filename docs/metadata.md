# Metadata Plane (OpenMetadata)

OpenMetadata serves as the central metadata control plane for this demonstrator.

## Technical Metadata

The physical tables created in Iceberg (`bronze`, `silver`, `gold`) are ingested automatically via the OpenMetadata Ingestion framework (running in the `openmetadata-ingestion` container). 
The `trino_ingestion.yaml` pipeline connects to the local Trino instance to extract schema definitions, column types, and descriptions.

## Business Glossary

A dedicated **Engineering Delivery Glossary** is created via the OpenMetadata REST API.
It includes domains such as Organization, Delivery, Engineering, People, and Data Governance.
The hero term, **Rework Rate**, is explicitly documented and linked to the physical column `gold_employee_delivery.rework_rate`.

## Lineage

Lineage is injected explicitly to demonstrate provenance:
- **Jira Issue History** -> **Silver Work Item** -> **Gold Employee Delivery** -> **Qlik Sense**.
This allows the consumer to trace the "Rework Rate" metric directly back to the physical source table.
