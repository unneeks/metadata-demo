from pyspark.sql import SparkSession
import pandas as pd
import os
from datetime import datetime

def run_dq(spark):
    print("Running Data Quality validation...")
    
    # We will generate synthetic DQ results for the demonstrator.
    # In a real environment we'd use Great Expectations or Soda Core.
    
    results = []
    
    # Rule 1: Identity mapping unmatched Jira users
    results.append({
        'dq_rule_id': 'DQ_001',
        'execution_timestamp': datetime.now().isoformat(),
        'dataset': 'silver_identity',
        'column': 'jira_user_id',
        'dimension': 'Referential Integrity',
        'records_checked': 12000,
        'violations': 50, # Injected orphan users
        'score': 99.5,
        'status': 'FAIL',
        'severity': 'HIGH'
    })
    
    # Rule 2: Rework rate range
    results.append({
        'dq_rule_id': 'DQ_002',
        'execution_timestamp': datetime.now().isoformat(),
        'dataset': 'gold_delivery',
        'column': 'rework_rate',
        'dimension': 'Validity',
        'records_checked': 1000,
        'violations': 0,
        'score': 100.0,
        'status': 'PASS',
        'severity': 'HIGH'
    })
    
    # Output DQ results
    os.makedirs("/opt/airflow/metadata/dq", exist_ok=True)
    pd.DataFrame(results).to_csv("/opt/airflow/metadata/dq/dq_results.csv", index=False)
    
    print("DQ validation complete.")

if __name__ == "__main__":
    spark = SparkSession.builder.appName("DQ Validation").getOrCreate()
    run_dq(spark)
    spark.stop()
