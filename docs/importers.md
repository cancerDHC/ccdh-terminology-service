# Importers

The importers transform the data from different sources and imported them into the Neo4J graph database in the
backend of the terminology service. 

Here are the list of data sources and how they're transformed. 

## GDC and PDC data dictionary

The GDC and PDC data dictionaries are included in the ccdh-terminology-service GitHub repo as submodules. The 
data dictionaries are parsed and transformed into the Graph model nodes. Only attributes have enumerated values
are imported. 

## NCI thesaurus 

NCIt release is downloaded and transformed into a simple Turtle RDF representation based on the [TCCM model spec](https://github.com/HOT-Ecosystem/tccm-model/) using 
[a script in the TCCM-API](https://github.com/HOT-Ecosystem/tccm-api/blob/master/tccm_loader/ncit.py). The turtle file
is imported into Neo4J using [the neosemantics RDF & Semantics toolkit](https://neo4j.com/labs/neosemantics/).  

## GDC-NCIt mappings

The GDC-NCIt mappings are downloaded from [the Mappings page of the NCI Term browser](https://ncit.nci.nih.gov/ncitbrowser/pages/mapping_search.jsf?nav_type=mappings&b=0&m=0). 
It is parsed and imported as Mapping nodes with edges connecting the terms and ConceptReferences(NCIt concept codes) in the Neo4J database.

## caDSR

caDSR data are downloaded in an experimental RDF format created by NCI. The RDF file is loaded into a GraphDB triple
store. [An FHIR terminology service API](https://github.com/HOT-Ecosystem/cadsr-on-fhir) was created to serve the value domains of caDSR CDEs as value sets.

The importer uses the FHIR api to pull the mappings and permissible value meanings of the enumerated values in the GDC/PDC models,
based on the caDSR CDE identifiers in the GDC and PDC data dictionaries. The value meanings are used to enrich
the metadata about the enumerated values. 

## CRDC-H 

The YAML file of the CRDC-H model is retrieved directly from the [ccdhmodel GitHub repo](https://github.com/cancerDHC/ccdhmodel). It is parsed using the
LinkML python package. The attributes of type enumerations are retrieved and imported into to the Neo4J database. 