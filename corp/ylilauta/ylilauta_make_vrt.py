#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import io
import re
import vrt_tools

titles = {}
threads = {}

def clean(string):
    string = string.strip('\n').strip()
    string = re.sub('(\\\\|\/|<|>|\"|\'|\+)', '', string)
    return string

def parse_file(f):
    content = ''
    for line in f:
        if line.startswith('@@TITLE@@'):
            title = re.sub('@@TITLE@@', '', line)
        if line.startswith('@@TIME@@'):
            time = re.sub('@@TIME@@', '', line)
            date = time.split(' ')[0]
            clock = time.split(' ')[1]
            ymd = date.split('.')
            datefrom = ymd[2] + ymd[1] + ymd[0]
        if line.startswith('@@ID@@'):
            id_ = re.sub('@@ID@@', '', line)
        if line.startswith('@@SECT@@'):
            sect = re.sub('@@SECT@@', '', line)
        if not line.startswith('@@'):
            content += line + '\n'
        if line.startswith('@@NEXT@@'):
            print('<TEXT title="{title}" datefrom="{datefrom}" dateto="{datefrom}" date="{date}" clock="{clock}" id="{id_}" sec="{sect}">'.format(
                    title=clean(title),
                    datefrom=datefrom,
                    date=date,
                    clock=clock,
                    id_=id_,
                    sect=sect))
            print('<paragraph>')
            print(vrt_tools.tokenize(content, 128))
            print('</paragraph>')
            print('</text>')
            content = ''
        else:
            pass
            
sys.stdin = sys.stdin.detach()
stdin = sys.stdin.read()
lines = stdin.decode("utf8", "ignore").splitlines()
parse_file(lines)
