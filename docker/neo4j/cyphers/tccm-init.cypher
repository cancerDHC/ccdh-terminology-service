CALL n10s.nsprefixes.add("owl", "http://www.w3.org/2002/07/owl#");
CALL n10s.nsprefixes.add("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#");
CALL n10s.nsprefixes.add("rdfs", "http://www.w3.org/2000/01/rdf-schema#");
CALL n10s.nsprefixes.add("skos", "http://www.w3.org/2004/02/skos/core#");
CALL n10s.nsprefixes.add("xsd", "http://www.w3.org/2001/XMLSchema#");
CALL n10s.nsprefixes.add("dct", "http://purl.org/dc/terms/");
CALL n10s.nsprefixes.add("dc", "http://purl.org/dc/elements/1.1/");
CALL n10s.nsprefixes.add("obo", "http://purl.obolibrary.org/obo/");
CALL n10s.nsprefixes.add("termci", "https://hotecosystem.org/termci/");
CALL n10s.nsprefixes.add("sh", "http://www.w3.org/ns/shacl#");
CALL n10s.nsprefixes.add("linkml", "https://w3id.org/linkml/");

// Node
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#Concept', 'ConceptReference');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#ConceptScheme', 'ConceptSystem');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#CodeSet', 'CodeSet');

// Object Properties
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#broader', 'narrower_than');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#inScheme', 'defined_in');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#member', 'has_member');

// Data Type Properties
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#notation', 'code');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#prefLabel', 'designation');
call n10s.mapping.add('http://www.w3.org/2004/02/skos/core#definition', 'definition');
call n10s.mapping.add('http://www.w3.org/2000/01/rdf-schema#seeAlso', 'reference');
