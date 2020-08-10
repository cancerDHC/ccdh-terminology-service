from googleapiclient.discovery import build
from ccdh.gdrive.authorize import authorize
from typing import List
import pprint
import csv

pp = pprint.PrettyPrinter()


def cdm(sheet_id: str) -> List[List]:
    """
    Extract ADM models from Google Drive
    :param str sheet_id: The identifier of the google sheet
    :return: A list of adm values
    """
    rows = []

    service = build('sheets', 'v4', credentials=authorize())

    # Call the Sheets API
    result = service.spreadsheets().values().batchGet(spreadsheetId=sheet_id, ranges='Enumerated').execute()
    value_ranges = result.get('valueRanges', [])
    for values in value_ranges[0]['values']:
        if len(values) < 9:
            continue
        for prop in values[8].split('\n'):
            if len(prop.split('.')) != 3:
                continue
            row = values[:2]
            row.extend(prop.split('.'))
            rows.append(row)
    return rows


def main():
    rows = cdm('1oWS7cao-fgz2MKWtyr8h2dEL9unX__0bJrWKv6mQmM4')
    with open('output.tsv', 'w', newline='') as f_output:
        tsv_output = csv.writer(f_output, delimiter='\t')
        for row in rows:
            tsv_output.writerow(row)


if __name__ == '__main__':
    main()
