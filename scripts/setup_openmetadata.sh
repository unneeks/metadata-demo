#!/bin/bash
echo "Waiting for OpenMetadata to be healthy..."
while ! curl -s http://localhost:8585/api/v1/system/version > /dev/null; do
    echo "Waiting for OM server..."
    sleep 5
done

echo "OpenMetadata is up! Bootstrapping configuration..."
# In a real environment, you'd use the admin login to generate a JWT token.
# For demo purposes, we will just echo instructions or use a pre-provisioned bot token if configured.
echo "Run metadata ingestion using docker-compose exec openmetadata-ingestion ..."
