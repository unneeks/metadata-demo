# Ab Initio Metadata Hub Harvesting

This platform generates deterministic metadata outputs in the `metadata/` directory specifically formatted to map into Ab Initio Metadata Hub ingestion processes.

## Supported Metadata Elements
1. **Business Metadata**: `metadata/glossary/glossary.csv` contains terms, definitions, and stewardship information.
2. **Technical Metadata**: `metadata/technical/columns.csv` provides schema configurations and maps logical data elements to physical columns.
3. **Lineage**: `metadata/lineage/lineage.csv` provides source-to-target explicit transformations.
4. **Data Quality**: `metadata/dq/dq_results.csv` outputs run-level quality validations.

## Integration Points
- Configure Ab Initio Metadata Hub's flat-file connectors to ingest these generated CSVs directly.
- The `generate_metadata.py` Spark job orchestrates these exports during the Airflow pipeline execution.
