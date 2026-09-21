#!/bin/bash
echo "Ingesting Trino/Iceberg metadata..."
docker-compose exec -T openmetadata-ingestion metadata ingest -c /openmetadata/config/trino_ingestion.yaml
echo "Metadata ingestion complete."
