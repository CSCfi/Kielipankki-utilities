#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ylilauta/suomi24.fi nettikielitokenisoija ja virkkeistäjä
# asahala fin-clarin 14.02.2015,

# vie importilla warcciparseriin
# kutsu funktiota tokenize, joka ottaa argumenteikseen syötemerkkjonon
# sekä pisimmän sallitun pituuden stringille (huomaa, että cwb-encode
# katkoo automaattisesti yli 4096 merkkiä pitkät stringit ja kadottaa
# näiden loput. Truncate-funktiota käyttämällä skripti lisää välejä
# n merkin välein pitkiin stringeihin, joten kaikki säilyvät.

import re
import html.parser

"""
smileys = hymiöt :D :--------D ^_^ :p
char_map = yleiset välimerkit
us_num = pisteillä erotetut jenkkinumerot
urls = ne ja sähköpostit
abbrs = kaksoispisteellä tai apostrofilla lyhennetyt ja taivutetut sanat
abbrx = yleiset lyhenteet
date = päivämäärät ja järjestysluvut
clock = kellonajat hh:mm
acronymsN = N kirjaimen pituiset pisteellä erotetut akronyymit
"""

smileys = r'([:;x=]-*[DEPO\(\)\|codpf]+)|\b(=?[\^oOx-]_+[\^oOx-]=?\b)|[ \b]:3'
char_map = r'(%s|[\.;:,\?!]+|[—\(\)\<\>\{\}]|(^|\s)-)' % smileys
us_num = r'(\d+\.)+\d+(,\d\d)?|\d+,\d\d'
urls = r'(https?://|www\.)([~/\?\+\&a-z0-9_-]+?\.?)+|'\
       '([A-Za-z0-9]+\.)?[A-Za-z0-9]+\@([a-z0-9]+\.)+[a-z]+'
abbrs = r'[a-zA-ZÄÖÅåäö]+?[:\'’]'\
        '(h?[aiuoeöä]+n|[aä]|i?l[lt][aä]|i?s[st][aä]|i?lle|i?ksi)[a-z]*'
abbrx = r' ([A-Z]|aik|kirj|alk|ark|as|ed|eKr|ekr|jKr|jkr|'\
                  'eaa|tod|henk|ym|koht|jaa|esim|huom|jne|joht|'\
                  'k|ks|kts|lk|lkm|lyh|läh|miel|milj|mm|mrd|myöh|n|'\
                  'nimim|ns|nyk|oik|os|p|ps|par|per|pj|prof|puh|'\
                  'kok|kes|kys|ko|virh|vas|pvm|rak|s|siht|synt|t|tark|til|'\
                  'tms|toim|huhtik||v|vas|vast|vrt|yht|yl|ym|yms|'\
                  'yo|ao|em|ko|ml|po|so|ts|vm|etc)\.'
acronyms4 = r'([A-Za-z])\.([A-Za-z])\.([A-Za-z])\.([A-Za-z])\.'
acronyms3 = r'([A-Za-z])\.([A-Za-z])\.([A-Za-z])\.'
acronyms2 = r'([A-Za-z])\.([A-Za-z])\.'
date = r'(\d\d?)\.'
clock = r'(\d\d?):(\d\d)(:\d\d)?'

def truncate(string, maxlen):
    """ Typistä floodaukset n (maxlen) merkkiin"""
    truncated = str()

    i = 0
    for c in string:
        if i == maxlen:
            truncated += '\n'
            i = -1
        else:
            truncated += c
        i += 1
    return truncated

