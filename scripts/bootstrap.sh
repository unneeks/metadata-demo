#!/bin/bash
echo "Bootstrapping OpenMetadata Demonstration Environment..."

echo "1. Starting Docker Services..."
docker-compose up -d

echo "2. Waiting for OpenMetadata Server to become healthy..."
while ! curl -s http://localhost:8585/api/v1/system/version > /dev/null; do
    echo "Waiting for OpenMetadata Server (http://localhost:8585)... this may take a few minutes."
    sleep 10
done
echo "OpenMetadata is up!"

echo "3. Initializing Database and Search Indices..."
echo -e "DELETE\n" | docker compose run --rm -T -e DB_USER=openmetadata_user -e DB_USER_PASSWORD=openmetadata_password --entrypoint /bin/bash openmetadata-server -c "/opt/openmetadata/bootstrap/openmetadata-ops.sh drop-create"
docker compose restart openmetadata-server

echo "4. Waiting for OpenMetadata Server to restart..."
sleep 10
while ! curl -s http://localhost:8585/api/v1/system/version > /dev/null; do
    echo "Waiting for OpenMetadata Server (http://localhost:8585)... this may take a few minutes."
    sleep 10
done
echo "OpenMetadata restarted successfully!"

echo "5. Bootstrapping Metadata Entities..."
python3 scripts/bootstrap_metadata.py

echo "6. Harvesting Lineage and Executing Data Quality..."
bash scripts/run_harvest_and_dq.sh

echo "Bootstrap complete! You can now navigate to http://localhost:8585"
