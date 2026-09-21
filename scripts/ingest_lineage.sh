#!/bin/bash
echo "Ingesting Lineage into OpenMetadata..."
docker-compose exec -T openmetadata-ingestion python /scripts/create_lineage.py
echo "Lineage ingestion complete."
