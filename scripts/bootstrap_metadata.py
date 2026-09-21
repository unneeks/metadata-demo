import os
import json
import time
import requests
import base64

SERVER_URL = os.getenv("OM_URL", "http://localhost:8585/api/v1")
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def login():
    payload = {
        "email": "admin@openmetadata.org",
        "password": base64.b64encode(b"admin").decode("utf-8")
    }
    r = requests.post(f"{SERVER_URL}/users/login", headers={"Content-Type": "application/json"}, json=payload)
    if r.status_code == 200:
        return r.json().get("accessToken")
    print("Login failed:", r.text)
    return None

def bootstrap():
    print("Starting OpenMetadata Bootstrap...")
    
    token = login()
    if not token:
        print("Failed to login")
        return
        
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    # 1. Technical Metadata
    print("Creating Technical Metadata...")
    
    db_service = requests.post(f"{SERVER_URL}/services/databaseServices", headers=headers, json={
        "name": "data_lake",
        "serviceType": "Iceberg",
        "connection": {"config": {"type": "Iceberg", "catalog": {"name": "dummy"}}}
    }).json()
    
    db = requests.post(f"{SERVER_URL}/databases", headers=headers, json={
        "name": "employee_data",
        "service": "data_lake"
    }).json()
    
    schema = requests.post(f"{SERVER_URL}/databaseSchemas", headers=headers, json={
        "name": "gold_layer",
        "database": f"data_lake.employee_data"
    }).json()
    
    table = requests.post(f"{SERVER_URL}/tables", headers=headers, json={
        "name": "employee_delivery_data_product",
        "databaseSchema": f"data_lake.employee_data.gold_layer",
        "columns": [
            {
                "name": "employee_id",
                "dataType": "VARCHAR",
                "dataLength": 255,
                "description": "Unique identifier for the employee"
            },
            {
                "name": "rework_count",
                "dataType": "INT",
                "description": "Number of reworked items"
            },
            {
                "name": "rework_rate",
                "dataType": "FLOAT",
                "description": "Rate of rework (rework_count / total_items)"
            }
        ]
    }).json()
    
    dashboard_service = requests.post(f"{SERVER_URL}/services/dashboardServices", headers=headers, json={
        "name": "qlik_bi",
        "serviceType": "QlikSense",
        "connection": {"config": {"type": "QlikSense", "hostPort": "http://localhost"}}
    }).json()
    
    dashboard = requests.post(f"{SERVER_URL}/dashboards", headers=headers, json={
        "name": "employee_delivery_dashboard",
        "service": "qlik_bi",
        "charts": []
    }).json()
    
    pipeline_service = requests.post(f"{SERVER_URL}/services/pipelineServices", headers=headers, json={
        "name": "airflow_orchestrator",
        "serviceType": "Airflow",
        "connection": {"config": {"type": "Airflow", "hostPort": "http://localhost"}}
    }).json()
    
    pipeline = requests.post(f"{SERVER_URL}/pipelines", headers=headers, json={
        "name": "jira_to_iceberg_pipeline",
        "service": "airflow_orchestrator"
    }).json()
    
    # 2. Glossary
    print("Creating Glossary...")
    glossary = requests.post(f"{SERVER_URL}/glossaries", headers=headers, json={
        "name": "Employee Metrics",
        "description": "Business glossary for employee performance and delivery metrics"
    }).json()
    
    glossary_term = requests.post(f"{SERVER_URL}/glossaryTerms", headers=headers, json={
        "name": "Rework Rate",
        "glossary": "Employee Metrics",
        "description": "The percentage of delivery items that required rework. Calculation: (Rework Count / Total Items) * 100",
        "mutuallyExclusive": False
    }).json()
    
    # 3. Lineage
    print("Creating Lineage...")
    requests.put(f"{SERVER_URL}/lineage", headers=headers, json={
        "edge": {
            "fromEntity": {
                "id": pipeline.get("id"),
                "type": "pipeline"
            },
            "toEntity": {
                "id": table.get("id"),
                "type": "table"
            }
        }
    })
    
    requests.put(f"{SERVER_URL}/lineage", headers=headers, json={
        "edge": {
            "fromEntity": {
                "id": table.get("id"),
                "type": "table"
            },
            "toEntity": {
                "id": dashboard.get("id"),
                "type": "dashboard"
            }
        }
    })

    # 4. Data Quality
    print("Creating Data Quality Results...")
    test_suite = requests.post(f"{SERVER_URL}/dataQuality/testSuites", headers=headers, json={
        "name": "rework_rate_quality_suite",
        "description": "DQ checks for Rework Rate",
        "executableEntityReference": f"data_lake.employee_data.gold_layer.employee_delivery_data_product"
    }).json()
    
    test_case_completeness = requests.post(f"{SERVER_URL}/dataQuality/testCases", headers=headers, json={
        "name": "rework_rate_completeness",
        "entityLink": f"<#E::table::data_lake.employee_data.gold_layer.employee_delivery_data_product::columns::rework_rate>",
        "testSuite": "rework_rate_quality_suite",
        "testDefinition": "columnValuesToBeNotNull",
        "parameterValues": []
    }).json()
    
    requests.put(f"{SERVER_URL}/dataQuality/testCases/{test_case_completeness.get('id')}/testCaseResult", headers=headers, json={
        "timestamp": int(time.time() * 1000),
        "testCaseStatus": "Success",
        "result": "Passed. 0 null values found."
    })

    print("Bootstrap completed successfully!")

if __name__ == "__main__":
    bootstrap()
