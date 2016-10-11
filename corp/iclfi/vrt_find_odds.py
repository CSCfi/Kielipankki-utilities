#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re

def process(f, filename):
    for line in f:
        line = line.split(':')
        if not int(line[1]) % 2 == 0:
            print('rm %s&' % line[0]) 
            
    
def main(filename):
    file = open(filename, mode="r")
    process(file, filename)
    file.close()
    
main(sys.argv[1])
