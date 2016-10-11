#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re

def process(f, filename):
    o = False
    i = 1
    for line in f:
        prt = True
        line = line.strip('\n')
        if line.startswith('<sent'):
            if o:
                prt = False
            else:
                pass
            o = True
        if line.startswith('</sent'):
            if not o:
                prt = False
            else:
                pass
            o = False
        else:
            if prt:
                print(line)
        i+=1
            
def main(filename):
    file = open(filename, mode="r")
    process(file, filename)
    file.close()
    
main(sys.argv[1])
