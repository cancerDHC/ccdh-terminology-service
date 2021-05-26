from rdflib import Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD, DC, DCTERMS

NCIT = Namespace('http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#')
OBO = Namespace('http://purl.obolibrary.org/obo/')
HP = Namespace('http://purl.obolibrary.org/obo/HP_')
MONDO = Namespace('http://purl.obolibrary.org/obo/MONDO_')
NCIT_OBO = Namespace('http://purl.obolibrary.org/obo/NCIT_')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')

# CCDH Local
CCDH = Namespace('https://ccdh.cancer.gov/')
GDC = Namespace('https://gdc.cancer.gov/')
PDC = Namespace('https://gdc.cancer.gov/')
HTAN = Namespace('https://humantumoratlas.org/')
ISO_11179 = Namespace('http://www.iso.org/11179/')


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
    'MONDO': MONDO,

    # CCDH Local
    'CCDH': CCDH,
    'GDC': GDC,
    'PDC': PDC,
    'HTAN': HTAN,
    'ISO-11179': ISO_11179,
}

