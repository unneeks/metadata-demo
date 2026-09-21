import requests
import json
import time
import base64

OM_URL = "http://openmetadata-server:8585/api/v1"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    # "Authorization": "Bearer <YOUR_JWT_TOKEN>" # Add JWT token here if auth is enabled
}

def login():
    payload = {
        "email": "admin@openmetadata.org",
        "password": base64.b64encode(b"admin").decode("utf-8")
    }
    r = requests.post(f"{OM_URL}/users/login", headers={"Content-Type": "application/json"}, json=payload)
    if r.status_code == 200:
        return r.json().get("accessToken")
    print("Login failed:", r.text)
    return None

def create_glossary(token):
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    payload = {
        "name": "Engineering_Delivery_Glossary",
        "displayName": "Engineering Delivery Glossary",
        "description": "Business Glossary for Engineering Delivery Metrics"
    }
    r = requests.post(f"{OM_URL}/glossaries", headers=headers, json=payload)
    if r.status_code in (200, 201):
        print("Created Glossary")
    else:
        print("Glossary may already exist or error:", r.text)

def create_term(name, display_name, description, token):
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    payload = {
        "glossary": "Engineering_Delivery_Glossary",
        "name": name,
        "displayName": display_name,
        "description": description
    }
    r = requests.post(f"{OM_URL}/glossaryTerms", headers=headers, json=payload)
    if r.status_code in (200, 201):
        print(f"Created Term: {display_name}")
    else:
        print(f"Term {display_name} may already exist:", r.text)

if __name__ == "__main__":
    time.sleep(5)  # Wait for OM server to be responsive
    token = login()
    if not token:
        print("Failed to get token, exiting.")
        exit(1)
        
    create_glossary(token)
    
    terms = [
        ("Rework_Rate", "Rework Rate", "The proportion of eligible work items classified as rework during a defined reporting period. Rework is determined from defined work-item state transitions."),
        ("Cycle_Time", "Cycle Time", "Median time taken to complete a work item from start to finish."),
        ("Change_Related_Incident", "Change-Related Incident", "An incident caused by a recently deployed change."),
        ("Office_Attendance_Pattern", "Office Attendance Pattern", "Categorization of physical office presence (e.g. Remote, Hybrid, Onsite).")
    ]
    
    for term in terms:
        create_term(term[0], term[1], term[2], token)
