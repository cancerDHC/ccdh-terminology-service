from rdflib import Namespace
from rdflib.namespace import SKOS


# The following namespaces can be imported from rdflib.namespaces
# * RDF
# * RDFS
# * OWL
# * XSD
# * FOAF
# * SKOS
# * DOAP
# * DC
# * DCTERMS
# * VOID

NCIT = Namespace('http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#')
CCDH = Namespace('https://ccdh.cancer.gov/')
GDC = Namespace('https://gdc.cancer.gov/')
PDC = Namespace('https://gdc.cancer.gov/')
HTAN = Namespace('https://humantumoratlas.org/')
ISO_11179 = Namespace('http://www.iso.org/11179/')


# Used by prefixcommons functions
NAMESPACES = [{
    'SKOS': SKOS,
    'NCIT': NCIT,
    'CCDH': CCDH,
    'GDC': GDC,
    'PDC': PDC,
    'HTAN': HTAN,
    'ISO-11179': ISO_11179,
}]

