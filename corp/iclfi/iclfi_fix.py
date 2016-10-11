#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re


class Converter:

    def __init__(self):
        self.title = ""
        self.output = []
        self.data = {}
        self.daatta = {}
        self.details = {}
        self.filename = ''
        
    def readfile(self, filename):
        with open(filename, encoding='utf-8') as data:
            self.data = data.readlines()
        self.filename = filename
        
    def readfile2(self, fname):
               
        with open('meta/'+fname, encoding='iso-8859-1') as data:
            self.daatta = data.readlines()
        
    def make_text_element(self):
        attrs = []
        for key in self.details.keys():
            attrs.append('{key}="{value}"'.format(
                key=key,
                value=self.details[key]))        
        self.text_element = '<text ' + ' '.join(attrs) + '>'
        self.output.append(self.text_element)

    def parse_meta(self):
        creator = ""
        title = ""
        datefrom = ''
        dateto = ''
        for line in self.daatta:
            line = line.strip('\n')
            line = line.lstrip()
            if 'coverage' in line:
                date = re.sub('<.+?>', '', line)
                '''
                x = date.split('.')
                dd = x[0].zfill(2)
                mm = x[1].zfill(2)
                yyyy = x[2]
                datefrom = yyyy+mm+dd
                '''
                datefrom = date + '0101'
                dateto = date + '1231'
        return 'datefrom="{df}" dateto="{dt}"'.format(df=datefrom, dt=dateto)
                
    def process(self):
        for line in self.data:
            l = line.strip('\n')
            if line.startswith('<'):
                data = re.sub('<|>', '', line)
                if data.count(':') > 2:
                    print(self.filename)
                    print(l)

        
def main(argv):
    if len(sys.argv) < 2:
        print("Usage: ocr-fixer.py [inputfile]\n")
        sys.exit(1)
    else:
        filename = sys.argv[1]

    o = Converter()
    o.readfile(filename)
    o.process()

if __name__ == "__main__":
    main(sys.argv[1:])