def split_sents(string, maxlen, sent_id):

    if sent_id is None:
        id_ = ''
    else:
        id_ = '_id="{sid}"'.format(sid=sent_id)

    string = ' ' + string + ' '
    #korvaa unicode-lainausmerkit suomalaisiksi
    string = re.sub('[”“„"]', ' " ', string)
    string = re.sub("['’]", r" ' ", string)
    """ Tekstin jako virkkeisiin joko kovasta välimerkistä tai hymiöstä.
    Virke saa alkaa myös pienellä alkukiraimella """
    string = re.sub('<', ' LESSERTHAN ', string)
    string = re.sub('>', ' GREATERTHAN ', string)
    string = re.sub(" [«»](.+?)[«»] ", r' <quote3> \1 </quote3> ', string)
    string = re.sub(' "(.+?)" ', r' <quote2> \1 </quote2> ', string)
    string = re.sub(" ['’](.+?)['’] ", r' <quote1> \1 </quote1> ', string)
    string = re.sub('\n| +', ' ', string)
    string = re.sub('( [\!\?\.]+?( %s)?( </quote.>)? | %s )' % (smileys, smileys),
                    r'\1 </sentence> <sentence%s> ' %id_ , string)
    string = '<sentence%s> ' % id_ + string
    #purkkakorjaus, korjaa vriheellisen virkejaon "tekstiä", ...
    string = re.sub('</sentence> <sentence> ,', ',', string)

    if not string.endswith(('</sentence> ', '</sentence>')):
        string += ' </sentence>'

    string = re.sub('</?quote2>', '"', string)
    string = re.sub('</?quote3>', '»', string)
    string = re.sub('</?quote1>', "'", string)
    string = re.sub('GREATERTHAN', '&gt;', string)
    string = re.sub('LESSERTHAN', '&lt;', string)
    string = re.sub(' +', ' ', string)
    tokens = string.split(' ')

    if sent_id is not None:
        tokens = [re.sub('<sentence_id', '<sentence id', token) for token in tokens]

    outfile = ''
    for token in tokens:
        outfile += truncate(token, maxlen) + '\n'
    return(outfile)
    #return '\n'.join(string.split(' '))

def mark_specials(string):
    """ merkitse tokenisoinnissa ignoroitavat yksiköt, esim. urlit.
    näiden perusteella ei tehdä myöskään virkejakoa, vaan kovat välimerkit
    sisällytetään tokeneihin """
    string = re.sub('([\(\)])', r' \1 ', string)
    string = re.sub(acronyms4, r' \1QxQz\2QxQz\3QxQz\4QxQz', string)
    string = re.sub(acronyms3, r' \1QxQz\2QxQz\3QxQz', string)
    string = re.sub(acronyms2, r' \1QxQz\2QxQz', string)
    string = re.sub(clock, r' \1QzQx\2 ', string)
    string = re.sub(abbrx, r' \1QxQz', string)
    string = re.sub(date, r'\1QxQz', string)
    # jos vuoden perässä piste, tulkitse kovaksi välimerkiksi
    string = re.sub('(1\d\d\d|20[01]\d)QxQz ', r' \1 .', string)
    return re.sub('(%s|%s|%s|&..;|&...;|&....;)' % (us_num, urls, abbrs), r'¶\1¶¤', string)

def remove_spaces(string):
    i = 0
    wrapped = str()
    replace = False
    for char in string:
        if char == '¶':
            replace = True
        elif char == '¤' and string[i-1] == '¶':
            replace = False
        elif replace:
            if char not in (' ', '¶'):
                wrapped += char
        else:
            if char not in ('¶'):
                wrapped += char
        i += 1
    return re.sub(' +', ' ', wrapped.strip())

def tokenize(string, maxlen, sent_id=None):

    if len(string) > maxlen:
        string = truncate(string, maxlen)

    # muunna HTML-entiteetit ja korvaa tabit (jäsennin ei tykkää)
    string = html.parser.HTMLParser().unescape(string)
    string = re.sub('\t', ' ', string)
    # lisää tähän poikkeuksia, mikäli haluat säilyttää html-tägejä
    # huomaa, että loppusuljetut tagit kuten <img src="..."/> tai <br/>
    # saattavat aiheuttaa ongelmia cwb:n ja korpin kanssa
    string = re.sub('<.+?>', '', string)

    out = (re.sub(char_map, r' \1 ', mark_specials(string)))
    # korvataan väliaikaiset symbolit 
    out = re.sub('QxQz', '.', remove_spaces(out))
    out = re.sub('QzQx', ':', remove_spaces(out))
    vrt = split_sents(out, maxlen, sent_id)
    return re.sub('<sentence>\n</sentence>', '', vrt[0:-1]).strip('\n')
