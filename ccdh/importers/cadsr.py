from fhirclient import client
from fhirclient.models.valueset import ValueSet


settings = {
    'app_id': 'hot-ecosystem',
    'api_base': 'https://fhir.hotecosystem.org/terminology/cadsr/'
}
smart = client.FHIRClient(settings=settings)


def get_cadsr_values(cde_id):
    value_set = ValueSet.read(cde_id, smart.server)
    return value_set.expansion.contains

