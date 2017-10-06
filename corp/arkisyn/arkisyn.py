#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Python 3
# asahala/finclarin

import sys
import re
import vrt_tools

class Converter:

    def __init__(self):
        self.title = "Toisin sanoen"
        self.output = []
        self.data = {}
        self.details = {}
        self.filename = ''
        self.urls = {}
                
    def readfile(self, filename):
        with open(filename, encoding='utf-8',
                  errors='ignore') as data:
            self.data = data.readlines()
        self.filename = filename
        return True
        
    def make_text_element(self):
        attrs = []
        for key in self.details.keys():
            attrs.append('{key}="{value}"'.format(
                key=key,
                value=self.details[key]))
        
        self.text_element = '<text ' + ' '.join(attrs) + '>'
        self.output.append(self.text_element)
        
    def process(self):
        """ Splits lines into tokens, sentences and paragraphs.
        OCR'd files usually have one paragraph per line """
        #self.parse_filename(category, writer)
        #self.make_text_element()
        print('<text filename="%s" datefrom="" dateto="">' %self.filename)
        first = True
        for line in self.data:
            line = line.strip()
            line = line.strip('■') # Removes strange boxes by Abbyy
            note = False
            if line.startswith('<t '):
                if first:
                    pass
                if not first:
                    print('</sentence>')

                if 'note' in line:
                    note = re.sub('.*<note>(.+?)</note>.*', r'\1', line)

                line = re.sub('>.+', '>', line)
                print(line.replace('<t', '<sentence'))

                if note:
                    print('&lt;note&gt;'+note+'&lt;/note&gt;' + '\t'*5)
                first = False
            if line.startswith('<w lem'):
                x = re.findall('="(.*?)"', line)
                w = re.sub('<.*?>', '', line)
                print(x[-1] + '\t' + '\t'.join(x[0:-1]) + '\t' + w)
            if line.startswith('<pa>'):
                print('&lt;pa&gt;' + '\t'*5)
            if line.startswith('<note'):
                print('\n' + re.sub('<(.+?)>' ,r'&lt;\1&gt;', line) + '\t'*5)
        print('</sentence>')
        print('</text>')
        
def main(argv):
    if len(sys.argv) < 2:
        print("Usage: arkisyn2vrt.py [inputfile]\n")
        sys.exit(1)
    else:
        filename = sys.argv[1]

    o = Converter()
    o.readfile(filename)
    o.process()

if __name__ == "__main__":
    main(sys.argv[1:])
