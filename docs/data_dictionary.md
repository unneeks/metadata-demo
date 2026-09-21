# Data Dictionary

## Gold Employee Delivery

| Column Name | Data Type | Description | Primary Key |
| --- | --- | --- | --- |
| `employee_id` | STRING | Unique identifier for employee | Yes |
| `completed_work_items` | INT | Count of work items completed in period | No |
| `median_cycle_time` | DOUBLE | Median days to complete work item | No |
| `rework_rate` | DOUBLE | Proportion of completed items that were reopened | No |
| `change_related_incident_rate` | DOUBLE | Rate of incidents caused by changes | No |
| `review_participation` | DOUBLE | Proportion of PRs reviewed | No |
| `office_attendance_pattern` | STRING | General location behavior (OFFICE/REMOTE/HYBRID) | No |
| `data_quality_score` | INT | Composite DQ score | No |
| `dq_status` | STRING | PASS/FAIL | No |
