# Data Quality Framework

## Dimensions
1. **Completeness**: Are required values present?
2. **Validity**: Are values within acceptable ranges?
3. **Uniqueness**: Are identifiers uniquely mapped?
4. **Consistency**: Do values agree across systems?
5. **Referential Integrity**: Do foreign keys point to valid records?
6. **Timeliness**: Is the data fresh?

## Rules

| ID | Name | Dimension | Description |
| --- | --- | --- | --- |
| DQ_001 | Valid Identity Mapping | Referential Integrity | All Jira users must map to an active Employee. |
| DQ_002 | Valid Rework Rate | Validity | Rework rate must be between 0 and 1. |
| DQ_003 | Unique Attendance | Uniqueness | No duplicate attendance events for the same day. |
