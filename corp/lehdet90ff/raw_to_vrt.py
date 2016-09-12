#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Python 3

import sys
import re
import vrt_tools

class Converter:

    def __init__(self):
        """ Type magazine's full name here """
        self.title = "Magazine name"
        self.output = []
        self.data = {}
        self.details = {}
        self.filename = ''
        self.urls = {}

    def read_meta(self):
        with open('read.me', encoding='utf-8') as meta:
            metadata = meta.readlines()

        for l in metadata:
            l = l.strip('\n')
            line = l.split('\t')
            if len(l) > 3:
                self.urls[re.sub('pdf', 'txt', line[0])] = line[1]
                
    def readfile(self, filename):
        with open(filename, encoding='utf-8',
                  errors='ignore') as data:
            self.data = data.readlines()
        self.filename = filename
        return True
        
    def parse_filename(self):
        url_available = False
        """ Uncomment this if the Magazine has a meta-data file.
        this file is named read.me or logfile.txt (if latter,
        rename it into read.me """
        #url_available = self.read_meta()

        """ Modify regex to match the filename. """
        if re.match('.*\d[-_]\d\d\d\d.*', self.filename):
            dateinfo = re.sub('.*(\d[-_]\d\d\d\d).*',
                          r'\1', self.filename).replace('-', '_')            
            x = dateinfo.split('_')
            
        self.details['datefrom'] = x[1] + '0101'
        self.details['dateto'] = x[1] + '1231'
        self.details['title'] = self.title
        self.details['year'] = x[1]
        self.details['issue'] = x[0] + '/' + x[1]

        if url_available:
            self.details['url'] = self.urls[self.filename]
        
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
        self.parse_filename()
        self.make_text_element()
        for line in self.data:
            line = line.strip()
            line = line.strip('■') # Removes strange boxes by Abbyy
            text_content = re.sub('<.*?>', '', line)
            line = '<paragraph>\n' +\
                   vrt_tools.tokenize(line, 128) +\
                   '\n</paragraph>'
            self.output.append(line)
        self.output.append('</text>')
        print('\n'.join(self.output))
        
def main(argv):
    if len(sys.argv) < 2:
        print("Usage: raw_to_vrt.py [inputfile]\n")
        sys.exit(1)
    else:
        filename = sys.argv[1]

    o = Converter()
    o.readfile(filename)
    o.process()

if __name__ == "__main__":
    main(sys.argv[1:])
