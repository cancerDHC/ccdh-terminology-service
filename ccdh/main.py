from ccdh.icdc import icdc_values
import csv


def main():
    rows = icdc_values()
    with open('valuesets_2020-08-16.tsv', 'w', newline='') as f_output:
        tsv_output = csv.writer(f_output, delimiter='\t')
        tsv_output.writerow(['CDM.Entity', 'CDM Attribute', 'Source', 'Source Entity', 'Source Attribute', 'Value'])
        for row in rows:
            tsv_output.writerow(row)


if __name__ == '__main__':
    main()