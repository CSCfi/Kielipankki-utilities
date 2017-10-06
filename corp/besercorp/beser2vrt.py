#! /usr/bin/env python
# -*- coding: utf-8 -*-
# asahala/finclarin

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

    def get_words(self, lines, sent_id):

        if sent_id.endswith('.1'):
            print('</paragraph>')
            print('<paragraph>')

        table = {0:[], 1:[], 2:[], 3:[]}

        """ pick words from each line """
        if len(lines) == 4:
            i = 0
            for line in lines:
                words = re.findall('<wrd>.+?</wrd>', line)
                for w in words:
                    table[i].append(re.sub('<.+?>', '', w))
                i += 1
        else:
            pass

        #for key in table.keys():
        #    print(len(table[key]))

        """ zip wordforms, lemmas, msds etc. """
        sents = zip(table[0], table[1], table[2], table[3])

        if len(lines) == 4:
            print('<sentence id="%s">' % sent_id)

        for sent in sents:
            s = list(sent)
            punct = ''
            if s[0].endswith(('.', ',', '?', '!')):
                punct = re.sub('.+?(\.+|,|\?|\!|\.)', r'\1', s[0])#s[0][-1]
                #x = s[0]
                pun = re.escape(punct)
                s[0] = re.sub(pun, '', s[0])#s[0][:-1])
                #print(x, s[0], punct)

            ##print('\t'.join(s))
            print(s[0])
            if punct:
                ##print('\t'.join([punct]*4))
                print(punct)
            #print('\t'.join(list(sent)))
            
        if len(lines) == 4:
            print('</sentence>')
            
    def process(self):
        print('<text title="Ансамбль" datefrom="20150101" dateto="20151231">')
        """ iterate lines of corpus """
        i = 0
        for line in self.data:
            line = line.strip('\n').lstrip()
            sent_id = re.sub('.+(ID.+?\d)".+', r'\1', line)
            elements = re.findall('<line>.+?</line>', line)
            self.get_words(elements, sent_id)
                
            #if i == 19:
            #    break
            i += 1

        print('</paragraph>')
        print('</text>')

            
def main(argv):
    if len(sys.argv) < 2:
        print("Usage: beser2vrt.py [inputfile]\n")
        sys.exit(1)
    else:
        filename = sys.argv[1]

    o = Converter()
    o.readfile(filename)
    o.process()

if __name__ == "__main__":
    main(sys.argv[1:])
