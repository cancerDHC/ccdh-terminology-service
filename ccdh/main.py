from ccdh.icdc import icdc_values
import csv


def main():
    rows = icdc_values()
    with open('icdc.tsv', 'w', newline='') as f_output:
        tsv_output = csv.writer(f_output, delimiter='\t')
        for row in rows:
            tsv_output.writerow(row)


if __name__ == '__main__':
    main()