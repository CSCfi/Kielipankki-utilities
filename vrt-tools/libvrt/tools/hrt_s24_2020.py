# -*- mode: Python; -*-

'''Implementation of hrt-from-s24-2020.'''

from libvrt.args import BadData
from libvrt.args import transput_args

import csv
import re, sys

def parsearguments(argv, *, prog = None):

    description = '''

    Process input like the 2021 dump of Suomi24 into HRT form (after
    dealing with the few NUL bytes in the dump that the Python CSV
    reader would not deal with).

    '''

    parser = transput_args(description = description,
                           inplace = False)

    parser.add_argument('--fix', action = 'store_true',
                        help = '''

                        Fix character-level issues that were observed
                        specifically in s24-2018-2020-src.

                        ''')
    
    args = parser.parse_args()
    args.prog = prog or parser.prog

    return args

# These are what the 2018-2020 dump head are:
# - "threads" 9 fields,
# - "comments" 10 fields, as indicated.
THEAD = ['thread_id', 'title', 'body',
         'anonnick', 'created', 'topics',
         'user_id', 'closed', 'deleted']
CHEAD = ['comment_id', 'thread_id', 'parent_comment_id',
         'body', 'user_id', 'anonnick', 'hierarchy_id',
         'quote_id', 'deleted', 'created']

TBODY = THEAD.index('body')
CBODY = CHEAD.index('body')
CQUID = CHEAD.index('quote_id') # maybe use this for something?

# pass args.fix from main to lower-level functions
FIXING = False

def main(args, ins, ous):
    '''Transput input stream (database dump) in ins to HRT in ous.

    There would be a head line followed by record lines, either thread
    starters or comments.

    '''

    global FIXING
    FIXING = args.fix

    data = csv.reader(ins)
    head = next(data, [])
    if head == THEAD:
        ship_thread(data, ous)
    elif head == CHEAD:
        ship_comment(data, ous)
    else:
        raise BadData('unexpected head: ' + repr(head))

def ship_thread(data, ous):
    for record in data:
        begin_thread(record, ous)
        ship_body(record[TBODY], None, ous)
        end_message(ous)
    pass

def ship_comment(data, ous):
    for record in data:
        begin_comment(record, ous)
        ship_body(record[CBODY], record[CQUID], ous)
        end_message(ous)
    pass

def esc_meta(value):
    # should not this come from some library?
    # must entify < > & and "
    return value

def begin_thread(record, ous):
    [ THREAD_ID, TITLE, BODY,
      ANONNICK, CREATED, TOPICS,
      USER_ID, CLOSED, DELETED ] = record

    # This is where to adapt to the desired attribute set: the keys of
    # the dict are the output attribute names and the selection of the
    # attributes is made right here.
    attributes = dict(thread_id = THREAD_ID,
                      title = TITLE,
                      anonnick = ANONNICK,
                      user_id = USER_ID,
                      closed = CLOSED,
                      deleted = DELETED)

    # Split topics at a comma that is not followed by a space (at a
    # guess), flank with vertical bars (not sure if topics is ever
    # empty, but then there is just a vertical bar).
    attributes['topics/'] = (
        '|'
        + '|'.join(re.split(r',(?=\S)', TOPICS))
        + '|'
    ) if TOPICS else '|'

    attributes.update(datetime_attributes(CREATED))

    ship_meta('text', attributes, ous)

    # paragraph number?
    # type is head? or title?
    # need escaping?

    print('<paragraph type="head">', file = ous)
    print(TITLE.replace('&quot;', '"') or '_', file = ous)
    print('</paragraph>', file = ous)

def begin_comment(record, ous):
    [ COMMENT_ID, THREAD_ID, PARENT_COMMENT_ID,
      BODY, USER_ID, ANONNICK, HIERARCHY_ID,
      QUOTE_ID, DELETED, CREATED ] = record

    # This is where to adapt to the desired attribute set: the keys of
    # the dict are the output attribute names and the selection of the
    # attributes is made right here.
    attributes = dict(comment_id = COMMENT_ID,
                      thread_id = THREAD_ID,
                      parent_comment_id = PARENT_COMMENT_ID,
                      user_id = USER_ID,
                      anonnick = ANONNICK,
                      hierarchy_id = HIERARCHY_ID,
                      quote_id = QUOTE_ID,
                      deleted = DELETED)

    attributes.update(datetime_attributes(CREATED))
    ship_meta('text', attributes, ous)

def datetime_attributes(CREATED):
    '''Return all manner of derived date attributes.'''
    date, time = CREATED.split(' ')
    YYYY, MM, DD = date.split('-')
    hh, mm, ss = time.split(':')
    return dict(created = CREATED,
                datefrom = YYYY + MM + DD,
                dateto = YYYY + MM + DD,
                timefrom = hh + mm + ss,
                timeto = hh + mm + ss)

