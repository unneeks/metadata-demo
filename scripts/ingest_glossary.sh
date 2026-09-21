#!/bin/bash
echo "Ingesting Business Glossary into OpenMetadata..."
# For a fully automated script, this calls a python script inside the ingestion container 
# using the OpenMetadata Python SDK to create glossary terms and link them.
docker-compose exec -T openmetadata-ingestion python /scripts/create_glossary.py
echo "Glossary ingestion complete."
