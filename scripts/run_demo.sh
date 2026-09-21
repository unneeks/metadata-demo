#!/bin/bash
echo "=== Employee Delivery Data Product Demonstration ==="

echo "1. Ensuring all services are up..."
docker-compose ps

echo "2. Check Qlik Sense Extracts..."
ls -l qlik/

echo "3. Opening OpenMetadata..."
echo "Please navigate to http://localhost:8585"
echo "Login with admin/admin if prompted."

echo "4. Demo Flow:"
echo "  - Search for 'Rework Rate' in the Glossary."
echo "  - Navigate to the associated column in gold_employee_delivery."
echo "  - Click on the 'Lineage' tab to trace back to Jira."
echo "  - Click on the 'Data Quality' tab to see Great Expectations results."
