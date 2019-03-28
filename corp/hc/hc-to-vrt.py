import re
import html
from catrefs import CATREFS

"""
Helsinki Corpus -> VRT 

CATREFS is a dictionary extracted from HC.xml
uasge: python3 hc-to-vrt.py > output.vrt
hc.xml and catrefs must be in the same folder with this script """

mode = '' # Keeps track of part of the corpus being processed 
text_ids = {}

with open('hc.xml', 'r', encoding="utf-8") as data:
    teksti = data.readlines()

def get_attrs(attrs, line):
    """ Returns a dictionary of attribute values from line,
    argument ´attrs´ must be given as a list """
    attributes = {}
    for attr in attrs:
        attributes[attr] = html.escape(re.sub('.+?{}="(.+?)".+'.format(attr),
                                              r'\1', line))
    return attributes

def esc(string):
    return html.escape(string)

def unesc(string):
    return html.unescape(string)

def get_attr(attr, line):
    """ Return single attribute value from line """ 
    return html.escape(re.sub('.+?{}="(.+?)".+'.format(attr), r'\1', line))

def getval(line):
    """ Return line without tags """
    return re.sub('<.+?>', '', line)

def formatdate(date):
    """ Add zero to date ranges """
    if date.startswith(('-', '–')):
        return '0'+date
    else:
        return date

def make_catrefs(dictionary):
    """ Return catrefs as <text> arguments for VRT """
    out = []
    for k, v in dictionary.items():
        out.append(k.replace('_', '') + '="' + esc(v) + '"')
    return ' '.join(out)

def close_(t, is_open):
    """ Check if tag ´t´ is open or not, and close it if yes.
    Return new truth value for the tag according to its state. """
    if t == 'sent':
        tag = '</sentence>'
    if t == 'para':
        tag = '</paragraph>'
    if t == 'line':
        tag = '</line>'
    if is_open:
        print(tag)
        return False
    else:
        return True

