#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Python 3
# asahala/fin-clarin

# Convert E-thesis into vrt


import sys
import re
import vrt_tools
import lang_recognizer

class Converter:

    def __init__(self):
        self.title = ""
        self.output = []
        self.data = {}
        self.details = {}
        self.filename = ''
        self.metadata = {}

    def normalize_attrnames(self, x):
        x = x.replace('citation', '')
        x = x.replace('authors=', 'author=')
        x = x.replace('pdfurl', 'pdfurl')
        x = x.replace('abstracthtmlurl', 'url')
        x = x.replace('language=""', 'lang="sv"')
        x = x.replace('language=', 'lang=')
        x = x.replace('faculty=""', 'faculty=""')
        d = re.sub('.*date(from|to)="(.+?)".*', r'\2', x)
        if len(d) != 8:
            x = re.sub('date(from|to)=".+?"', r'date\1=""', x)
        return(x)
        
    def read_meta(self):
        with open('logfile.txt', encoding='utf-8') as meta:
            metadata = meta.readlines()

        for l in metadata:
            l = l.strip('\n')
            line = l.split('|||')
            self.metadata[re.sub('pdf', 'txt', line[0])] = self.normalize_attrnames(line[1])
                
    def readfile(self, filename):
        with open(filename, encoding='utf-8',
                  errors='ignore') as data:
            self.data = data.readlines()
        self.filename = filename
        return True
        
    def parse_filename(self):
        self.read_meta()
        """ Modify regex to match the filename. """
        
    def make_text_element(self):
        attrs = []
        for key in self.details.keys():
            attrs.append('{key}="{value}"'.format(
                key=key,
                value=self.details[key]))
        
        self.text_element = '<text ' + ' '.join(attrs) + '>'
        self.output.append(self.text_element)
        
    def process(self):
        do = False
        """ Splits lines into tokens, sentences and paragraphs.
        OCR'd files usually have one paragraph per line """
        self.parse_filename()
        l = lang_recognizer.recognize(' '.join(self.data))

        x = open('lang.text', 'a')
        x.writelines(l + '\t' + self.filename + '\n')
        
        if l == 'sv':
            do = True
        else:
            do = False

        if do:
            print(self.metadata[self.filename])
            for line in self.data:
                line = line.strip()
                line = line.strip('■') # Removes strange boxes by Abbyy
                text_content = re.sub('<.*?>', '', line)
                dada = vrt_tools.tokenize(line, 128)
                if len(dada) > 4:
                    line = '<paragraph>\n' +\
                           dada +\
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
