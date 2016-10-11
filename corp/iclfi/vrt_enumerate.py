#! /usr/bin/env python
# -*- coding: utf-8 -*-

import io
import sys
import re

def open_input():
    f = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    remove_sents(f)
    
def remove_sents(ifile):
    concatenated = '<BREAK>'.join(ifile)
    c = re.sub('\n', '', concatenated)
    c = re.sub('(<BREAK>)+', '<BREAK>', c)
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
