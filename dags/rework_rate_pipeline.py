from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import random

# Default settings for the DAG
default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'rework_rate_pipeline',
    default_args=default_args,
    description='Pipeline to extract Jira data and calculate Rework Rate into Iceberg',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['employee_delivery', 'gold_product'],
) as dag:

    def extract_jira_data():
        print("Extracting issue history from Jira...")
        # Simulated extraction
        return "jira_extract_success"

    def classify_rework():
        print("Classifying issues as rework based on status transitions...")
        # Simulated classification
        return "classification_success"
        
    def calculate_rework_rate():
        print("Calculating Rework Count and Rework Rate...")
        rework_rate = 17.4 + (random.random() - 0.5) # Simulating slight variations around 17.4%
        print(f"Current Rework Rate calculated: {rework_rate:.1f}%")
        return rework_rate

    def write_to_iceberg(ti):
        rework_rate = ti.xcom_pull(task_ids='calculate_rework_rate')
        print(f"Writing Rework Rate {rework_rate:.1f}% to Iceberg table data_lake.employee_data.gold_layer.employee_delivery_data_product...")
        # Simulated write
        
    def run_soda_data_quality():
        print("Running Soda DQ checks on Iceberg table...")
        print("Check: rework_rate IS NOT NULL -> PASS")
        print("Check: rework_rate BETWEEN 0 and 100 -> PASS")

    t1 = PythonOperator(
        task_id='extract_jira_data',
        python_callable=extract_jira_data,
    )

    t2 = PythonOperator(
        task_id='classify_rework',
        python_callable=classify_rework,
    )

    t3 = PythonOperator(
        task_id='calculate_rework_rate',
        python_callable=calculate_rework_rate,
    )

    t4 = PythonOperator(
        task_id='write_to_iceberg',
        python_callable=write_to_iceberg,
    )
    
    t5 = PythonOperator(
        task_id='run_soda_data_quality',
        python_callable=run_soda_data_quality,
    )

    # Lineage definition: extract -> classify -> calculate -> write -> dq
    t1 >> t2 >> t3 >> t4 >> t5
