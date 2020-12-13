from rdflib import Namespace
from rdflib.namespace import SKOS, RDF, RDFS, OWL, XSD, DC, DCTERMS

NCIT = Namespace('http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#')
OBO = Namespace('http://purl.obolibrary.org/obo/')
HP = Namespace('http://purl.obolibrary.org/obo/HP_')

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
}

