#!/usr/bin/env python3
# Convert Alto XML into VRT

import re
from sys import stderr
import xml.etree.ElementTree as ET
from vrt_util import *
from string import punctuation
from copy import deepcopy
from ast import literal_eval

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


# Align tokenizations from the XML file (strings) and hfst-tokenize (tokens)
# Cases:
# * Exact match:
#   - "foo" vs. "foo"
# * String comprises several tokens: punctuation attached to the word
#   - "foo." vs. ["foo", "."]
#   - "(foo)" vs. ["(", "foo", ")"]
# * Strings combine into one token: numerals
#   - ["100", "000"] vs. "100 000"
#   - ["100", "000", "000"] vs. "100 000 000"
# * Both of the above: punctuation and numerals
#   - ["100", "000."] vs. ["100 000", "."]
#   - ["(10", "000)"] vs. ["(", "10 000", ")"]
def align_data(element, page_file):

    string_data = get_string_data(element)

    text = ' '.join([ s for ( s, atts ) in string_data ])
    sents = tokenize(text, page_file)
    use_original_strings=False # prefer result from hfst-tokenize
    
    aligned_para = []
    
    for sent in sents:
        aligned_sent = []
        for token in sent:
            ( string, atts ) = string_data.pop(0)
            string = string.strip()
            while string == '':
                ( string, atts ) = string_data.pop(0)
                string = string.strip()
            # strings combine into one token
            if len(token) > len(string):
                stderr.write('WARNING: mismatch between token "%s" and original string(s)!\n' % token)
                stderr.write('%s vs. "%s"\n' % ( sent, string))
                if not use_original_strings:
                    stderr.write('Using %s as token instead...\n' % token)
                    new_string = ''
                    new_atts = {}
                    # append strings while they match
                    while token.startswith(string):
                        token = token[len(string):].strip()
                        if new_string == '':
                            new_string = str(string)
                        else:
                            # combine parts of token with nbsp
                            new_string = new_string + "\u00A0" + string
                        for key in atts.keys():
                            if key not in new_atts.keys():
                                new_atts[key] = atts[key]
                            else:
                                new_atts[key] = new_atts[key] + " " + atts[key]
                        if len(string_data) != 0:
                            ( string, atts ) = string_data.pop(0)
                            string = string.strip()
                    # see if part of the last string matches
                    if token != '' and string.startswith(token):
                        if new_string == '':
                            new_string = str(string)
                        else:
                            new_string = new_string + "\u00A0" + token
                        for key in atts.keys():
                            value = atts[key]
                            if key == "CC":
                                value = value[:len(token)] # only matching part of CC value
                                if value == '':
                                    value = '_' # empty value (words that are hyphenated between pages)
                            if key == "HYPH":
                                value = value[:len(token)+1] # only matching part of HYPH value
                                if value == '':
                                    value = '_' # empty value (words that are hyphenated between pages)
                            if key not in new_atts.keys():
                                new_atts[key] = value
                            else:
                                new_atts[key] = new_atts[key] + " " + value
                        string = string[len(token):].strip()
                        # the part of string that did not match will be processed on next iteration
                        if string != '':
                            string_data = [ ( string, atts ) ] + string_data
                    aligned_sent.append((new_string, new_atts))
                    if token != '':
                        continue
                else: # if not use_original_strings:
                    while token.startswith(string):
                        stderr.write('Using %s as token instead...\n' % string)
                        token = token[len(string):].strip()
                        aligned_sent.append((string, atts))
                        ( string, atts ) = string_data.pop(0)
                        string = string.strip()
            # exact match or string comprises several tokens
            if string.startswith(token):
                if token != '':
                    atts1 = deepcopy(atts)
                    atts1["CC"] = atts["CC"][:len(token)] # only matching part of CC value
                    if "HYPH" in atts1.keys():
                        atts1["HYPH"] = atts["HYPH"][:len(token)+1] # only matching part of HYPH value
                    aligned_sent.append((token, atts1))
                string = string[len(token):].strip()
                # the part of string that did not match will be processed on next iteration
                if string != '':
                    value = atts["CC"][len(token):] # only matching part of CC value
                    if value == '':
                        value = '_' # empty value (words that are hyphenated between pages)
                    atts["CC"] = value
                    if "HYPH" in atts.keys():
                        value = atts["HYPH"][len(token)+1:] # only matching part of HYPH value
                        if value == '':
                            value = '_' # empty value (words that are hyphenated between pages)
                        atts["HYPH"] = value
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
        # character confidence not defined
        if not 'CC' in atts:
            atts['CC'] = '_'
        # word confidence or not defined
        if not 'WC' in atts:
            atts['WC'] = '_'
        if 'SUBS_CONTENT' in atts:
            if atts['SUBS_TYPE'] == 'HypPart1':
                pairs.append(( atts['SUBS_CONTENT'], atts ))
            if atts['SUBS_TYPE'] == 'HypPart2':
                # combine CC and WC values from first and second parts
                # of hyphenated words and add attribute HYPH
                if len(pairs) > 0:
                    previous_cc = pairs[-1][1]['CC']
                    previous_wc = pairs[-1][1]['WC']
                    previous_content = pairs[-1][1]['CONTENT']
                    current_cc = atts['CC']
                    current_wc = atts['WC']
                    current_content = atts['CONTENT']
                    if (previous_cc == '_' or current_cc == '_'):
                        new_cc = '_'
                    else:
                        new_cc = previous_cc + current_cc
                    if (previous_wc == '_' or current_wc == '_'):
                        new_wc = '_'
                    else:
                        new_wc = previous_wc + " " + current_wc
                    new_content = previous_content + " " + current_content
                    hyphenated = previous_content + "-" + current_content
                    pairs[-1][1]['CC'] = new_cc
                    pairs[-1][1]['WC'] = new_wc
                    pairs[-1][1]['CONTENT'] = new_content
                    pairs[-1][1]['HYPH'] = hyphenated
        else:
            pairs.append(( atts['CONTENT'], atts))

    return pairs


