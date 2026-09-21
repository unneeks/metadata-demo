# Brown-Bag Demo Script (15-25 Minutes)

## Introduction (3 mins)
- Briefly describe the Data Fabric concept: Connecting data with meaning, context, and trust.

## Step 1: Open Qlik Sense (3 mins)
- Point to the KPI card for **Rework Rate**.
- Ask the audience: *"Would you trust this number?"*

## Step 2: The Business Glossary (4 mins)
- Ask: *"What exactly does Rework mean?"*
- Switch to the Ab Initio Glossary view (or `glossary.md`).
- Show the definition and the specific condition (status transition from DONE to REOPENED).
- **Key Message:** A metric without a shared definition is not a reliable business metric.

## Step 3: Ontology & Context (4 mins)
- Ask: *"What is Rework related to?"*
- Open Neo4j and run a conceptual query.
- Trace the path from `Employee` -> `Team` -> `Work Item` -> `Rework` -> `Change` -> `Incident`.
- **Key Message:** Ontology tells us how things relate.

## Step 4: Lineage (4 mins)
- Ask: *"Where did this number come from?"*
- Show the explicit column-level lineage graph.
- Trace backwards from the Qlik Sense dashboard all the way to the `jira.issue_history` source table.
- **Key Message:** Lineage turns a number into something we can explain.

## Step 5: Data Quality & Trust (4 mins)
- Ask: *"Can we trust the number?"*
- Show the DQ dashboard/results.
- Highlight the injected failure: *"12% of Jira Users are unmatched to a corporate Employee ID."*
- Show the downstream impact: Rework numbers might be misattributed.
- **Key Message:** Data quality isn't just green or red, it's fitness for intended use.

## Step 6: AI / Agent Scenario (3 mins)
- End with a hypothetical scenario.
- Ask an AI agent: *"Why has rework increased in our engineering organization?"*
- Explain that the AI requires **all** of the above metadata (Glossary, Ontology, Lineage, DQ) to reason safely and answer accurately.
