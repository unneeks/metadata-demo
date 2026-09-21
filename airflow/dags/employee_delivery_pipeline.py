from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta

default_args = {
    'owner': 'data_platform_team',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'employee_delivery_pipeline',
    default_args=default_args,
    description='End-to-End Medallion Pipeline for Employee Delivery Data Product',
    schedule_interval='@daily',
    catchup=False,
    tags=['medallion', 'iceberg', 'spark', 'demonstrator'],
) as dag:

    start = DummyOperator(task_id='start')

    with TaskGroup("ingest") as ingest:
        # In a real environment this would pull from source systems.
        # Here we just run the generator script if it hasn't been run.
        generate_data = BashOperator(
            task_id='generate_synthetic_data',
            bash_command='python3 /opt/airflow/src/../generators/generate_all.py --output /opt/airflow/src'
        )

    with TaskGroup("bronze") as bronze:
        load_successfactors = BashOperator(
            task_id='bronze_successfactors',
            bash_command='spark-submit /opt/airflow/spark/bronze_load.py --source successfactors'
        )
        load_jira = BashOperator(
            task_id='bronze_jira',
            bash_command='spark-submit /opt/airflow/spark/bronze_load.py --source jira'
        )
        load_git = BashOperator(
            task_id='bronze_git',
            bash_command='spark-submit /opt/airflow/spark/bronze_load.py --source git'
        )
        load_servicenow = BashOperator(
            task_id='bronze_servicenow',
            bash_command='spark-submit /opt/airflow/spark/bronze_load.py --source servicenow'
        )
        load_workplace = BashOperator(
            task_id='bronze_workplace',
            bash_command='spark-submit /opt/airflow/spark/bronze_load.py --source workplace'
        )

    with TaskGroup("silver") as silver:
        standardize = BashOperator(
            task_id='standardize_schemas',
            bash_command='spark-submit /opt/airflow/spark/silver_standardize.py'
        )
        identity_resolution = BashOperator(
            task_id='identity_resolution',
            bash_command='spark-submit /opt/airflow/spark/silver_identity.py'
        )
        conformed_entities = BashOperator(
            task_id='conformed_entities',
            bash_command='spark-submit /opt/airflow/spark/silver_conformed.py'
        )
        
        standardize >> identity_resolution >> conformed_entities

    with TaskGroup("gold") as gold:
        gold_metrics = BashOperator(
            task_id='calculate_metrics',
            bash_command='spark-submit /opt/airflow/spark/gold_metrics.py'
        )
        gold_delivery = BashOperator(
            task_id='employee_delivery_data_product',
            bash_command='spark-submit /opt/airflow/spark/gold_delivery.py'
        )
        
        gold_metrics >> gold_delivery

    with TaskGroup("dq") as dq:
        run_dq_rules = BashOperator(
            task_id='run_dq_validation',
            bash_command='spark-submit /opt/airflow/spark/dq_validation.py'
        )

    with TaskGroup("metadata") as metadata:
        gen_glossary = BashOperator(
            task_id='generate_glossary',
            bash_command='python3 /opt/airflow/spark/generate_metadata.py --type glossary'
        )
        gen_technical = BashOperator(
            task_id='generate_technical_metadata',
            bash_command='python3 /opt/airflow/spark/generate_metadata.py --type technical'
        )
        gen_ontology = BashOperator(
            task_id='generate_ontology',
            bash_command='python3 /opt/airflow/spark/generate_metadata.py --type ontology'
        )

    with TaskGroup("lineage") as lineage:
        gen_lineage = BashOperator(
            task_id='generate_lineage',
            bash_command='python3 /opt/airflow/spark/generate_metadata.py --type lineage'
        )

    with TaskGroup("publish") as publish:
        publish_qlik = BashOperator(
            task_id='publish_to_qlik',
            bash_command='python3 /opt/airflow/spark/publish_qlik.py'
        )
        publish_abinitio = BashOperator(
            task_id='publish_to_abinitio',
            bash_command='python3 /opt/airflow/spark/publish_abinitio.py'
        )

    end = DummyOperator(task_id='end')

    # Define Dependencies
    start >> ingest >> bronze >> silver >> gold >> dq >> metadata >> lineage >> publish >> end
