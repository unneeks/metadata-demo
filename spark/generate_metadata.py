import argparse
import os
import json
import pandas as pd

def generate_glossary():
    print("Generating glossary...")
    os.makedirs("/opt/airflow/metadata/glossary", exist_ok=True)
    terms = [
        {
            'term_id': 'TERM_001',
            'term_name': 'Rework Rate',
            'definition': 'The proportion of eligible work items classified as rework during a defined reporting period.',
            'business_description': 'Measures how often work needs to be revisited after being considered done.',
            'domain': 'Delivery',
            'owner': 'Data Governance',
            'steward': 'Engineering Ops',
            'status': 'APPROVED'
        },
        {
            'term_id': 'TERM_002',
            'term_name': 'Rework',
            'definition': 'Work performed on an item after it has reached an agreed completion state.',
            'business_description': 'Identified by status transitioning from DONE to REOPENED.',
            'domain': 'Delivery',
            'owner': 'Data Governance',
            'steward': 'Engineering Ops',
            'status': 'APPROVED'
        }
    ]
    pd.DataFrame(terms).to_csv("/opt/airflow/metadata/glossary/glossary.csv", index=False)
    with open("/opt/airflow/metadata/glossary/glossary.json", "w") as f:
        json.dump(terms, f, indent=2)

def generate_technical():
    print("Generating technical metadata...")
    os.makedirs("/opt/airflow/metadata/technical", exist_ok=True)
    cols = [
        {
            'dataset_name': 'gold_employee_delivery',
            'column_name': 'rework_rate',
            'data_type': 'DOUBLE',
            'business_term': 'TERM_001'
        }
    ]
    pd.DataFrame(cols).to_csv("/opt/airflow/metadata/technical/columns.csv", index=False)

def generate_ontology():
    print("Generating ontology...")
    os.makedirs("/opt/airflow/metadata/ontology", exist_ok=True)
    nodes = [
        {'node_id': 'N1', 'node_type': 'Employee', 'name': 'Employee'},
        {'node_id': 'N2', 'node_type': 'Team', 'name': 'Team'}
    ]
    pd.DataFrame(nodes).to_csv("/opt/airflow/metadata/ontology/nodes.csv", index=False)
    
    rels = [
        {'relationship_id': 'R1', 'subject': 'N1', 'relationship_type': 'BELONGS_TO', 'object': 'N2'}
    ]
    pd.DataFrame(rels).to_csv("/opt/airflow/metadata/ontology/relationships.csv", index=False)

def generate_lineage():
    print("Generating lineage...")
    os.makedirs("/opt/airflow/metadata/lineage", exist_ok=True)
    lineage = [
        {
            'source_dataset': 'jira.issue_history',
            'source_column': 'status',
            'transformation': 'status_transition_logic',
            'target_dataset': 'gold_employee_delivery',
            'target_column': 'rework_rate'
        }
    ]
    pd.DataFrame(lineage).to_csv("/opt/airflow/metadata/lineage/lineage.csv", index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', required=True)
    args = parser.parse_args()
    
    if args.type == 'glossary':
        generate_glossary()
    elif args.type == 'technical':
        generate_technical()
    elif args.type == 'ontology':
        generate_ontology()
    elif args.type == 'lineage':
        generate_lineage()
