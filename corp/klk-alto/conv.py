#!/usr/bin/env python3
# Convert Alto XML into VRT

import re
from sys import stderr
import xml.etree.ElementTree as ET
from vrt_util import *
from string import punctuation

page_tag   = 'Page'
block_tag  = 'TextBlock'
line_tag   = 'TextLine'
string_tag = 'String'

paragraph_id = 0
sentence_id  = 0

ns = {}

def get_namespaces(xml_file):
    ns = dict([ x[1] for x in ET.iterparse(xml_file, events=['start-ns']) ])
    return ns


# Retrieve DD.MM.YYYY date from mets, return YYYYMMDD
def get_date(mets_dict={}):
    if mets_dict == {}:
        return date
    return ''.join([ s.zfill(2) for s in mets['issue_date'].split('.')[::-1] ])


def align_data(element):

    string_data = get_string_data(element)

    text = ' '.join([ s for ( s, atts ) in string_data ])
    sents = tokenize(text)
    
    aligned_para = []
    
    for sent in sents:
        aligned_sent = []
        for token in sent:
            ( string, atts ) = string_data.pop(0)
            string = string.strip()
            while string == '':
                ( string, atts ) = string_data.pop(0)
                string = string.strip()
            if len(token) > len(string):
                stderr.write('WARNING: mismatch between token "%s" and original string(s)!\n' % token)
                stderr.write('%s vs. "%s"\n' % ( sent, string))
                while token.startswith(string):
                    stderr.write('Using %s as token instead...\n' % string) 
                    token = token[len(string):].strip()
                    aligned_sent.append((string, atts))
                    ( string, atts ) = string_data.pop(0)
                    string = string.strip()
            if string.startswith(token):
                aligned_sent.append((token, atts))
                string = string[len(token):].strip()
                if string != '':
                    string_data = [ ( string, atts ) ] + string_data
            else:
                stderr.write('ERROR: unable to find token "%s" in text string "%s"!\n' % (token, string))
                exit(0)
        aligned_para.append(aligned_sent)

    return aligned_para


def get_string_data(block_elem):
    
    pairs = []
    for string_elem in block_elem.findall('.//'+string_tag, ns):
        atts = string_elem.attrib
        if 'SUBS_CONTENT' in atts:
            if atts['SUBS_TYPE'] == 'HypPart1':
                pairs.append(( atts['SUBS_CONTENT'], atts ))
        else:
            pairs.append(( atts['CONTENT'], atts))
    return pairs


def sentence(sent):

    global sentence_id

    string = ''
    for (token, atts) in sent:
        s_id = atts['ID']
        cont = atts['CONTENT']
        vpos = atts['VPOS']
        hpos = atts['HPOS']
        string += '%s\t%s\t%s\t%s\n' % (token, s_id, cont, vpos)
    sentence_atts = { 'id' : sentence_id, }
    sentence_id += 1

    # Escape &, < and >
    string = string.replace('&','&amp;')
    string = string.replace('<','&lt;')
    string = string.replace('>','&gt;')

    return enclose(string, 'sentence', sentence_atts)

"""
def sentence(sent):
    
    global sentence_id

    string = '\n'.join([ token for token in sent ]) + '\n'
    sentence_atts = { 'id' : sentence_id, }
    sentence_id += 1
    
    return enclose(string, 'sentence', sentence_atts)


def paragraph(element):
    
    global paragraph_id

    text   = ' '.join([ s for (s, atts) in get_string_data(element) ])
    string = ''.join([ sentence(sent) for sent in tokenize(text) ])

    paragraph_atts = { 'id' : paragraph_id, }
    paragraph_id += 1

    return enclose(string, 'paragraph', paragraph_atts)"""


def paragraph(element):

    global paragraph_id
    
    string = ''.join([ sentence(sent) for sent in align_data(element) ])
    
    paragraph_atts = { 'id' : paragraph_id, }
    paragraph_id += 1

    return enclose(string, 'paragraph', paragraph_atts)


def text(page_file, mets={}, date=''):

    element = ET.parse(page_file).getroot()
    
    string = ''.join([ paragraph(block) for block in element.findall('.//'+block_tag, ns) ])
    datefrom, dateto, timefrom, timeto = timespan(date)
    
    text_atts = {
        'datefrom' : datefrom,
        'dateto'   : dateto,
        'timefrom' : timefrom,
        'timeto'   : timeto,
        'page_no'  : element.findall('.//'+page_tag, ns)[0].get('PHYSICAL_IMG_NR'),
        'page_id'  : element.findall('.//'+page_tag, ns)[0].get('ID'),
        }
    text_atts.update(mets)
    
    return enclose(string, 'text', text_atts)


def main(page_file, mets={}, date=''):
    
    global page_tag, block_tag, line_tag, string_tag 
    global paragraph_id, sentence_id, ns

    paragraph_id = 0
    sentence_id = 0
    
    # Get XML Namespaces
    ns  = get_namespaces(page_file)
    pfx = ''

    # NOTE: ElementTree sucks at handling default namespaces;
    # If a default namespace (empty string) is found, use a non-empty prefix instead.
    if '' in ns:
        ns['default'] = ns.pop('')
        pfx = 'default:'
    
    page_tag   = pfx+'Page'
    block_tag  = pfx+'TextBlock'
    line_tag   = pfx+'TextLine'
    string_tag = pfx+'String'
   
    stderr.write('Converting %s...\n' % page_file)
    return text(page_file, mets, date)


if __name__ == '__main__':
    
    from mets import get_mets
    import argparse
    
    parser = argparse.ArgumentParser(description='Converts an Alto XML file into VRT, writes into STDOUT.')
    parser.add_argument('file', help='input file (XML)')
    parser.add_argument('--mets', type=str, help='optional mets.xml file containing metadata')
    parser.add_argument('--date', type=str, default="", help='date in YYYY, YYYYMM or YYYYMMDD format; overrides whatever date is found in METS')
    args = parser.parse_args()
    
    page_file = args.file
    mets_file = args.mets
    date      = args.date
    
    mets = {}
    if mets_file != None:
        mets = get_mets(mets_file)
        if date == '':
            date = get_date(mets)
    
    vrt_string = main(page_file, mets, date)
    print(vrt_string, end='')
    stderr.write('Done.\n')
