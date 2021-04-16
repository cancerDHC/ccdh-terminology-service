CALL n10s.graphconfig.init();

DROP CONSTRAINT n10s_unique_uri IF EXISTS;
CREATE CONSTRAINT n10s_unique_uri ON (r:Resource) ASSERT r.uri IS UNIQUE;

CALL n10s.graphconfig.init({
  handleVocabUris: 'MAP'
});

CALL n10s.nsprefixes.add(
    'neo4voc',
    'http://neo4j.org/vocab/sw#'
);

call n10s.nsprefixes.addFromText("
@prefix neo4voc: <http://neo4j.org/vocab/sw#> .
@prefix iso-11179: <http://www.iso.org/11179/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix ccdh: <http://ccdh.cancer.gov/ccdh/> .
@prefix gdc: <https://gdc.cancer.gov/> .
@prefix pdc: <https://pdc.cancer.gov/> .
@prefix htan: <https://humantumoratlas.org/> .
");

// Nodes
call n10s.mapping.add('http://www.iso.org/11179/DataElement', 'DataElement');
call n10s.mapping.add('http://www.iso.org/11179/DataElementConcept', 'DataElementConcept');
call n10s.mapping.add('http://www.iso.org/11179/ValueDomain', 'ValueDomain');
call n10s.mapping.add('http://www.iso.org/11179/PermissibleValue', 'PermissibleValue');
call n10s.mapping.add('http://www.iso.org/11179/ConceptualDomain', 'ConceptualDomain');
call n10s.mapping.add('http://www.iso.org/11179/ValueMeaning', 'ValueMeaning');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#Concept', 'Concept');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#Collection', 'CodeSet');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#ConceptSheme', 'ConceptScheme');
call n10s.mappinp.add('http://purl.org/sssom/type/TermMatch', 'Mapping');

// Object Properties
call n10s.mapping.add('http://www.iso.org/11179/dataElement.hasMeaning', 'HAS_MEANING');
call n10s.mapping.add('http://www.iso.org/11179/valueMeaning.hasRepresentation', 'HAS_REPRESENTATION');
call n10s.mapping.add('http://www.iso.org/11179/uses', 'USES');
call n10s.mapping.add('http://www.iso.org/11179/dataElementConcept.hasObjectClass', 'HAS_OBJECT_CLASS');
call n10s.mapping.add('http://www.iso.org/11179/dataElementConcept.hasProperty', 'HAS_PROPERTY');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#member', 'HAS_MEMBER');
call n10s.mapping.add('http://purl.org/sssom/meta/creator_id', 'CREATED_BY');

// Datatype Properties
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#definition', 'definition');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#prefLabel', 'pref_label');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#altLabel', 'alt_label');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#notation', 'notation');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#inScheme', 'in_scheme');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#note', 'note');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#changeNote', 'change_note');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#scopeNote', 'scope_note');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#historyNote', 'history_note');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#editorialNote', 'editorial_note');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#example', 'example');
call n10s.mapping.add('http://www.w3.org/'

call n10s.mapping.add('http://purl.org/sssom/type/MatchType', 'match_type');
call n10s.mapping.add('http://purl.org/sssom/meta/comment', 'comment');
call n10s.mapping.add('http://purl.org/sssom/meta/confidence', 'confidence');
call n10s.mapping.add('http://purl.org/sssom/meta/mapping_date', 'mapping_date');
call n10s.mapping.add('http://purl.org/sssom/meta/mapping_provider', 'mapping_provider');
call n10s.mapping.add('http://purl.org/sssom/meta/comment', 'comment');
call n10s.mapping.add('http://purl.org/sssom/meta/comment', 'comment');
call n10s.mapping.add('http://purl.org/sssom/meta/comment', 'comment');
call n10s.mapping.add('http://purl.org/sssom/meta/comment', 'comment');

call n10s.mapping.add('http://ccdh.cancer.gov/ccdh/system', 'system');
call n10s.mapping.add('http://ccdh.cancer.gov/ccdh/entity', 'entity');
call n10s.mapping.add('http://ccdh.cancer.gov/ccdh/attribute', 'attribute');


// INDEXES
DROP INDEX data_element_entity_idx IF EXISTS;
CREATE INDEX data_element_entity_idx FOR (n:DataElement) ON (n.entity);

DROP INDEX data_element_attribute_idx IF EXISTS;
CREATE INDEX data_element_attribute_idx FOR (n:DataElement) ON (n.attribute);

DROP INDEX data_element_context_idx IF EXISTS;
CREATE INDEX data_element_context_idx FOR (n:DataElement) ON (n.context);

DROP INDEX data_element_concept_context_idx IF EXISTS;
CREATE INDEX data_element_concept_context_idx FOR (n:DataElementConcept) ON (n.context);

DROP INDEX data_element_concept_objectClass_idx IF EXISTS;
CREATE INDEX data_element_concept_objectClass_idx FOR (n:DataElementConcept) ON (n.objectClass);

DROP INDEX data_element_concept_property_idx IF EXISTS;
CREATE INDEX data_element_concept_property_idx FOR (n:DataElementConcept) ON (n.property);

DROP INDEX permissible_value_prefLabel_idx IF EXISTS;
CREATE INDEX permissible_value_prefLabel_idx FOR (n:PermissibleValue) ON (n.prefLabel);
