# Neo4J Schema

The backend of the database is a Neo4J graph database. The conceptual graph model in the database is based on the 
ISO/IEC 11179-3, a metadata registries metamodel of the International Organization 
for Standardization (ISO)’s technical committee on data management and interchange.

![value-mapping-graph-model](./images/value-mappings-graph-model.png)
Figure: Conceptual models (ovals) of the data in the CCDH Terminology Service and their sources (the shaded boxes).

The Cypher language is used to define [the schema](../docker/neo4j/cyphers), and the schema is loaded into the docker container automatically when
the container is started. 

More content to be added ...