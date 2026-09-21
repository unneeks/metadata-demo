# Data Quality (DQ)

Data Quality validations are run using Great Expectations/PySpark during the Airflow pipeline execution.

## Intentional DQ Failures

To demonstrate the importance of Data Quality in a Data Fabric, the synthetic dataset is injected with intentional failures:

1. **Orphan Jira Users**: ~12% of Jira users do not map to a valid corporate Employee ID in the identity resolution phase.
2. **Missing Employee IDs**: Some records in the Gold dataset will have null employee IDs as a result of the orphan Jira users.

## OpenMetadata Integration

The results of the DQ validations (passed/failed expectations, affected row counts) are pushed to OpenMetadata.
When a user views the `gold_employee_delivery` data product in OpenMetadata, they can navigate to the **Data Quality** tab to see these test results natively. 

The Qlik Sense dashboard also pulls from `dq_results.csv` to render a top-level Data Trust score alongside the business metrics.
