from rdflib import Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD, DC, DCTERMS

NCIT = Namespace('http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#')
OBO = Namespace('http://purl.obolibrary.org/obo/')
HP = Namespace('http://purl.obolibrary.org/obo/HP_')
MONDO = Namespace('http://purl.obolibrary.org/obo/MONDO_')
NCIT_OBO = Namespace('http://purl.obolibrary.org/obo/NCIT_')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')

# Used by prefixcommons functions
NAMESPACES = {
    'DC': DC,
    'DCTERMS': DCTERMS,
    'HP': HP,
    'OBO': OBO,
    'OWL': OWL,
    'NCIT': NCIT,
    'RDF': RDF,
    'SKOS': SKOS,
    'MONDO': MONDO
}

