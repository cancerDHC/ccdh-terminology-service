from ccdh.cdm import cdm_dictionary_sheet
from ccdh.htan import htan_values
from ccdh.icdc import icdc_values
import csv
from fhirclient import client
from fhirclient.models.valueset import ValueSet
from ccdh.gdc import gdc_values
from ccdh.pdc import pdc_values
from ccdh.icdc import icdc_values
from pathlib import Path
from datetime import date


settings = {
    'app_id': 'hot-ecosystem',
    'api_base': 'https://fhir.hotecosystem.org/terminology/cadsr/'
}
smart = client.FHIRClient(settings=settings)


def main():
    rows = cdm_dictionary_sheet('1oWS7cao-fgz2MKWtyr8h2dEL9unX__0bJrWKv6mQmM4')
    rows = htan_values(pdc_values(gdc_values(rows)))
    cde_id = None
    values = []
    output = Path(__file__).parent.parent.joinpath(f'output/valuesets_{date.today().strftime("%m-%d-%y")}.tsv')
    with open(output, 'w', newline='') as f_output:
        tsv_output = csv.writer(f_output, delimiter='\t')
        # tsv_output.writerow(['CDM.Entity.Attribute', 'Source.Entity.Attribute', 'Value',
        #                      'NCIt Concept Code', 'NCIt Preferred Name', 'CDE ID (caDSR)'])
        tsv_output.writerow(['subject_match_field', 'subject_label', 'predicate_id', 'object_match_field', 'object_id',
                             'object_label', 'see_also'])
        for row in rows:
            if row[8]:
                if row[8] != cde_id:
                    cde_id = row[8]
                    values = get_ncit_code(cde_id)
                # for value in values:
                #     if value.code.lower() == row[5].lower():
                #         if value.extension:
                #             for ext in value.extension:
                #                 if ext.url != 'http://cbiit.nci.nih.gov/caDSR#main_concept':
                #                     continue
                #                 row.append(ext.valueCodeableConcept.coding[0].code)
                #                 row.append(ext.valueCodeableConcept.coding[0].display)
            tsv_output.writerow(row)


def get_ncit_code(cde_id):
    value_set = ValueSet.read(cde_id, smart.server)
    return value_set.expansion.contains


if __name__ == '__main__':
    main()
