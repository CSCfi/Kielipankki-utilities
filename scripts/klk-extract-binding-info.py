#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Extract information for the page image links of the KLK corpus from
# a CSV file provided by the Finnish National Library; output as TSV


import sys
import csv


def extract_binding_info(fname):

    def make_issue_name(zippath):
        return zippath.split('/')[-1].split('.')[0]

    def make_issue_type(url):
        return url.split('/')[3]

    with open(fname) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            issue_name = make_issue_name(row['METSZIP'])
            issue_id = row['NIDE_ID']
            issue_type = make_issue_type(row['DIGI_PDF_URL'])
            sys.stdout.write('\t'.join([issue_name, issue_id, issue_type])
                             + '\n')


def main():
    extract_binding_info(sys.argv[1])


if __name__ == '__main__':
    main()
