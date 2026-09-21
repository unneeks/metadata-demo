import pandas as pd
import numpy as np
from faker import Faker
import os
import random
from datetime import timedelta

def generate_git(seed, employees, months, output_dir):
    fake = Faker()
    Faker.seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    
    os.makedirs(f"{output_dir}/git", exist_ok=True)
    
    # 1. Git Users
    git_users = []
    git_user_ids = []
    
    for emp in employees:
        if random.random() > 0.10: # 90% have git accounts
            g_id = f"GH-{random.randint(1000, 9999)}"
            git_user_ids.append(g_id)
            git_users.append({
                'git_user_id': g_id,
                'email': fake.email(),
                'username': emp['employee_name'].lower().replace(" ", ".")
            })
            
    # Shared git accounts (for DQ failures)
    for _ in range(10):
        g_id = f"GH-SHARED-{random.randint(10, 99)}"
        git_user_ids.append(g_id)
        git_users.append({
            'git_user_id': g_id,
            'email': fake.company_email(),
            'username': f"svc.account.{random.randint(1,10)}"
        })
        
    # 2. Repositories
    repos = []
    for i in range(20):
        repos.append({
            'repository_id': f"REPO-{i}",
            'repository_name': fake.slug() + "-service",
            'language': random.choice(['Python', 'Java', 'Go', 'TypeScript'])
        })
    pd.DataFrame(repos).to_csv(f"{output_dir}/git/repository.csv", index=False)
    
    # 3. Commits & PRs & Deployments
    commits = []
    prs = []
    deployments = []
    
    for i in range(500 * months):
        repo_id = random.choice(repos)['repository_id']
        author_id = random.choice(git_user_ids)
        commit_ts = fake.date_time_between(start_date=f"-{months*30}d", end_date='now')
        commit_id = fake.sha1()
        
        commits.append({
            'commit_id': commit_id,
            'repository_id': repo_id,
            'git_user_id': author_id,
            'commit_timestamp': commit_ts,
            'branch': 'main' if random.random() > 0.8 else fake.word(),
            'lines_added': random.randint(1, 500),
            'lines_deleted': random.randint(0, 200)
        })
        
        if random.random() > 0.5: # 50% commits tied to PRs
            pr_id = f"PR-{random.randint(10000, 99999)}"
            prs.append({
                'pull_request_id': pr_id,
                'repository_id': repo_id,
                'author_id': author_id,
                'reviewer_id': random.choice(git_user_ids),
                'created_timestamp': commit_ts - timedelta(hours=random.randint(1, 48)),
                'merged_timestamp': commit_ts,
                'status': 'MERGED'
            })
            
            if random.random() > 0.8: # Some PRs trigger deployments
                deployments.append({
                    'deployment_id': f"DEP-{random.randint(10000, 99999)}",
                    'repository_id': repo_id,
                    'application_id': f"APP-{repo_id}",
                    'deployment_timestamp': commit_ts + timedelta(minutes=random.randint(5, 60)),
                    'status': 'SUCCESS' if random.random() > 0.05 else 'FAILED'
                })
                
    pd.DataFrame(commits).to_csv(f"{output_dir}/git/commit.csv", index=False)
    pd.DataFrame(prs).to_csv(f"{output_dir}/git/pull_request.csv", index=False)
    pd.DataFrame(deployments).to_csv(f"{output_dir}/git/deployment.csv", index=False)
    
    return git_users
