# Lineage

Explicit column-level lineage ensures provenance tracking.

## Hero Lineage: Rework Rate

```
jira.issue_history (status)
       ↓
status_transition_logic (identify REOPENED)
       ↓
rework_flag
       ↓
rework_count / eligible_work_items
       ↓
rework_rate
       ↓
gold_employee_delivery
       ↓
Qlik Sense
```

## ServiceNow Lineage: Change-Related Incident Rate

```
servicenow.change (change_id)
       +
servicenow.incident (incident_id)
       +
change_incident_link
       ↓
change_related_incident_flag
       ↓
change_related_incident_rate
       ↓
gold_employee_delivery
```
