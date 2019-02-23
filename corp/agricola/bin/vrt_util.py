#! /usr/bin/env python3

import xml.etree.ElementTree as ET
import hfst, random, subprocess, re
from string import whitespace
from sys import stderr

token_sep = '\n'
sent_sep  = '\n\n'

# XML element tags
def enclose(string, tag, atts):
    return start_tag(tag, atts) + string + end_tag(tag)


def start_tag(tag, atts={}):
    att_str = ' '.join(sorted([ '%s="%s"' % (att, encode(val))
                                for att, val in atts.items() ]))
    return '<%s %s>\n' % (tag, att_str)


def end_tag(tag):
    return '</%s>\n' % tag

# Encode special characters as XML entities
# Convert all whitespace characters into simple spaces
# Remove leading and trailing whitespace characters
# Also rewrite characters and sequences specified by user (exc)

xml_ents = {
        '<':'&lt;',
        '>':'&gt;',
        '"':'&quot;',
        "'":'&apos;',
        '[':'&#91;',
        ']':'&#93;',
        }


def encode(string, exc={}):
    for key, char in exc.items():
        string = string.replace(key, char)
    for char in whitespace:
        string = string.replace(char, ' ')
    for key, char in xml_ents.items():
        string = string.replace(key, char)
    string = re.sub('&(?!([a-zA-Z]+|#[0-9]+);)', '&amp;', string)
    string = string.strip()
    return string

# Dates and timespans

def days_in_month(yyyymm):
    
    year   = int(yyyymm[0:4])
    month  = int(yyyymm[4:6])
    
    days = [ '' ,'30','28','31','30','31','30','31','31','30','31','30','31' ]
    if year % 4 == 0:
        days[2] = '29'
    
    try:
        month = days[month] 
    except:
        stderr.write('WARNING: Missing or invalid date "%s"\n' % yyyymmdd)
        exit(0)
    return month


def timespan(yyyymmdd):
    
    datefrom, dateto = yyyymmdd, yyyymmdd
    timefrom, timeto = "000000", "235959"

    if len(datefrom) not in [ 4, 6, 8 ]:
        stderr.write('WARNING: Missing or invalid date "%s", assigning empty timespan values.\n' % yyyymmdd)
        return ('', '', '', '')

    if len(datefrom) == 4:
        datefrom = datefrom + '01'
        dateto   = dateto + '12'
    if len(datefrom) == 6:
        datefrom = datefrom + '01'
        dateto   = dateto + days_in_month(dateto)

    return (datefrom, dateto, timefrom, timeto)
