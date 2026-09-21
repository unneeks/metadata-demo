# Ontology & Knowledge Graph

The Data Fabric uses a semantic knowledge graph to map concepts.

## Relationships
```
Employee BELONGS_TO Team
Team PART_OF Department
Department PART_OF Division

Employee PERFORMS WorkItem
WorkItem MAY_HAVE Rework
WorkItem MAY_RESULT_IN Change
Change MAY_CAUSE Incident

Employee IDENTIFIED_BY SourceSystemIdentity

DataProduct CONTAINS DataElement
DataElement REPRESENTS BusinessTerm
DataQualityRule VALIDATES DataElement
```
