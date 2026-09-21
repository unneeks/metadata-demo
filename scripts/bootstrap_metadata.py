import os
import json
import uuid
import time
from metadata.generated.schema.entity.data.table import Table, Column, DataType, ColumnConstraint
from metadata.generated.schema.entity.data.database import Database
from metadata.generated.schema.entity.data.databaseSchema import DatabaseSchema
from metadata.generated.schema.entity.services.databaseService import DatabaseService, DatabaseServiceType
from metadata.generated.schema.entity.services.connections.database.icebergConnection import IcebergConnection
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import OpenMetadataConnection
from metadata.generated.schema.security.client.openMetadataJWTClientConfig import OpenMetadataJWTClientConfig
from metadata.generated.schema.entity.data.glossary import Glossary
from metadata.generated.schema.entity.data.glossaryTerm import GlossaryTerm
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.generated.schema.type.entityLineage import EntitiesEdge
from metadata.generated.schema.api.lineage.addLineage import AddLineageRequest
from metadata.generated.schema.tests.testCase import TestCase
from metadata.generated.schema.tests.testSuite import TestSuite
from metadata.generated.schema.tests.basic import TestCaseResult, TestCaseStatus
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.generated.schema.entity.services.dashboardService import DashboardService, DashboardServiceType
from metadata.generated.schema.entity.services.connections.dashboard.qlikSenseConnection import QlikSenseConnection
from metadata.generated.schema.entity.data.dashboard import Dashboard
from metadata.generated.schema.entity.services.pipelineService import PipelineService, PipelineServiceType
from metadata.generated.schema.entity.services.connections.pipeline.airflowConnection import AirflowConnection
from metadata.generated.schema.entity.data.pipeline import Pipeline
from metadata.generated.schema.entity.services.messagingService import MessagingService, MessagingServiceType
from metadata.generated.schema.entity.services.connections.messaging.kafkaConnection import KafkaConnection

SERVER_URL = os.getenv("OM_URL", "http://localhost:8585/api")
# We will use basic auth for simplicity, or we can use JWT token if auth is enabled.
# For local dev without auth, we can just connect.
server_config = OpenMetadataConnection(hostPort=SERVER_URL)
metadata = OpenMetadata(server_config)

def create_database_service():
    print("Creating Database Service...")
    service_request = {
        "name": "data_lake",
        "serviceType": DatabaseServiceType.Iceberg.value,
        "connection": {
            "config": {
                "type": "Iceberg",
                "catalogType": "Hive", # Dummy
            }
        }
    }
    # Using raw API to avoid complex model instantiation issues
    res = metadata.client.post("/services/databaseServices", data=json.dumps(service_request))
    return res

def bootstrap():
    print("Starting OpenMetadata Bootstrap...")
    
    # 1. Technical Metadata
    print("Creating Technical Metadata...")
    # Using REST API directly via metadata.client for robustness and less import issues
    
    # Database Service
    db_service = metadata.client.post("/services/databaseServices", data=json.dumps({
        "name": "data_lake",
        "serviceType": "Iceberg",
        "connection": {"config": {"type": "Iceberg"}}
    }))
    
    # Database
    db = metadata.client.post("/databases", data=json.dumps({
        "name": "employee_data",
        "service": "data_lake"
    }))
    
    # Schema
    schema = metadata.client.post("/databaseSchemas", data=json.dumps({
        "name": "gold_layer",
        "database": f"data_lake.employee_data"
    }))
    
    # Table
    table = metadata.client.post("/tables", data=json.dumps({
        "name": "employee_delivery_data_product",
        "databaseSchema": f"data_lake.employee_data.gold_layer",
        "columns": [
            {
                "name": "employee_id",
                "dataType": "VARCHAR",
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
    }))
    
    # Qlik Sense Dashboard
    dashboard_service = metadata.client.post("/services/dashboardServices", data=json.dumps({
        "name": "qlik_bi",
        "serviceType": "QlikSense",
        "connection": {"config": {"type": "QlikSense", "hostPort": "http://localhost"}}
    }))
    
    dashboard = metadata.client.post("/dashboards", data=json.dumps({
        "name": "employee_delivery_dashboard",
        "service": "qlik_bi",
        "charts": []
    }))
    
    # Jira Pipeline
    pipeline_service = metadata.client.post("/services/pipelineServices", data=json.dumps({
        "name": "airflow_orchestrator",
        "serviceType": "Airflow",
        "connection": {"config": {"type": "Airflow", "hostPort": "http://localhost"}}
    }))
    
    pipeline = metadata.client.post("/pipelines", data=json.dumps({
        "name": "jira_to_iceberg_pipeline",
        "service": "airflow_orchestrator"
    }))
    
    # 2. Glossary
    print("Creating Glossary...")
    glossary = metadata.client.post("/glossaries", data=json.dumps({
        "name": "Employee Metrics",
        "description": "Business glossary for employee performance and delivery metrics"
    }))
    
    glossary_term = metadata.client.post("/glossaryTerms", data=json.dumps({
        "name": "Rework Rate",
        "glossary": "Employee Metrics",
        "description": "The percentage of delivery items that required rework. Calculation: (Rework Count / Total Items) * 100",
        "mutuallyExclusive": False
    }))
    
    # Link Glossary to Table Column
    # OpenMetadata allows patching table to add glossary terms
    table_id = table.get("id")
    # Actually, simpler to patch the table via API using JSON Patch to add the glossary term to the column
    patch_op = [
        {
            "op": "add",
            "path": "/columns/2/tags/-",
            "value": {
                "tagFQN": "Employee Metrics.Rework Rate",
                "source": "Glossary",
                "labelType": "Manual",
                "state": "Confirmed"
            }
        }
    ]
    # We won't patch here, let's keep it simple. We can manually link in UI to show the 'Meaning' part of the demo!

    # 3. Lineage
    print("Creating Lineage...")
    # Add lineage from Pipeline to Table, and Table to Dashboard
    metadata.client.put("/lineage", data=json.dumps({
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
    }))
    
    metadata.client.put("/lineage", data=json.dumps({
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
    }))

    # 4. Data Quality
    print("Creating Data Quality Results...")
    test_suite = metadata.client.post("/dataQuality/testSuites", data=json.dumps({
        "name": "rework_rate_quality_suite",
        "description": "DQ checks for Rework Rate",
        "executableEntityReference": f"data_lake.employee_data.gold_layer.employee_delivery_data_product"
    }))
    
    test_case_completeness = metadata.client.post("/dataQuality/testCases", data=json.dumps({
        "name": "rework_rate_completeness",
        "entityLink": f"<#E::table::data_lake.employee_data.gold_layer.employee_delivery_data_product::columns::rework_rate>",
        "testSuite": "rework_rate_quality_suite",
        "testDefinition": "columnValuesToBeNotNull",
        "parameterValues": []
    }))
    
    # Add a PASS result
    metadata.client.put(f"/dataQuality/testCases/{test_case_completeness.get('id')}/testCaseResult", data=json.dumps({
        "timestamp": int(time.time() * 1000),
        "testCaseStatus": "Success",
        "result": "Passed. 0 null values found."
    }))

    print("Bootstrap completed successfully!")

if __name__ == "__main__":
    bootstrap()
