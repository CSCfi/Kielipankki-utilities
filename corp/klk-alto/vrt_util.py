import xml.etree.ElementTree as ET
import hfst, random, subprocess, re, os
from datetime import datetime
from string import whitespace
from sys import stderr

token_sep = '\n'
sent_sep  = '\n\n'

# Tokenize given text, return a list on sentences, which are lists of tokens
def tokenize(text, lang="fi"):
    lines = run_hfst_tokenize(text)
    sents = [ [ token for token in sent.split(token_sep) if token != '' ]
              for sent in lines.split(sent_sep) if sent != '' ]
    return sents


# Run hfst-tokenize for in shell for given text, return output                                                                      
def run_hfst_tokenize(text, tokenizer='finnish-tokenize'):
    timestamp = datetime.now().isoformat(sep="_").replace(":", '').replace('.', '_')
    filename_in = 'untokenized_%s.txt' % timestamp
    open(filename_in, 'w', encoding='utf8').write(text)
    out_str = subprocess.getoutput('cat %s | %s' % (filename_in, tokenizer))
    os.remove(filename_in)
    return out_str

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
    string = str(string)
    for key, char in exc.items():
        string = string.replace(key, char)
    for char in whitespace:
        string = string.replace(char, ' ')
    for key, char in xml_ents.items():
        string = string.replace(key, char)
    string = re.sub('&(?!([a-zA-Z]+|#[0-9]+);)', '&amp;', string)
    string = string.strip()
    return string


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