def ship_meta(element, attributes, ous):
    print('<{element}{space}{attributes}>'
          .format(element = element,
                  space = ' ' if attributes else '',
                  attributes =
                  ' '.join('{}="{}"'.format(name, esc_meta(value))
                           for name, value
                           in sorted(attributes.items()))),
          file = ous)

def end_message(ous):
    print('</text>', file = ous)

def ship_body(body, quid, ous):
    '''Tentative hypothesis is that <br /><br /> is the paragraph break,
    single <br /> is just a line break and not even a sentence break,
    so never mind those, and longer <br /> sequences do not occur at
    all. And any other angles are already entified? Are they?

    There were longer <br /> sequeces, many with whitespace between.
    There were a small number of other angles, now entified before
    reaching this script.

    '''

    # if args.fix:
    #     repair observed encoding problems
    #
    # This must be before <br /> processing.
    body = fix(body)

    # paragraph number?
    # paragraph type? (shipping now)

    body = body.replace('&quot;', '"')
    for para in re.split(r'<br />(?:\s*<br />)+', body):
        para = para.replace('<br />', '\n')
        if re.fullmatch(r'\s*', para): continue
        print('<paragraph type="body">', file = ous)
        print(para, file = ous)
        print('</paragraph>', file = ous)

def fix(data):
    '''Called with FIXING == args.fix, hopefully repair character problems
    (observed in s24-2018-2020 data) if args.fix, else just return data.

    The minimum contract is to make prohibited characters go away. If
    this cannot be done sensibly, introduce some minor nonsense, or it
    is more likely to be GIGO.

    '''
    if FIXING:
        return data.translate(character_fixes)
    return data

character_fixes = str.maketrans({
    # Translations based on observing the occurrences in
    # comments_2018.
    #
    # Translations of LS and PS introduce new "<br />".

    '\u0001' : None, # delete C0 SOH ^A
    '\u0002' : None, # delete C0 STX ^B (cannot help)
    '\u0008' : None, # delete C0 BS ^H
    '\u000B' : None, # delete C0 VT ^K (cannot help)
    '\u000E' : None, # delete C0 SO ^N (cannot help)
    '\u000F' : None, # delete C0 SI ^O
    '\u0010' : None, # delete C0 DLE ^P
    '\u0011' : None, # delete C0 DC1 ^Q (sigh)
    '\u0012' : None, # delete C0 DC2 ^R
    '\u0013' : '\u2013', # C0 DC3 ^S : – (in two sentences)
    '\u0014' : None, # delete C0 DC4 ^T
    '\u0015' : None, # delete C0 NAK ^U
    '\u0016' : None, # delete C0 SYN ^V
    '\u0017' : None, # delete C0 ETB ^W
    '\u0018' : None, # delete C0 CAN ^X
    '\u0019' : None, # delete C0 EM ^Y
    '\u001A' : None, # delete C0 SUB ^Z
    '\u001D' : None, # delete C0 GS ^]
    '\u001E' : None, # delete C0 RS ^^
    '\u001F' : None, # delete C0 US ^_

    '\u007F' : None, # delete DEL

    # C1 : Windows-1252 from Wikipedia
    # https://en.wikipedia.org/wiki/Windows-1252
    '\u0080' : 'U+0080', # C1 PAD : GIGO (€ makes no sense)
    '\u0082' : None, # delete C1 BPH (‚ makes no sense)
    '\u0083' : None, # delete C1 NBH (ƒ makes no sense)
    '\u0084' : 'U+0084', # C1 IND : GIGO („ makes no sense)
    '\u0085' : '\u2026', # C1 NEL : … (HORIZONTAL ELLIPSIS)
    '\u0086' : 'U+0086', # C1 SSA : GIGO († makes no sense)
    '\u0090' : 'U+0090', # C1 DCS : GIGO (not in Windows-1252)
    '\u0092' : '\u2019', # C1 PU2 : ’
    '\u0093' : '\u201C', # C1 STS : “
    '\u0094' : '\u201D', # C1 CCH : ”
    '\u0096' : '\u2013', # C1 SPA : –
    '\u009D' : None, # delete C1 OSC (not in Windows-1252)

    # LS, LINE SEPARATOR, 108 occurrences in comments_2018, no way to
    # do justice to them all (some are even inside a URI), but give
    # them a chance to combine with adjacent <br /> to become a
    # paragraph break and never mind the rest.
    '\u2028' : '<br />',

    # PS, PARAGRAPH SEPARATOR, two occurrences in comments_2018, in
    # one message, in Swedish, this will insert a good paragraph break
    # in one and a bad paragraph break at a place that is already bad,
    # so never mind.
    '\u2029' : '<br /><br />',
})
