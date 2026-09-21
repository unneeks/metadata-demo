#!/bin/bash
echo "Bootstrapping OpenMetadata Demonstration Environment..."

echo "1. Starting Docker Services..."
docker-compose up -d

echo "2. Waiting for Services to become healthy..."
# A simple wait loop for OpenMetadata Server
while ! curl -s http://localhost:8585/api/v1/system/version > /dev/null; do
    echo "Waiting for OpenMetadata Server (http://localhost:8585)... this may take a few minutes."
    sleep 10
done
echo "OpenMetadata is up!"

echo "3. Executing Metadata Ingestion..."
bash scripts/setup_openmetadata.sh
bash scripts/ingest_metadata.sh
bash scripts/ingest_glossary.sh
bash scripts/ingest_lineage.sh

echo "Bootstrap complete! You can now navigate to http://localhost:8585"
