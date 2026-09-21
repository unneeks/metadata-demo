#!/bin/bash

echo "Starting Harvest and DQ Process..."
# Use python3 and the OM_URL configured for the local environment
# For docker-compose, this runs against localhost:8585
export OM_URL="http://localhost:8585/api/v1"
python3 scripts/harvest_and_dq.py
echo "Done!"
