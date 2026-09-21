# Qlik Sense Dashboard Integration

The platform prepares a specific data mart layer for Qlik Sense.

## Load Script
The load script is automatically generated at `qlik/employee_delivery_load.qvs`.

It points to the published CSV / Parquet equivalents in the `qlik/` output directory.

## Recommended Visualizations
1. **Executive View**: KPI cards for Total Work Items, Rework Rate (%), Cycle Time, and Data Quality Score.
2. **Team View**: A table grouped by `team_id` detailing output volume and change-related incidents.
3. **Data Trust View**: Drill-downs into `dq_results.csv` to explain *why* the data quality score fluctuates, exposing injected identity-mapping failures from Jira.
