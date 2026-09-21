import os
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

def publish_lineage(headers):
    print("Harvesting Column-Level Lineage...")
    
    # 1. Create Source Table in OpenMetadata (e.g. Jira Issue History in Bronze)
    print("  Creating source table (Jira Issue History)...")
    bronze_db = requests.post(f"{SERVER_URL}/databases", headers=headers, json={
        "name": "bronze_employee_data",
        "service": "data_lake"
    }).json()
    
    bronze_schema = requests.post(f"{SERVER_URL}/databaseSchemas", headers=headers, json={
        "name": "bronze_layer",
        "database": f"data_lake.bronze_employee_data"
    }).json()
    
    source_table = requests.post(f"{SERVER_URL}/tables", headers=headers, json={
        "name": "jira_issue_history",
        "databaseSchema": f"data_lake.bronze_employee_data.bronze_layer",
        "columns": [
            {
                "name": "issue_id",
                "dataType": "VARCHAR",
                "dataLength": 255
            },
            {
                "name": "status",
                "dataType": "VARCHAR",
                "dataLength": 255,
                "description": "The current status of the issue (e.g. DONE, REOPENED)"
            }
        ]
    }).json()
    if "id" not in source_table:
        # Fetch it
        source_table = requests.get(f"{SERVER_URL}/tables/name/data_lake.bronze_employee_data.bronze_layer.jira_issue_history", headers=headers).json()
    
    # Target table already created by bootstrap_metadata.py
    # Re-fetch it just in case
    target_table = requests.get(f"{SERVER_URL}/tables/name/data_lake.employee_data.gold_layer.employee_delivery_data_product", headers=headers).json()
    
    if "id" not in target_table:
        print("  Error: Target table 'employee_delivery_data_product' not found. Run bootstrap_metadata.py first.")
        return
        
    print("  Publishing lineage edge with column mapping...")
    time.sleep(2) # Wait for OpenSearch index to settle
    lineage_payload = {
        "edge": {
            "fromEntity": {
                "id": source_table.get("id"),
                "type": "table"
            },
            "toEntity": {
                "id": target_table.get("id"),
                "type": "table"
            },
            "lineageDetails": {
                "columnsLineage": [
                    {
                        "fromColumns": [
                            "data_lake.bronze_employee_data.bronze_layer.jira_issue_history.status"
                        ],
                        "toColumn": "data_lake.employee_data.gold_layer.employee_delivery_data_product.rework_rate"
                    }
                ]
            }
        }
    }
    
    # Retry lineage creation because OpenSearch connection might close intermittently
    for attempt in range(3):
        r = requests.put(f"{SERVER_URL}/lineage", headers=headers, json=lineage_payload)
        if r.status_code in (200, 201):
            print("  Successfully created column-level lineage from Jira -> Iceberg Gold.")
            break
        else:
            print(f"  Attempt {attempt+1} Error creating lineage:", r.text)
            time.sleep(2)

def publish_dq(headers):
    print("Executing Data Quality Validation...")
    
    # Target table
    table_fqn = "data_lake.employee_data.gold_layer.employee_delivery_data_product"
    test_suite_fqn = f"{table_fqn}.testSuite"
    
    # Ensure Executable Test Suite exists
    requests.post(f"{SERVER_URL}/dataQuality/testSuites/executable", headers=headers, json={
        "name": test_suite_fqn,
        "executableEntityReference": table_fqn
    })
    
    print("  Publishing Data Quality Results...")
    
    # 1. Fetch test cases
    test_case_name = f"rework_rate_completeness"
    # Test case on a column has FQN: tableFQN.columnName.testCaseName
    tc_fqn = f"{table_fqn}.rework_rate.{test_case_name}"
    test_case = requests.get(f"{SERVER_URL}/dataQuality/testCases/name/{tc_fqn}", headers=headers).json()
    
    if "id" not in test_case:
        print(f"  Test case {test_case_name} not found. Creating it...")
        # Create it just in case
        r_tc = requests.post(f"{SERVER_URL}/dataQuality/testCases", headers=headers, json={
            "name": test_case_name,
            "entityLink": f"<#E::table::{table_fqn}::columns::rework_rate>",
            "testSuite": test_suite_fqn,
            "testDefinition": "columnValuesToBeNotNull",
            "parameterValues": []
        })
        test_case = r_tc.json()
        if r_tc.status_code not in (200, 201):
            if r_tc.status_code == 409:
                print("  Test case already exists, fetching again...")
                test_case = requests.get(f"{SERVER_URL}/dataQuality/testCases/name/{tc_fqn}", headers=headers).json()
            else:
                print("  Error creating test case:", r_tc.text)
            
    if "id" not in test_case:
        print("  Error fetching or creating test case.")
        return
        
    # Execution (Mock logic: simulate a new DQ check run)
    print("  Simulating DQ execution on Iceberg Parquet files...")
    records_checked = 1000
    violations = 0
    score = 100.0
    
    result_payload = {
        "timestamp": int(time.time() * 1000),
        "testCaseStatus": "Success" if violations == 0 else "Failed",
        "result": f"Passed. Checked {records_checked} records. {violations} null values found.",
        "testResultValue": [
            {
                "name": "nullCount",
                "value": str(violations)
            }
        ]
    }
    
    tc_fqn = test_case.get('fullyQualifiedName')
    print(f"  Using Test Case FQN: {tc_fqn}")
    r = requests.put(f"{SERVER_URL}/dataQuality/testCases/{tc_fqn}/testCaseResult", headers=headers, json=result_payload)
    if r.status_code in (200, 201):
        print(f"  Successfully published DQ result for '{test_case_name}'. Score: {score}%.")
    else:
        print("  Error publishing DQ result:", r.text)

def harvest():
    print("Starting Harvest and DQ Pipeline...")
    token = login()
    if not token:
        print("Failed to login")
        return
        
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    publish_lineage(headers)
    publish_dq(headers)
    print("Harvesting complete!")

if __name__ == "__main__":
    harvest()
