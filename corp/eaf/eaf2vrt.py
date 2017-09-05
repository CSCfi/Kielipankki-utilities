#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Python 3

import sys
import re
import vrt_tools

class Converter:

    def __init__(self):
        self.output = []
        self.data = {}
        self.details = {}
        self.filename = ''
        self.timeslot_ids = {}
        self.urls = {}

    def parse_time(self, time):
        t = time.split(' ')
        y, m, d = t[0].split('-')
        return t[0].replace('-', ''), d + '.' + m + '.' + y, t[1]
        
    def read_meta(self, filename):
        try:
            with open(filename, encoding='utf-8', errors='ignore') as meta:
                metadata = meta.readlines()
        except:
            with open(filename, encoding='iso-8859-1', errors='ignore') as meta:
                metadata = meta.readlines()                            
            
        for l in metadata:
            l = l.strip('\n')
            line = l.split(': ')
            self.details[line[0].lower()] = line[1]

        df, y, t = self.parse_time(self.details['published'])
        self.details['datefrom'] = df
        self.details['dateto'] = df
        self.details['date'] = y
        self.details['time'] = t
        self.details['filename'] = filename.replace('.metadata', '.eaf')
        
        
    def readfile(self, filename):
        with open(filename, encoding='utf-8',
                  errors='ignore') as data:
            self.data = data.readlines()
        self.filename = filename
        return True
        
    def parse_filename(self):
        pass
    
    def make_text_element(self):
        attrs = []
        for key in self.details.keys():
            attrs.append('{key}="{value}"'.format(
                key=key,
                value=self.details[key]))
        
        self.text_element = '<text ' + ' '.join(attrs) + '>'
        self.output.append(self.text_element)
        
    def process(self):
        def get_attrs(d):
            return re.findall('"(.+?)"', d)
            
        self.read_meta(self.filename.replace('eaf', 'metadata'))
        #self.parse_filename(category, writer)
        self.make_text_element()
        #print(self.output)
        for line in self.data:
            line = line.strip()
            if line.startswith('<TIME_SLOT'):
                d = get_attrs(line)
                self.timeslot_ids[d[0]] = d[1]
            if line.startswith('<TIER'):
                ll = ''
                replace = True
                for c in line:
                    if c == '"' and replace:
                        replace = False
                    elif c == '"' and not replace:
                        replace = True

                    if replace and c != '_':
                        ll += c.lower()
                    if not replace and c != '_':
                        ll += c

                self.output.append(ll.replace('<tier', '<paragraph'))
                self.output.append('<sentence>')
            if line.startswith('<ALIGNABLE_ANNOTATION'):
                d = get_attrs(line)
                slots = []
                for item in d:
                    if item in self.timeslot_ids.keys():
                        slots.append(self.timeslot_ids[item])
                attrs = '\t'.join(d + slots)
                
            if line.startswith('<ANNOTATION_VALUE'):
                text = re.sub('<.+?>', '', line)
                if text == '.':
                    self.output.append(text + '\t' + attrs)
                    #self.output.append('</sentence>')
                    #self.output.append('<sentence>')
                else:
                    self.output.append(text + '\t' + attrs)
            if line.startswith('</TIER'):
                self.output.append('</paragraph>')

        #self.output.append('</sentence>')
        #self.output.append('</paragraph>')
        self.output.append('</text>')

        j = 0
        for x in self.output:
            if x.startswith('.'):
                print(x)
                print('</sentence>')
                if not self.output[j+1].startswith('<'):
                    print('<sentence>')
            else:
                print(x)
                    
            j += 1   
        #print('\n'.join(self.output))
                
                
def main(argv):
    if len(sys.argv) < 2:
        print("Usage: eaf2vrt.py [inputfile]\n")
        sys.exit(1)
    else:
        filename = sys.argv[1]

    o = Converter()
    o.readfile(filename)
    o.process()

if __name__ == "__main__":
    main(sys.argv[1:])
