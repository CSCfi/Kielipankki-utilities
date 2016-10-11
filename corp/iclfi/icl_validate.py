#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re

def process(f, filename):
    for line in f:
        if line.endswith('>\n') and not line.startswith(('<', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0')):
            print(filename)
        elif not line.startswith(('<', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0')) and len(line) > 150:
            print(filename)
            
def main(filename):
    file = open(filename, mode="r")
    process(file, filename)
    file.close()
    
main(sys.argv[1])