def sentence(sent):

    global sentence_id, tokencount

    string = ''
    for (token, atts) in sent:
        s_id = atts['ID']
        cont = atts['CONTENT']
        vpos = atts['VPOS']
        hpos = atts['HPOS']
        ocr = atts['WC']
        cc = atts['CC']
        if 'HYPH' in atts.keys():
            hyph = atts['HYPH']
        else:
            hyph = token
        # Handle whitespace:
        #
        # represent tabs in content as underscores as tab is reserved
        # for field separator in VRT format
        cont = cont.replace('\t', '_')
        # sometimes content has an empty value, so value combined from hyphenated parts
        # might contain spaces in the beginning or end
        cont = cont.strip()
        if cont == '':
            cont = '_'
        # do not show tabs in hyphenated form
        hyph = hyph.replace('\t', '')
        if hyph == '':
            hyph = '_'
        # 'token' doesn't have any whitespace other than nbps
        # Any problematic characters in 'token' and hyphenated form are removed later using vrt-fix-character
        # Any problematic characters in content are later replaced with '_' using vrt-fix-characters
        #  (in order to preserve alignment of ocr value)
        string += '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (token, s_id, cont, vpos, ocr, cc, hyph)
        tokencount += 1
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


def paragraph(element, page_file):

    global paragraph_id
    
    string = ''.join([ sentence(sent) for sent in align_data(element, page_file) ])
    
    paragraph_atts = { 'id' : paragraph_id, }
    paragraph_id += 1

    return enclose(string, 'paragraph', paragraph_atts)


def text(page_file, mets={}, date=''):

    element = ET.parse(page_file).getroot()
    
    string = ''.join([ paragraph(block, page_file) for block in element.findall('.//'+block_tag, ns) ])
    datefrom, dateto, timefrom, timeto = timespan(date.replace('-',''))
    
    text_atts = {
        'datefrom' : datefrom,
        'dateto'   : dateto,
        'timefrom' : timefrom,
        'timeto'   : timeto,
        'page_no'  : element.findall('.//'+page_tag, ns)[0].get('PHYSICAL_IMG_NR'),
        'page_id'  : element.findall('.//'+page_tag, ns)[0].get('ID'),
        'filename_orig' : page_file,
        'filename_metadata' : metadata_file,
        'sentcount' : sentence_id,
        'tokencount' : tokencount
        }
    text_atts.update(mets)
    
    return enclose(string, 'text', text_atts)


def main(page_file, mets={}, date=''):
    
    global page_tag, block_tag, line_tag, string_tag 
    global paragraph_id, sentence_id, ns, tokencount

    paragraph_id = 0
    sentence_id = 0
    tokencount = 0
    
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
    parser.add_argument('--metadata', type=str, help='optional .metadata file containing metadata (extracted with mets2metadata.py from mets.xml and linking files)')
    parser.add_argument('--metsfilename', type=str, help='optional mets.xml filename used as value for attribute "filename_metadata"')
    args = parser.parse_args()
    
    page_file = args.file
    metadata_file = args.metadata
    mets_filename = args.metsfilename

    mets = {}
    date = ''
    if metadata_file != None:
        with open(metadata_file, 'r') as file:
            data = file.read().replace('\n', '')
        mets = literal_eval(data)
        date = mets['date']

    if mets_filename != None:
        mets['filename_metadata'] = mets_filename

    vrt_string = main(page_file, mets, date)
    print('<!-- #vrt positional-attributes: word wid content vpos ocr cc hyph -->')
    print(vrt_string, end='')
    stderr.write('Done.\n')
