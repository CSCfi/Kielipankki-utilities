#! /usr/bin/env python3

from sys import argv, stderr
import xml.etree.ElementTree as ET
from vrt_util import *
from string import punctuation

div_tag       = 'div'
paragraph_tag = 'p'
sentence_tag  = 's'
clause_tag    = 'cl'
word_tag      = 'w'
punct_tag     = 'pu'

div_id = 0
paragraph_id = 0
sentence_id = 0
clause_id = 0

wordcount = 0

def word_atts(element):
    
    global wordcount    
    wordcount += 1
    
    wordform = element.text
    atts = element.attrib
    fields = [ wordform ]
    for name in [ 'lemma', 'pos', 'new', 'type', 'mrp', 'fun', 'com', 'tunit' ]:
        if name in atts:
            if name == 'new' and atts['new'] == '':
                fields.append(atts['lemma'])
            else:
                fields.append(atts[name])
        else:
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
        elif sub_element.tag == sentence_tag:
            stderr.write("WARNING: Nested sentence %s found within %s!\n" % (sub_element, element))
            stderr.write("Processing subelements instead...\n")
            for sub2_element in sub_element:
                string += new_clause(sub2_element)
        else:
            stderr.write("WARNING: Unexpected %s within %s, skipping...\n" % (sub_element, element))
    
    clause_atts = {
        'id'     : str(curr_id),
        'loc'    : '',
        'biblia' : '',
        'type'   : '',
        #'fun'    : '',
        }
    if type(element) != list:
        clause_atts.update({ key:val for key, val in element.attrib.items()
                             if key in clause_atts })
    
    
    return enclose(string, 'cl', clause_atts)


def new_sentence(element):
    
    global sentence_id, clause_id
    
    clause_id, misc_id = 0, 0
    curr_id = sentence_id
    sentence_id += 1
    
    string = ''
    for sub_element in element:
        if sub_element.tag == clause_tag:
            string += new_clause(sub_element)
        elif sub_element.tag in [ word_tag, punct_tag ]:
            string += new_clause([ sub_element ])
        elif sub_element.tag == sentence_tag:
            stderr.write("WARNING: Nested sentence %s found within %s!\n" % (sub_element, element))
            stderr.write("Processing subelements instead...\n")
            for sub2_element in sub_element:
                string += new_clause(sub2_element)
        else:
            stderr.write("WARNING: Unexpected %s within %s, skipping...\n" % (sub_element, element))
    
    sentence_atts = {
        'id'     : str(curr_id),
        'loc'    : '',
        'biblia' : ''
        }
    if type(element) != list:
        sentence_atts.update({ key:val for key, val in element.attrib.items()
                               if key in sentence_atts })
    return enclose(string, 'sentence', sentence_atts)


def new_paragraph(element):

    global vrt_string, paragraph_id, sentence_id
    sentence_id = 0
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
        'id' : str(curr_id)
    }
    
    return enclose(string, 'div', div_atts)


def new_text(filename, subcorpus):

    global vrt_string, wordcount

    root = ET.parse(filename).getroot()
    header = root.find('header').text.strip()

    try:
        date = dates[subcorpus]
    except:
        stderr.write('WARNING: Spurious subcorpus name "%s", no date found!\n' % subcorpus)
        date = ''
    
    datefrom, dateto, timefrom, timeto = timespan(date)

    string = ''
    for sub_element in root.find('text').findall('div'):
        string += new_div(sub_element)
    
    text_atts = {
        'id'       : 'agricola_%s' % subcorpus,
        'title'    : header,
        'filename' : filename.split('/')[-1],
        'date_orig': encode(date),
        'datefrom' : datefrom,
        'dateto'   : dateto,
        'timefrom' : timefrom,
        'timeto'   : timeto,
        'wordcount': str(wordcount),
    }
    text_atts.update(root.find('text').attrib)
    
    return enclose(string, 'text', text_atts)


xml_file  = argv[1]
subcorpus = argv[2]

dates = { "abckiria"        : "1543",
          "kasikiria"       : "1540",
          "messu"           : "1549",
          "piina"           : "1549",
          "profeetat"       : "1552",
          "psaltari"        : "1551",
          "rucouskiria"     : "1544",
          "sewsitestamenti" : "1548",
          "veisut"          : "1551"
}

stderr.write('Converting %s\n' % xml_file)
vrt_string = new_text(xml_file, subcorpus)
print(vrt_string, end='')
