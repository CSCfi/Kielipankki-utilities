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

def get_text(block_elem):
    
    strings = []
    for string_elem in block_elem.findall('.//'+string_tag, ns):
        atts = string_elem.attrib
        if 'SUBS_CONTENT' in atts:
            if atts['SUBS_TYPE'] == 'HypPart1':
                strings.append(atts['SUBS_CONTENT'])
        else:
            strings.append(atts['CONTENT'])
    return ' '.join(strings)


def sentence(sent):

    global sentence_id
    
    string = '\n'.join([ token for token in sent ]) + '\n'
    sentence_atts = { 'id' : sentence_id, }
    sentence_id += 1

    return enclose(string, 'sentence', sentence_atts)


def paragraph(element):

    global paragraph_id
    
    text  = get_text(element)
    string    = ''.join([ sentence(sent) for sent in tokenize(text) ])    
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
    # If a default namespace are found, a non-empty prefix is required
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
