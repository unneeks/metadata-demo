// Neo4j Load Script for Employee Delivery Data Product

// Create constraints
CREATE CONSTRAINT IF NOT EXISTS FOR (e:Employee) REQUIRE e.node_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (t:Team) REQUIRE t.node_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (d:Department) REQUIRE d.node_id IS UNIQUE;

// Load Nodes
LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
CALL apoc.create.node([row.node_type], {
    node_id: row.node_id,
    name: row.name,
    description: coalesce(row.description, ""),
    domain: coalesce(row.domain, ""),
    owner: coalesce(row.owner, "")
}) YIELD node
RETURN count(*);

// Load Relationships
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
MATCH (source {node_id: row.subject})
MATCH (target {node_id: row.object})
CALL apoc.create.relationship(source, row.relationship_type, {
    relationship_id: row.relationship_id
}, target) YIELD rel
RETURN count(*);