for line in teksti:
    """ Parsing is done one sub-corpora at a time
    
    1. initialize everything at <TEI>
    2. collect metadata wrapped between certain elements (title, class etc.)
    3. collect text -> tokenize -> split into sents
    4. print everything when </TEI> appears
    5. repeat """

    line = line.strip().strip('\n')
    if line.startswith('<TEI n='):
        ''' text_ids contain information about the text '''
        text_ids = get_attrs(['n', 'xml:id'], line)
        rivit = []
        texttitle = ''
        textauthor = ''
        datefrom = ''
        dateto = ''
        timespan = ''
        sources = []
        lang = ''
        lang_id = ''
        note = '_'
        page = '_'
        pid = 1
        sid = 1
        catrefs = {'contemporaneity': '',
                   'dialect': '',
                   'form': '',
                   'texttype': '',
                   'foreign_orig': '',
                   'foreign_lang': '',
                   'spoken': '',
                   'author_sex': '',
                   'author_age': '',
                   'social_rank': '',
                   'audience': '',
                   'part_rel': '',
                   'interaction': '',
                   'setting': '',
                   'proto': ''}
        milestone = {'type': '_', 'n': '_', 'unit': '_'}
        
    if line.startswith('</TEI'):
        lopen = False
        print('<text title="%s" author="%s" xmlid="%s" id="%s" lang="%s" langid="%s" datefrom="%s" dateto="%s" date="%s" source="%s" %s>' %\
                  (texttitle, textauthor, 
                   text_ids['xml:id'], 
                   text_ids['n'],
                   lang, 
                   lang_id,
                   datefrom+'0101',
                   dateto+'1231', 
                   formatdate(timespan),
                   ' | '.join(sources),
                   make_catrefs(catrefs)))

        print('<paragraph id="%i">' % pid)
        popen = True
        pid += 1
        print('<sentence id="%i">' % sid)
        sopen = True
        sid += 1

        i = 0
        for rivi in rivit:
            """ Process the actual text content """
            if rivi.startswith('.'):
                print(rivi)
                if popen:
                    if i != len(rivit)-2:
                        """ Add a new sentence tag after closed one only
                        if there are still lines left """
                        print('</sentence>')
                        print('<sentence id="%i">' % sid)
                        sopen = True
                        sid += 1
            elif '@PARA@' in rivi:
                """ Paragraph begins  """                
                sopen = close_('sent', sopen)
                popen = close_('para', popen)
                print('<paragraph id="%i">' % pid)
                popen = True
                pid += 1
                print('<sentence id="%i">' % sid)
                sopen = True
                sid += 1
            elif '@PARAEND@' in rivi:
                """ Paragraph ends """
                sopen = close_('sent', sopen)
                popen = close_('para', popen)
            else:
                if '@PARA' not in rivi or not rivi.startswith('.'):
                    print(rivi)
            i += 1

        """ Close sentence and paragraph before </text> if they 
        are still open """
        sopen = close_('sent', sopen)
        popen = close_('para', popen)
        print('</text>')

    if line.startswith('<titleStmt>'):
        mode = 'title'
    if line.startswith('</titleStmt>'):
        mode = ''

    if line.startswith('<textClass'):
        mode = 'class'
    if line.startswith('</textClass'):
        mode = ''

    if mode == 'title':
        if line.startswith('<title key'):
            texttitle = esc(getval(line))
        if line.startswith('<author key'):
            v = get_attr('key', line).title() 
            if v == 'X':
                v = 'Anonymous'
            textauthor = v

    if mode == 'class':
        if line.startswith('<catRef'):
            key = get_attr('scheme', line)[1:]
            target = get_attr('target', line)[1:]
            if key != 'periods':
                """ Ignore overlapping period data """
                catrefs[key] = CATREFS[target]
                
    if line.startswith('<biblStruct'):
        mode = 'biblStruct'
        bibl_info = [] # initialize
    if line.startswith('</biblStruct'):
        """ Merge multiple sources into one string separeted by ; """
        mode = ''
        sources.append('; '.join(bibl_info))
    if mode == 'biblStruct':
        content = re.sub('<.+?>', '', line)
        if content:
            bibl_info.append(esc(content))
    if line.startswith('<date type="original"'):
        datefrom = get_attr('from', line)
        dateto = get_attr('to', line)
        datefrom = get_attr('from', line)
        timespan = getval(line)
    if line.startswith('<language ident='):
        lang_id = get_attr('ident', line)
        lang = esc(getval(line))

    if line.startswith('<text>'):
        mode = 'text'
    if line.startswith('</text>'):
        mode = ''

    if '<milestone' in line:
        milestone = get_attrs(['type', 'unit', 'n'], line)
    if '<note' in line:
        note = getval(line)
    if '<pb ' in line:
        page = get_attr('n', line)

    """ Remove milestone tags from lines """
    line = re.sub('<milestone.+?>', '', line)
    
    """ Replace paragraph tags with placeholders """
    line = re.sub('(<p .+?>|<p>)', ' @PARA@ ', line)
    line = re.sub('</p>', ' @PARAEND@ ', line)

    # Linebreaks can be added in a similar manner,
    # but they will overlap paragraph and sentence tags
    # unless the script above and close_() is modified

    """ Wrap supplied passages with placeholder tags """
    line = re.sub('<supplied.+?>', ' @SS@ ', line)
    line = re.sub('</supplied>', ' @SE@ ', line)

    if mode == 'text':
        supplied = '_'

        if not '<milestone' in line:
            """ Very simple tokenization; wrap punctuation between
            spaces; checking if milestone doesn not exist is now obsolete """
            teksti = re.sub('([\.\!\?:,])', r' \1 ', getval(unesc(line)))
            if re.match('.*[A-Z]\d.*', teksti):
                # quickfix: detokenize identifiers (e.g. B14.2) 
                teksti = teksti.replace(' ', '')

            sanat = re.sub(' +', ' ', teksti).split(' ') # remove excess spaces
            for sana in sanat:
                """ Add supplied attribute to all words encased between
                placeholders """
                if sana == '@SS@':
                    supplied = 'supplied'
                    sana = ''
                if sana == '@SE@':
                    supplied = '_'
                    sana = ''
                if not sana.startswith(('<', '@')) and sana:
                    """ Store actual text content into ´rivit´ list with their
                    corresponding word attributes. Ignore tags and placeholders. """
                    rivit.append(esc(sana) + '\t' + '\t'.join([page, supplied, note, milestone['n'], 
                                                               milestone['unit'], milestone['type']]))
                if sana and sana.strip().startswith('@'):
                    """ Store remaining placeholders @PARA@ / @PARAEND@ """
                    rivit.append(sana)
                else:
                    pass
