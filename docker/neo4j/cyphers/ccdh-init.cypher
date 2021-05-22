CALL n10s.nsprefixes.add("neo4voc", "http://neo4j.org/vocab/sw#");
CALL n10s.nsprefixes.add("sssom-type", "http://purl.org/sssom/type/");
CALL n10s.nsprefixes.add("sssom-meta", "http://purl.org/sssom/meta/");
CALL n10s.nsprefixes.add("iso-11179", "http://www.iso.org/11179/");
CALL n10s.nsprefixes.add("owl", "http://www.w3.org/2002/07/owl#");
CALL n10s.nsprefixes.add("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#");
CALL n10s.nsprefixes.add("rdfs", "http://www.w3.org/2000/01/rdf-schema#");
CALL n10s.nsprefixes.add("skos", "http://www.w3.org/2004/02/skos/core#");
CALL n10s.nsprefixes.add("xsd", "http://www.w3.org/2001/XMLSchema#");
CALL n10s.nsprefixes.add("ccdh", "https://ccdh.cancer.gov/");
CALL n10s.nsprefixes.add("gdc", "https://gdc.cancer.gov/");
CALL n10s.nsprefixes.add("pdc", "https://pdc.cancer.gov/");

// Nodes
call n10s.mapping.add('http://www.iso.org/11179/DataElement', 'NodeAttribute');
call n10s.mapping.add('http://www.iso.org/11179/DataElementConcept', 'HarmonizedAttribute');
call n10s.mapping.add('http://www.iso.org/11179/ValueDomain', 'Enumeration');
call n10s.mapping.add('http://www.iso.org/11179/PermissibleValue', 'PermissibleValue');
call n10s.mapping.add('http://purl.org/sssom/type/TermMatch', 'Mapping');

// Object Properties
call n10s.mapping.add('http://www.iso.org/11179/dataElement.hasMeaning', 'HAS_MEANING');
call n10s.mapping.add('http://www.iso.org/11179/valueMeaning.hasRepresentation', 'HAS_REPRESENTATION');
call n10s.mapping.add('http://www.iso.org/11179/uses', 'USES');
call n10s.mapping.add('http://www.iso.org/11179/dataElementConcept.hasObjectClass', 'HAS_OBJECT_CLASS');
call n10s.mapping.add('http://www.iso.org/11179/dataElementConcept.hasProperty', 'HAS_PROPERTY');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#member', 'HAS_MEMBER');
call n10s.mapping.add('http://purl.org/sssom/meta/creator_id', 'CREATED_BY');

// Datatype Properties
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#note', 'note');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#changeNote', 'change_note');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#scopeNote', 'scope_note');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#historyNote', 'history_note');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#editorialNote', 'editorial_note');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#example', 'example');

call n10s.mapping.add('http://purl.org/sssom/type/MatchType', 'match_type');
call n10s.mapping.add('http://purl.org/sssom/meta/comment', 'comment');
call n10s.mapping.add('http://purl.org/sssom/meta/confidence', 'confidence');
call n10s.mapping.add('http://purl.org/sssom/meta/mapping_date', 'mapping_date');
call n10s.mapping.add('http://purl.org/sssom/meta/mapping_provider', 'mapping_provider');
call n10s.mapping.add('http://purl.org/sssom/meta/comment', 'comment');

call n10s.mapping.add('https://ccdh.cancer.gov/system', 'system');
call n10s.mapping.add('https://ccdh.cancer.gov/entity', 'entity');
call n10s.mapping.add('https://ccdh.cancer.gov/attribute', 'attribute');


// INDEXES
DROP INDEX node_entity_idx IF EXISTS;
CREATE INDEX node_entity_idx FOR (n:NodeAttribute) ON (n.entity);

DROP INDEX node_attribute_idx IF EXISTS;
CREATE INDEX node_attribute_idx FOR (n:NodeAttribute) ON (n.attribute);

DROP INDEX node_system_idx IF EXISTS;
CREATE INDEX node_system_idx FOR (n:NodeAttribute) ON (n.system);

DROP INDEX harmonizned_system_idx IF EXISTS;
CREATE INDEX harmonizned_system_idx FOR (n:HarmonizedAttribute) ON (n.system);

DROP INDEX harmonizned_entity_idx IF EXISTS;
CREATE INDEX harmonizned_entity_idx FOR (n:HarmoniznedAttribute) ON (n.entity);

DROP INDEX harmonized_attribute_idx IF EXISTS;
CREATE INDEX harmonized_attribute_idx FOR (n:HarmoniznedAttribute) ON (n.attribute);

DROP INDEX permissible_value_pref_label_idx IF EXISTS;
CREATE INDEX permissible_value_pref_label_idx FOR (n:PermissibleValue) ON (n.pref_label);
