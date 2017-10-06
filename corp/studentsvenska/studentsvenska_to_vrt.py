#! /usr/bin/env python
# -*- coding: utf-8 -*-
# asahala / finclarin
# input must be converted into utf-u!

import sys
import re

class Studentsvenska_to_VRT:

    def __init__(self):
        self.output = []
        self.data = {}
        self.initvars()
        
    def initvars(self):
        self.metadict = {'<T': 'textnumber',
                         '<Ä': 'subject',
                         '<S': 'schoolnumber',
                         '<K': 'gender',
                         '<A': 'gradeword',
                         '<B': 'gradeexam',
                         '<L': 'gradeteacher',
                         '<G': 'gradegrammar',
                         '<F': 'errorother',
                         '<O': 'errorwordorder'}
        self.metavals = {}
        self.classes = {'c': '', 'k': '', 'm': '', 'i': '',
                        'a': '', 'p': '', 'h': '', 'e': '',
                        'j': '', 'c': '', 'e': '', 'i': '',
                        'k': '', 'i': '', 's': ''}

    def readfile(self, filename):
        with open(filename, encoding='utf-8') as data:
            self.data = data.readlines()

    def process(self):
        sent_id = 1
        firstsent = True
        sent_open = False
        for line in self.data:
            line = line.lstrip()
            line = line.strip('\n')
            
            if line.startswith(tuple(self.metadict.keys())):
                value = re.sub('(<.?| )', r'', line)
                key = line[0:2]
                self.metavals[key] = value
            if line.startswith('<O'):
                attrs = [self.metadict[x] + '="%s"' %self.metavals[x] for x\
                         in self.metadict.keys()]
                if not firstsent:
                    print('</text>')
                attrs.append('datefrom="19790101"')
                attrs.append('dateto="19801231"')
                print('<text %s>' % ' '.join(attrs))
                firstsent = False
            if line.startswith('_'):
                key = line[1]
                if 'slut' not in line:
                    value = re.sub('_', '', line)
                    self.classes[key] = value
                else:
                    self.classes[key] = ''                    
            if line == "''''":
                if sent_open:
                    print('</sentence>')
                print('<sentence id="%s">' %\
                      (sent_id))
                sent_open = True
                sent_id += 1
            #if line == "````":
            #    print('</sentence>')
            if re.match('.*\d\d\d\d\d.+', line):
                word_type = line[0:5]
            else:
                if not line.startswith(('<', '_', "'", ';', '+', '#', '=', '`', '~', 'QQQ')):
                    wattrs = [self.classes[x] for x in self.classes.keys()]
                    word_attrs = '|'.join(sorted(filter(None, wattrs)))
                    words = re.sub(' +', '\t', line).split('\t')
                    if len(words) < 2:
                        words.append('')
                    if words[0].endswith(('?', '!', ',', '.', ':', ';')):
                        punct = words[0][-1]
                        words[0] = words[0][0:-1]
                    else:
                        punct = ''
                    if words[0]:
                        print(str(words[0]).lower() + '\t' + str(words[1]).lower() + '\t' + word_type + '\t' + word_attrs)
                        if punct:
                            print(punct + '\t' + punct + '\t\t' + word_attrs)
        print('</sentence>')
        print('</text>')
                
                

        
def main(argv):
    if len(sys.argv) < 2:
        print("Usage: studentsvenska_to_vrt.py [inputfile]\n")
        sys.exit(1)
    else:
        filename = sys.argv[1]

    o = Studentsvenska_to_VRT()
    o.readfile(filename)
    o.process()

if __name__ == "__main__":
    main(sys.argv[1:])
