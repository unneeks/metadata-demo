# Target Architecture

```
                         SOURCE SYSTEMS
       SuccessFactors       Jira        Git       ServiceNow      Workplace
              │              │          │             │              │
              └──────────────┼──────────┴─────────────┴──────────────┘
                             │
                       ServiceNow
                             │
                        Workplace
                             │
                             ▼
                    ┌─────────────────┐
                    │  APACHE AIRFLOW │
                    │ Integration &   │
                    │ Orchestration   │
                    └────────┬────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │     DATA LAKE       │
                  │                     │
                  │ Object Storage      │
                  │ MinIO               │
                  │                     │
                  │ Apache Iceberg      │
                  │ Bronze → Silver     │
                  │          → Gold     │
                  └──────────┬──────────┘
                             │
                         Apache Spark
                      transformations
                             │
                             ▼
                EMPLOYEE DELIVERY DATA PRODUCT
                             │
                 ┌───────────┼───────────┐
                 │           │           │
                 ▼           ▼           ▼
             QLIK SENSE   AB INITIO    NEO4J
             Analytics    Metadata     Knowledge
                          Hub          Graph
                 │           │           │
                 │           ├───────────┤
                 │           │
                 │       Glossary
                 │       Lineage
                 │       Technical Metadata
                 │       Data Quality
                 │
                 ▼
              BUSINESS
              CONSUMERS
```
