import requests
import json
import time

OM_URL = "http://openmetadata-server:8585/api/v1"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def create_glossary():
    payload = {
        "name": "Engineering_Delivery_Glossary",
        "displayName": "Engineering Delivery Glossary",
        "description": "Business Glossary for Engineering Delivery Metrics"
    }
    r = requests.post(f"{OM_URL}/glossaries", headers=HEADERS, json=payload)
    if r.status_code in (200, 201):
        print("Created Glossary")
    else:
        print("Glossary may already exist or error:", r.text)

def create_term(name, display_name, description):
    payload = {
        "glossary": "Engineering_Delivery_Glossary",
        "name": name,
        "displayName": display_name,
        "description": description
    }
    r = requests.post(f"{OM_URL}/glossaryTerms", headers=HEADERS, json=payload)
    if r.status_code in (200, 201):
        print(f"Created Term: {display_name}")
    else:
        print(f"Term {display_name} may already exist:", r.text)

if __name__ == "__main__":
    time.sleep(5)  # Wait for OM server to be responsive
    create_glossary()
    
    terms = [
        ("Rework_Rate", "Rework Rate", "The proportion of eligible work items classified as rework during a defined reporting period. Rework is determined from defined work-item state transitions."),
        ("Cycle_Time", "Cycle Time", "Median time taken to complete a work item from start to finish."),
        ("Change_Related_Incident", "Change-Related Incident", "An incident caused by a recently deployed change."),
        ("Office_Attendance_Pattern", "Office Attendance Pattern", "Categorization of physical office presence (e.g. Remote, Hybrid, Onsite).")
    ]
    
    for term in terms:
        create_term(term[0], term[1], term[2])
