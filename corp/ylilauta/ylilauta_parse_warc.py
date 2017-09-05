#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import io
import re
import vrt_tools

patt_title = r'.*<div class="op_post" id="no\d+"><div class="postsubject"><span>(.+?)</span></div>.*'

titles = {}
threads = {}

def parse_file(f):
    i = 0
    title = ''
    ''' tämä estää parsimisen muualla kuin avatuissa langoissa '''
    parsehtml = False
    parsecontent = False
    postx = {'time': '', 'id': '', 'title': '', 'section': '', 'content': ''}
    post = {'time': '', 'id': '', 'title': '', 'section': '', 'content': ''}

    for line in f:
        line = line.strip()
        if line.startswith('<div class="op_post"'):
            i += 1
            title = re.sub(patt_title, r'\1', line)
            
        if not title.startswith('<'):
            titles[i] = title
            parsehtml = True
        else:
            parsehtml = False

        if parsehtml:
            if line.startswith('<span class="posttime"'):
                print('@@NEXT@@')
                print('@@TITLE@@' + title)
                print('@@TIME@@' + re.sub('.*<span class="posttime">(.+?)</span>.*',
                                      r'\1', line))
            if re.match('.*<div class="post">.*', line):
                print('@@ID@@' + re.sub('.*<p id="post_(\d.+?)".*', r'\1', line))
                print('@@SECT@@' + re.sub('.*data-board="(.+?)".*', r'\1', line))
                parsecontent = True
    
            if parsecontent:
                print(re.sub('<.+?>', '', line))

            if re.match('.*</p>.*', line):
                parsecontent = False
 
        sys.stdin = sys.stdin.detach()
stdin = sys.stdin.read()
lines = stdin.decode("utf8", "ignore").splitlines()
parse_file(lines)
