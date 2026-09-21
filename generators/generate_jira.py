import pandas as pd
import numpy as np
from faker import Faker
import os
import random
from datetime import timedelta

def generate_jira(seed, employees, months, output_dir):
    fake = Faker()
    Faker.seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    
    os.makedirs(f"{output_dir}/jira", exist_ok=True)
    
    # 1. Jira Users
    jira_users = []
    jira_user_ids = []
    
    # Map some employees to Jira users
    for emp in employees:
        if random.random() > 0.05: # 95% mapped correctly
            j_id = f"USR-{random.randint(10000, 99999)}"
            jira_user_ids.append(j_id)
            jira_users.append({
                'jira_user_id': j_id,
                'email': fake.email(),
                'display_name': emp['employee_name'],
                'active': True
            })
            
    # Orphan Jira users (for DQ failures)
    for _ in range(50):
        j_id = f"USR-{random.randint(10000, 99999)}"
        jira_user_ids.append(j_id)
        jira_users.append({
            'jira_user_id': j_id,
            'email': fake.email(),
            'display_name': fake.name(),
            'active': True
        })
        
    pd.DataFrame(jira_users).to_csv(f"{output_dir}/jira/jira_user.csv", index=False)
    
    # 2. Projects
    projects = []
    project_keys = []
    for i in range(10):
        key = fake.word().upper()[:4]
        project_keys.append(key)
        projects.append({
            'project_id': f"PRJ-{i}",
            'project_key': key,
            'project_name': fake.bs().title()
        })
    pd.DataFrame(projects).to_csv(f"{output_dir}/jira/project.csv", index=False)
    
    # 3. Sprints
    sprints = []
    sprint_ids = []
    for p in projects:
        for i in range(months * 2): # 2 week sprints
            s_id = f"SPR-{p['project_id']}-{i}"
            sprint_ids.append(s_id)
            sprints.append({
                'sprint_id': s_id,
                'project_id': p['project_id'],
                'sprint_name': f"Sprint {i}",
                'start_date': fake.date_between(start_date=f"-{months*30}d", end_date='today'),
                'end_date': fake.date_between(start_date='today', end_date='+14d')
            })
    pd.DataFrame(sprints).to_csv(f"{output_dir}/jira/sprint.csv", index=False)
    
    # 4. Issues & History
    issues = []
    issue_history = []
    
    status_flow = ['TO_DO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE']
    
    for i in range(300 * months): # rough number of issues
        p_key = random.choice(project_keys)
        issue_id = f"{p_key}-{random.randint(1000, 9999)}"
        created = fake.date_time_between(start_date=f"-{months*30}d", end_date='now')
        
        is_rework = random.random() < 0.15 # 15% rework rate
        
        reporter = random.choice(jira_user_ids)
        assignee = random.choice(jira_user_ids)
        
        issues.append({
            'issue_id': issue_id,
            'project_id': next(p['project_id'] for p in projects if p['project_key'] == p_key),
            'jira_user_id': assignee,
            'issue_type': random.choice(['Story', 'Task', 'Bug']),
            'summary': fake.sentence(),
            'priority': random.choice(['High', 'Medium', 'Low']),
            'created_timestamp': created,
            'resolved_timestamp': created + timedelta(days=random.randint(1, 14)),
            'status': 'DONE',
            'sprint_id': random.choice(sprint_ids),
            'story_points': random.choice([1, 2, 3, 5, 8])
        })
        
        # Build history
        curr_time = created
        for stat in status_flow:
            issue_history.append({
                'issue_id': issue_id,
                'status': stat,
                'changed_timestamp': curr_time,
                'changed_by': assignee
            })
            curr_time += timedelta(hours=random.randint(2, 48))
            
        if is_rework:
            issue_history.append({
                'issue_id': issue_id,
                'status': 'REOPENED',
                'changed_timestamp': curr_time,
                'changed_by': reporter
            })
            curr_time += timedelta(hours=random.randint(1, 24))
            issue_history.append({
                'issue_id': issue_id,
                'status': 'IN_PROGRESS',
                'changed_timestamp': curr_time,
                'changed_by': assignee
            })
            curr_time += timedelta(hours=random.randint(4, 48))
            issue_history.append({
                'issue_id': issue_id,
                'status': 'DONE',
                'changed_timestamp': curr_time,
                'changed_by': assignee
            })
            
    pd.DataFrame(issues).to_csv(f"{output_dir}/jira/issue.csv", index=False)
    pd.DataFrame(issue_history).to_csv(f"{output_dir}/jira/issue_history.csv", index=False)
    
    return jira_users
