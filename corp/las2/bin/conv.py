#!/usr/bin/env python3

from sys import argv, stderr
import xml.etree.ElementTree as ET
from vrt_util import *
from string import punctuation

div_tag = 'div'
paragraph_tag = 'p'
sentence_tag = 's'
clause_tag = 'cl'
word_tag = 'w'
punct_tag = 'pn'

div_id = 0
paragraph_id = 0
sentence_id = 0
clause_id = 0
misc_id = 0

wordcount = 0


def new_misc(element):
    
    global wordcount, misc_id
    curr_id = misc_id
    
    text = element.text
    if text == None:
        stderr.write('WARNING: Unexpected empty element %s -> discarding\n' % element)
        return ''
    
    # Exclude questions from result
    if element.tag == 'kysymys':
        return ''

    misc_id += 1
    
    string = ''
    sentences = tokenize(text)
    for sentence in sentences:
        for token in sentence:
            wordcount += 1
            fields = [ token, '', '', '', '', '' ]
            string += '\t'.join([ encode(f) for f in fields]) + '\n'
    
    misc_atts = {
        'id'  : str(curr_id),
        'type': element.tag
        }
    
    return enclose(string, 'misc', misc_atts)


def word_atts(element):
    
    global wordcount    
    wordcount += 1
    
    wordform = element.text
    if wordform == None:
        wordform = ''
    atts = element.attrib
    fields = [ wordform ]
    for name in [ 'lemma', 'pos', 'mrp', 'fun', 'com' ]:
        if name in atts:
            fields.append(atts[name])
        else:
            if element.tag != punct_tag:
                stderr.write('WARNING: Element %s with missing attribute %s for word %s\n' % ( element, name, wordform ))
            fields.append('')
    return '\t'.join([ encode(f) for f in fields]) + '\n'


def new_clause(element):
    
    global clause_id
    curr_id = clause_id
    clause_id += 1
    
    string = ''
    for sub_element in element:
        if sub_element.tag == clause_tag:
            string += new_clause(sub_element)
        elif sub_element.tag in [ word_tag, punct_tag ]:
            string += word_atts(sub_element)
        else:
            stderr.write("WARNING: Unexpected element %s within element %s\n" % ( sub_element, element ))
            string += new_misc(sub_element)
    
    clause_atts = {
        'id'   : str(curr_id),
        'type' : '',
        'fun'  : '',
        'com'  : '',
        }
    clause_atts = get_atts(element, clause_atts)
    
    return enclose(string, 'cl', clause_atts)


def new_sentence(element):
    
    global sentence_id, clause_id, misc_id
    
    curr_id = sentence_id
    sentence_id += 1
    
    string = ''
    for sub_element in element:
        if sub_element.tag == clause_tag:
            string += new_clause(sub_element)
        elif sub_element.tag in [ word_tag, punct_tag ]:
            string += word_atts(sub_element)
        else:
            string += new_misc(sub_element)
    
    sentence_atts = {
        'id' : str(curr_id),
        'num' : '',
        }
    
    return enclose(string, 'sentence', sentence_atts)


def new_paragraph(element):

    global vrt_string, paragraph_id, sentence_id
    
    curr_id = paragraph_id
    paragraph_id += 1
    
    string = ''
    for sub_element in element:
        if sub_element.tag == sentence_tag:
            string += new_sentence(sub_element)
        else:
            string += new_sentence([ sub_element ])

    paragraph_atts = {
        'id' : str(curr_id)
    }
    
    return enclose(string, 'paragraph', paragraph_atts)


def new_div(element):

    global div_id
    curr_id = div_id
    div_id += 1
    
    string = ''
    for sub_element in element:
        if sub_element.tag == paragraph_tag:
            string += new_paragraph(sub_element)
        else:
            string += new_paragraph([ sub_element ])

    div_atts = {
        'id' : str(curr_id),
        'question' : ' '.join([ s.text.strip() for s in element.iter('kysymys') ]),
    }
    
    return enclose(string, 'div', div_atts)


def new_text(root, xml_file, corpus_name):
    
    global vrt_string, wordcount    
    
    date = ''    
    if root.find('paivamaara') != None:
        date = root.find('paivamaara').text
        if date == None:
            date = ''
    datefrom, dateto, timefrom, timeto = timespan(date)
    
    string = ''.join([ new_div(sub_element) for sub_element in root.findall('div') ])
    
    text_atts = {
        'id' : corpus_name,
        'title'    : '',
        'filename' : xml_file.split('/')[-1],
        'date_orig': encode(date),
        'datefrom' : datefrom,
        'dateto'   : dateto,
        'timefrom' : timefrom,
        'timeto'   : timeto,
        'wordcount': str(wordcount),
        'num' : '',
        'inf' : '',
        'tt'  : '',
        'te'  : '',
        'lo'  : '',
        'l1'  : '',
        'alin_cefr'    : '',
        'ylin_cefr'    : '',
        'tekstin_cefr' : '',
    }
    text_atts = get_atts(root.find('teksti'), text_atts)
    
    return enclose(string, 'text', text_atts)


def main(xml_file, corpus_name):
    
    stderr.write('Converting %s\n' % xml_file)
    try:
        root = ET.parse(xml_file).getroot()
    except:
        stderr.write("Invalid XML file %s, could not parse!\n" % xml_file)
        exit(0)
    vrt_string = new_text(root, xml_file, corpus_name)
    print(vrt_string, end='')

    
main(argv[1], argv[2])
