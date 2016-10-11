#! /usr/bin/env python
# -*- coding: utf-8 -*-

import io
import sys
import re

repl = [
    ['\x85', '\u2026'],
    ['\x8a', '\u0160'],
    ['\x8e', '\u017D'],
    ['\x91', '\u2018'],
    ['\x92', '\u2019'],
    ['\x94', '&quot;'],
    ['\x96', '\u2013'],
    ['\x9a', '\u0161'],
    ['\x9e', '\u017e']]

def open_input():
    f = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    fix(f)
    
def fix(ifile):
    for line in ifile:
        line = line.strip('\n')
        if line.startswith('<text'):
            """
            #print(re.sub('tsekki|t.ekki', 'tšekki', line))
            line = re.sub('äidinkieli(: ?)?', '', line)
            line = re.sub(u'\u009a', 'š', line)
            line = re.sub(u'\u0160', 'Š', line)
            line = re.sub(u'\u010c', 'Č', line)
            line = re.sub(u'\u010d', 'č', line)
            line = re.sub(u'\u017d', 'Ž', line)
            line = re.sub(u'\u017c', 'ž', line)
            line = re.sub('tsekki', 'tšekki', line)
            print(line)
            """
            #line = re.sub('\x94', '&quot;', line)

            for r in repl:
                line = re.sub(r[0], r[1], line)

        print(line)
            
open_input()
