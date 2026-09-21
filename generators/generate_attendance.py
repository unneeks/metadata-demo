import pandas as pd
import numpy as np
from faker import Faker
import os
import random
from datetime import timedelta, date

def generate_attendance(seed, employees, months, output_dir):
    fake = Faker()
    Faker.seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    
    os.makedirs(f"{output_dir}/workplace", exist_ok=True)
    
    events = []
    
    start_date = date.today() - timedelta(days=months*30)
    end_date = date.today()
    
    delta = end_date - start_date
    all_dates = [start_date + timedelta(days=i) for i in range(delta.days)]
    work_dates = [d for d in all_dates if d.weekday() < 5] # Monday to Friday
    
    for emp in employees:
        emp_id = emp['employee_id']
        # Each employee has a preference
        pref = random.choice(['OFFICE_HEAVY', 'REMOTE_HEAVY', 'HYBRID'])
        
        for d in work_dates:
            if random.random() < 0.05:
                event_type = 'LEAVE'
            elif random.random() < 0.02:
                event_type = 'BUSINESS_TRAVEL'
            else:
                if pref == 'OFFICE_HEAVY':
                    event_type = 'OFFICE' if random.random() < 0.8 else 'REMOTE'
                elif pref == 'REMOTE_HEAVY':
                    event_type = 'REMOTE' if random.random() < 0.8 else 'OFFICE'
                else:
                    event_type = 'OFFICE' if random.random() < 0.5 else 'REMOTE'
                    
            events.append({
                'attendance_event_id': fake.uuid4(),
                'employee_id': emp_id,
                'event_date': d,
                'location_type': 'OFFICE' if event_type == 'OFFICE' else 'NON_OFFICE',
                'event_type': event_type
            })
            
            # Inject duplicate attendance event for DQ
            if random.random() < 0.001:
                events.append({
                    'attendance_event_id': fake.uuid4(),
                    'employee_id': emp_id,
                    'event_date': d,
                    'location_type': 'NON_OFFICE',
                    'event_type': 'REMOTE'
                })
                
    pd.DataFrame(events).to_csv(f"{output_dir}/workplace/attendance_event.csv", index=False)
