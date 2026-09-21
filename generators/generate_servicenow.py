import pandas as pd
import numpy as np
from faker import Faker
import os
import random
from datetime import timedelta

def generate_servicenow(seed, months, output_dir):
    fake = Faker()
    Faker.seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    
    os.makedirs(f"{output_dir}/servicenow", exist_ok=True)
    
    # 1. Changes
    changes = []
    change_ids = []
    for i in range(100 * months):
        c_id = f"CHG{random.randint(100000, 999999)}"
        change_ids.append(c_id)
        start = fake.date_time_between(start_date=f"-{months*30}d", end_date='now')
        changes.append({
            'change_id': c_id,
            'application_id': f"APP-REPO-{random.randint(0, 19)}",
            'change_type': random.choice(['Standard', 'Normal', 'Emergency']),
            'planned_start': start,
            'planned_end': start + timedelta(hours=random.randint(1, 4)),
            'implementation_status': random.choices(['Successful', 'Successful with issues', 'Failed'], weights=[0.8, 0.15, 0.05])[0],
            'risk': random.choice(['High', 'Medium', 'Low'])
        })
    pd.DataFrame(changes).to_csv(f"{output_dir}/servicenow/change_request.csv", index=False)
    
    # 2. Incidents
    incidents = []
    incident_ids = []
    for i in range(200 * months):
        i_id = f"INC{random.randint(100000, 999999)}"
        incident_ids.append(i_id)
        opened = fake.date_time_between(start_date=f"-{months*30}d", end_date='now')
        incidents.append({
            'incident_id': i_id,
            'application_id': f"APP-REPO-{random.randint(0, 19)}",
            'opened_timestamp': opened,
            'resolved_timestamp': opened + timedelta(hours=random.randint(1, 48)),
            'severity': random.choice(['1 - Critical', '2 - High', '3 - Moderate', '4 - Low']),
            'category': random.choice(['Software', 'Hardware', 'Network', 'Database']),
            'status': 'Resolved'
        })
    pd.DataFrame(incidents).to_csv(f"{output_dir}/servicenow/incident.csv", index=False)
    
    # 3. Change Incident Links
    links = []
    for inc in incidents:
        if random.random() < 0.15: # 15% of incidents are change-related
            # Find a change for the same app that happened recently
            app_changes = [c for c in changes if c['application_id'] == inc['application_id'] and c['planned_start'] <= inc['opened_timestamp']]
            if app_changes:
                related_chg = sorted(app_changes, key=lambda x: x['planned_start'], reverse=True)[0]
                links.append({
                    'incident_id': inc['incident_id'],
                    'change_id': related_chg['change_id'],
                    'relationship_type': 'CAUSED_BY'
                })
                
    # Inject bad data: incident linked to non-existent change
    for _ in range(10):
        links.append({
            'incident_id': random.choice(incident_ids),
            'change_id': "CHG_INVALID_999",
            'relationship_type': 'CAUSED_BY'
        })
        
    pd.DataFrame(links).to_csv(f"{output_dir}/servicenow/change_incident_link.csv", index=False)
