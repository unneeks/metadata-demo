import pandas as pd
import numpy as np
from faker import Faker
import os
import random

def generate_successfactors(seed, num_employees, output_dir):
    fake = Faker()
    Faker.seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    
    os.makedirs(f"{output_dir}/successfactors", exist_ok=True)
    
    # 1. Location
    locations = []
    countries = ['USA', 'UK', 'India', 'Germany', 'Australia', 'Canada', 'Singapore', 'Japan', 'France', 'Brazil']
    for i in range(20):
        locations.append({
            'location_id': f"LOC{i:03d}",
            'city': fake.city(),
            'country': random.choice(countries)
        })
    pd.DataFrame(locations).to_csv(f"{output_dir}/successfactors/location.csv", index=False)
    
    # 2. Division (Organization)
    divisions = []
    for i in range(5):
        divisions.append({
            'division_id': f"DIV{i:03d}",
            'division_name': f"Division {fake.company_suffix()}"
        })
    pd.DataFrame(divisions).to_csv(f"{output_dir}/successfactors/organization.csv", index=False)
    
    # 3. Department
    departments = []
    for i in range(15):
        departments.append({
            'department_id': f"DEP{i:03d}",
            'department_name': fake.bs().title() + " Dept",
            'division_id': random.choice(divisions)['division_id']
        })
    pd.DataFrame(departments).to_csv(f"{output_dir}/successfactors/department.csv", index=False)
    
    # 4. Team
    teams = []
    for i in range(40):
        teams.append({
            'team_id': f"TEAM{i:03d}",
            'team_name': fake.catch_phrase().title() + " Squad",
            'department_id': random.choice(departments)['department_id']
        })
    pd.DataFrame(teams).to_csv(f"{output_dir}/successfactors/team.csv", index=False)
    
    # 5. Employee
    employees = []
    emp_ids = [f"EMP{i:06d}" for i in range(1, num_employees + 1)]
    for emp_id in emp_ids:
        is_active = random.random() > 0.15 # 85% active
        hire_date = fake.date_between(start_date='-5y', end_date='-1y')
        term_date = fake.date_between(start_date=hire_date, end_date='today') if not is_active else None
        
        employees.append({
            'employee_id': emp_id,
            'employee_name': fake.name(),
            'employee_status': 'ACTIVE' if is_active else 'TERMINATED',
            'hire_date': hire_date,
            'termination_date': term_date,
            'job_title': fake.job(),
            'job_level': random.choice(['L1', 'L2', 'L3', 'L4', 'L5', 'L6']),
            'department_id': random.choice(departments)['department_id'],
            'team_id': random.choice(teams)['team_id'],
            'manager_employee_id': random.choice(emp_ids) if random.random() > 0.05 else None,
            'location_id': random.choice(locations)['location_id'],
            'employment_type': random.choice(['FULL_TIME', 'PART_TIME', 'CONTRACTOR'])
        })
    pd.DataFrame(employees).to_csv(f"{output_dir}/successfactors/employee.csv", index=False)
    
    # 6. Performance Review
    reviews = []
    review_cycles = ['2022-H1', '2022-H2', '2023-H1', '2023-H2']
    outcomes = ['NEEDS_IMPROVEMENT', 'MEETS_EXPECTATIONS', 'EXCEEDS_EXPECTATIONS', 'OUTSTANDING']
    for emp in employees:
        for cycle in review_cycles:
            if random.random() > 0.2: # 80% have review
                reviews.append({
                    'review_id': f"REV_{emp['employee_id']}_{cycle}",
                    'employee_id': emp['employee_id'],
                    'review_period': cycle,
                    'review_date': fake.date_between(start_date='-2y', end_date='today'),
                    'review_status': 'COMPLETED',
                    'outcome_category': random.choices(outcomes, weights=[0.1, 0.6, 0.2, 0.1])[0],
                    'review_cycle': cycle
                })
    pd.DataFrame(reviews).to_csv(f"{output_dir}/successfactors/performance_review.csv", index=False)
    
    return employees
