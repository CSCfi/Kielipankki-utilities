#! /usr/bin/env python
# -*- coding: utf-8 -*-
# asahala (FIN-CLARIN) 2015

import io
import sys
import re

"""
This script removes empty sentences and paragraphs and
enumerates them. This should be run on those vrt files made
with raw_to_vrt.py

Run only if the sentences and paragraphs do not have attributes
"""

def open_input():
    f = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    remove_sents(f)
    
def remove_sents(ifile):
    concatenated = '<BREAK>'.join(ifile)
    c = re.sub('\n', '', concatenated)

    #remove empty paragraph and sentence elements
    e_sents = re.findall('<sentence><BREAK></sentence><BREAK>', c)
    e_pars = re.findall('<paragraph></paragraph><BREAK>', c)
    c = re.sub('<sentence><BREAK></sentence><BREAK>', '', c)
    c = re.sub('<paragraph><BREAK></paragraph><BREAK>', '', c)

    #fix broken html-entities
    c = re.sub('(&#\d+?|&.+?)<BREAK>(;)', r'\1\2', c)
    split = c.split('<BREAK>')

    #enumerate paragraphs and sentences
    sents = 1
    paras = 1
    out = []
    for item in split:
        if item.startswith('<sent'):
            out.append('<sentence id="%s">' % str(sents))
            sents += 1
        elif item.startswith('<para'):
            out.append('<paragraph id="%s">' % str(paras))
            paras += 1
        elif item.startswith(('\t', ' ')):
            pass
        else:
            out.append(item)
    
    print('\n'.join(out))

open_input()
