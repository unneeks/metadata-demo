import requests
import json

OM_URL = "http://openmetadata-server:8585/api/v1"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    # "Authorization": "Bearer <YOUR_JWT_TOKEN>" # Add JWT token here if auth is enabled
}

def login():
    import base64
    payload = {
        "email": "admin@openmetadata.org",
        "password": base64.b64encode(b"admin").decode("utf-8")
    }
    r = requests.post(f"{OM_URL}/users/login", headers={"Content-Type": "application/json"}, json=payload)
    if r.status_code == 200:
        return r.json().get("accessToken")
    print("Login failed:", r.text)
    return None

def add_lineage(from_fqn, to_fqn, token):
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    # Retrieve the IDs for the from and to entities
    r_from = requests.get(f"{OM_URL}/tables/name/{from_fqn}", headers=headers)
    r_to = requests.get(f"{OM_URL}/tables/name/{to_fqn}", headers=headers)
    
    if r_from.status_code == 200 and r_to.status_code == 200:
        from_id = r_from.json().get("id")
        to_id = r_to.json().get("id")
        
        payload = {
            "edge": {
                "fromEntity": {
                    "id": from_id,
                    "type": "table"
                },
                "toEntity": {
                    "id": to_id,
                    "type": "table"
                }
            }
        }
        
        r_lineage = requests.put(f"{OM_URL}/lineage", headers=headers, json=payload)
        if r_lineage.status_code in (200, 201):
            print(f"Lineage created: {from_fqn} -> {to_fqn}")
        else:
            print(f"Error creating lineage: {r_lineage.text}")
    else:
        print(f"Could not find entities. From: {r_from.status_code}, To: {r_to.status_code}")

if __name__ == "__main__":
    token = login()
    if not token:
        print("Failed to get token, exiting.")
        exit(1)
        
    # Example lineage mapping
    # Note: FQNs depend on the ingestion service name and database/schema.
    # Assuming serviceName 'trino_iceberg', database 'iceberg', schema 'bronze'/'silver'/'gold'
    
    # Bronze to Silver Lineage Example
    add_lineage("trino_iceberg.iceberg.bronze.jira_issue_history", "trino_iceberg.iceberg.silver.silver_work_item", token)
    add_lineage("trino_iceberg.iceberg.silver.silver_work_item", "trino_iceberg.iceberg.gold.gold_employee_delivery", token)
    
    add_lineage("trino_iceberg.iceberg.bronze.servicenow_change_request", "trino_iceberg.iceberg.silver.silver_change", token)
    add_lineage("trino_iceberg.iceberg.bronze.servicenow_incident", "trino_iceberg.iceberg.silver.silver_incident", token)
    add_lineage("trino_iceberg.iceberg.silver.silver_change", "trino_iceberg.iceberg.gold.gold_change_quality", token)
