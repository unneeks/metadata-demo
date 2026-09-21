import argparse
import os
import pandas as pd
from generate_employees import generate_successfactors
from generate_jira import generate_jira
from generate_git import generate_git
from generate_servicenow import generate_servicenow
from generate_attendance import generate_attendance
import random

def main():
    parser = argparse.ArgumentParser(description='Generate synthetic data.')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--employees', type=int, default=1000)
    parser.add_argument('--months', type=int, default=12)
    parser.add_argument('--output', type=str, default='./src')
    
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    
    print(f"Generating SuccessFactors data for {args.employees} employees...")
    employees = generate_successfactors(args.seed, args.employees, args.output)
    
    print(f"Generating Jira data for {args.months} months...")
    jira_users = generate_jira(args.seed, employees, args.months, args.output)
    
    print(f"Generating Git data for {args.months} months...")
    git_users = generate_git(args.seed, employees, args.months, args.output)
    
    print("Generating ServiceNow data...")
    generate_servicenow(args.seed, args.months, args.output)
    
    print("Generating Workplace data...")
    generate_attendance(args.seed, employees, args.months, args.output)
    
    print("Generating Identity Mapping...")
    mappings = []
    
    # 1. SuccessFactors Mapping (Base)
    for emp in employees:
        mappings.append({
            'enterprise_employee_id': emp['employee_id'],
            'source_system': 'SuccessFactors',
            'source_identity': emp['employee_id'],
            'mapping_status': 'ACTIVE',
            'effective_date': '2020-01-01',
            'expiry_date': '9999-12-31'
        })
        
    # 2. Jira Mapping
    for ju in jira_users:
        # Simple heuristic: find employee by name
        matched = [e for e in employees if e['employee_name'] == ju['display_name']]
        if matched and random.random() > 0.05:
            mappings.append({
                'enterprise_employee_id': matched[0]['employee_id'],
                'source_system': 'Jira',
                'source_identity': ju['jira_user_id'],
                'mapping_status': 'ACTIVE',
                'effective_date': '2020-01-01',
                'expiry_date': '9999-12-31'
            })
            
    # 3. Git Mapping
    for gu in git_users:
        # Match by email username approx
        matched = [e for e in employees if e['employee_name'].lower().replace(" ", ".") == gu['username']]
        if matched and random.random() > 0.05:
            mappings.append({
                'enterprise_employee_id': matched[0]['employee_id'],
                'source_system': 'Git',
                'source_identity': gu['git_user_id'],
                'mapping_status': 'ACTIVE',
                'effective_date': '2020-01-01',
                'expiry_date': '9999-12-31'
            })
            
    pd.DataFrame(mappings).to_csv(f"{args.output}/identity_mapping.csv", index=False)
    
    print("Generation complete!")

if __name__ == '__main__':
    main()
