# -*- mode: Python; -*-

'''Implementation of hrt-from-s24-2023.'''

from libvrt.args import BadData
from libvrt.args import transput_args

import csv
import re, sys

from itertools import chain

def parsearguments(argv, *, prog = None):

    description = '''

    Process input like the 2023 dump of Suomi24 into HRT form (this
    time deal with the few NUL bytes in the dump that the Python CSV
    reader would not deal with). (Also deal with either , or ; as
    separator. Also override a change in one field name in 2023, as
    content looks as before.)

    '''

    parser = transput_args(description = description,
                           inplace = False)

    parser.add_argument('--fix', action = 'store_true',
                        help = '''

                        Fix character-level issues that were observed
                        specifically in s24-2018-2020-src and then in
                        s24-2021-2023.

                        ''')
    
    args = parser.parse_args()
    args.prog = prog or parser.prog

    return args

# These are what the 2018-2020 dump head are:
# - "threads" 9 fields,
# - "comments" 10 fields, as indicated.
# In 2021-2023, year 2023 comments have one field name change.
# The content of the field seems same as before, so this script
# will accept the new header but use the old header for output.
THEAD = ['thread_id', 'title', 'body',
         'anonnick', 'created', 'topics',
         'user_id', 'closed', 'deleted']
CHEAD = ['comment_id', 'thread_id', 'parent_comment_id',
         'body', 'user_id', 'anonnick', 'hierarchy_id',
         'quote_id', 'deleted', 'created']
CHEAD_2023 = [ # hierarchy_id become comment_order
    'comment_id', 'thread_id', 'parent_comment_id',
    'body', 'user_id', 'anonnick', 'comment_order',
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

    NONNUL = str.maketrans('', '', '\x00') # delete NUL character

    headline = next(ins)
    headline = headline.lstrip('\ufeff') # sigh

    data = csv.reader(chain([headline], map(lambda s : s.translate(NONNUL), ins)),
                      delimiter = ',;'[';' in headline])
    head = next(data, [])
    if head == THEAD:
        ship_thread(data, ous)
    elif head in (CHEAD, CHEAD_2023):
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

ESC_META = str.maketrans({
    # '<' : '&lt;',
    # '>' : '&gt;',
    # '&' : '&amp;',
    '"' : '&quot;',
})

def esc_meta(value):
    # should not this come from some library? maybe not - corpus
    # specific what is already entified and what is entified here
    return value.translate(ESC_META)

ESC_DATA = str.maketrans({
    # to be used _after_ breaking paragraphs at <br /><br />, when
    # some stray < and > still remain to be encoded; cannot also
    # replace & because many such characters are already encoded! so
    # use another mechanism (re.sub) to replace &
    '<' : '&lt;',
    '>' : '&gt;'
})

def esc_data(value):
    '''Replace & with &amp; unless the & already starts &amp; or &lt; or
    &gt; (so this is quite rather brittle, hope value is as expected),
    then replace any <, > with &lt;, &gt; (also brittle! do not use
    this function too early!)

    '''
    value = re.sub(r'&(?!amp;|lt;|gt;)', '&amp;', value)
    return value.translate(ESC_DATA)

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
    #
    # attributes['topics/'] = (
    #    '|'
    #    + '|'.join(re.split(r',(?=\S)', TOPICS))
    #    + '|'
    # ) if TOPICS else '|'

    # On second thought, maybe topics was not meant to be multivalued
    # but a "super > sub" sequence? That be done so, with ">" already
    # as "&gt;" everywhere so the ampersand will not be re-escaped.
    # (Later further renamed to topic_names.)
    attributes['topic_names'] = ' &gt; '.join(re.split(r',(?=\S)', TOPICS))

    attributes.update(datetime_attributes(CREATED))

    ship_meta('text', attributes, ous)

    # paragraph number?
    # type is head? or title?
    # need escaping? yes, there are bare & in these

    print('<paragraph type="head">', file = ous)
    print(esc_data(TITLE.replace('&quot;', '"') or '_'), file = ous)
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
        print(esc_data(para), file = ous)
        print('</paragraph>', file = ous)

def fix(data):
    '''Called with FIXING == args.fix, hopefully repair character problems
    (observed in s24-2018-2020 data) if args.fix, else just return data.

    The minimum contract is to make prohibited characters go away. If
    this cannot be done sensibly, introduce some minor nonsense, or it
    is more likely to be GIGO.

    '''
    if FIXING:
        data = remove_internal_shy(data)
        return data.translate(character_fixes)
    return data

def remove_internal_shy(data):
    '''Remove U+00AD between letters (including digits and underscores,
    because why not and it was easier that way). Vastly many SHY are
    either compound boundaries or full syllabification, presumably
    invisible to a reader of the message, and otherwise potentially
    problematic.

    Also remove U+00AD after a space or a hyphen, or before a space or
    a hyphen (some occur as both). Is there any explanation for such?

    Some (few) double SHY were spotted, so remove runs.

    '''

    if '\xad' not in data: return data # premature optimization
    data = re.sub(r'(?<=\w)\xad+(?=\w)', '', data)
    data = re.sub(r'(?<=[\s\-])\xad+|\xad+(?=[\s\-])', '', data)

    return data

character_fixes = str.maketrans({
    # Translations based on observing the occurrences in
    # comments_2018 first, then also on the other files.
    #
    # Translations of LS and PS introduce new "<br />".

    '\u0001' : None, # delete C0 SOH ^A
    '\u0002' : None, # delete C0 STX ^B (cannot help)
    '\u0003' : None, # delete C0 ETX ^C (garbage, cannot help)
    '\u0004' : None, # delete C0 EOT ^D (garbage, cannot help)
    '\u0005' : None, # delete C0 ENQ ^E (garbage, cannot help)
    '\u0006' : None, # delete C0 ACK ^F (garbage, cannot help)
    '\u0007' : None, # delete C0 BEL ^G (garbage, cannot help)
    '\u0008' : None, # delete C0 BS ^H
    '\u000B' : None, # delete C0 VT ^K (cannot help)
    '\u000C' : None, # delete C0 FF ^L (garbage, cannot help)
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
    '\u001B' : '\u241B', # replace C0 ESC with control picture (2023)
    '\u001C' : None, # delete C0 FS (2023)
    '\u001D' : None, # delete C0 GS ^]
    '\u001E' : None, # delete C0 RS ^^
    '\u001F' : None, # delete C0 US ^_

    '\u007F' : None, # delete DEL

    # C1 : Windows-1252 from Wikipedia
    # https://en.wikipedia.org/wiki/Windows-1252
    '\u0080' : 'U+0080', # C1 PAD : GIGO (€ makes no sense)
    '\u0081' : None, # delete (one) C1 HOP (not in Windows-1252)
    '\u0082' : None, # delete C1 BPH (‚ makes no sense)
    '\u0083' : None, # delete C1 NBH (ƒ makes no sense)
    '\u0084' : 'U+0084', # C1 IND : GIGO („ makes no sense)
    '\u0085' : '\u2026', # C1 NEL : … (HORIZONTAL ELLIPSIS)
    '\u0086' : 'U+0086', # C1 SSA : GIGO († makes no sense)
    '\u0089' : None, # delete C1 HTJ (‰ makes no sense)
    '\u008A' : '\u0160', # C1 LTS : Š (S with caron, blindly in 2023, once)
    '\u0090' : 'U+0090', # C1 DCS : GIGO (not in Windows-1252)
    '\u0091' : '\u2018', # C1 PU1 : ‘ (once, twice)
    '\u0092' : '\u2019', # C1 PU2 : ’
    '\u0093' : '\u201C', # C1 STS : “
    '\u0094' : '\u201D', # C1 CCH : ”
    '\u0095' : '\u2022', # C1 MW : • (bullet, used to mask the letters in a vulgar word in 2023)
    '\u0096' : '\u2013', # C1 SPA : – (en dash)
    '\u0097' : '\u2014', # C1 EPA : — (em dash, blindly in 2023, once)
    '\u009A' : '\u0161', # C1 SCI : š (s with caron, blindly in 2023, once)
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

    # The *only* nonchar (of 66 possible) in this data, occurs in word
    # forms in what seems to be copy-paste, and seems removable.
    '\uFFFE' : None,

    # Private codes.
    '\uF04A' : '(private+F04A)', # times in 2021-2023: 10
    '\uF071' : '(private+F071)', # times in 2021-2023: 12
    '\uF095' : '(private+F095)', # times in 2021-2023: 12
    '\uF0C5' : '(private+F0C5)', # times in 2021-2023: 13
    '\uF0B7' : '(private+F0B7)', # times in 2021-2023: 148
    '\uF02B' : '(private+F02B)', # times in 2021-2023: 15
    '\uF0D8' : '(private+F0D8)', # times in 2021-2023: 19
    '\U00100B35' : '(private+100B35)', # times in 2021-2023: 1
    '\uE002' : '(private+E002)', # times in 2021-2023: 1
    '\uE007' : '(private+E007)', # times in 2021-2023: 1
    '\uE00A' : '(private+E00A)', # times in 2021-2023: 1
    '\uE00B' : '(private+E00B)', # times in 2021-2023: 1
    '\uE019' : '(private+E019)', # times in 2021-2023: 1
    '\uE01B' : '(private+E01B)', # times in 2021-2023: 1
    '\uE01C' : '(private+E01C)', # times in 2021-2023: 1
    '\uE092' : '(private+E092)', # times in 2021-2023: 1
    '\uE099' : '(private+E099)', # times in 2021-2023: 1
    '\uE09A' : '(private+E09A)', # times in 2021-2023: 1
    '\uE09B' : '(private+E09B)', # times in 2021-2023: 1
    '\uE09C' : '(private+E09C)', # times in 2021-2023: 1
    '\uE292' : '(private+E292)', # times in 2021-2023: 1
    '\uE715' : '(private+E715)', # times in 2021-2023: 1
    '\uE8C8' : '(private+E8C8)', # times in 2021-2023: 1
    '\uF017' : '(private+F017)', # times in 2021-2023: 1
    '\uF02A' : '(private+F02A)', # times in 2021-2023: 1
    '\uF02F' : '(private+F02F)', # times in 2021-2023: 1
    '\uF057' : '(private+F057)', # times in 2021-2023: 1
    '\uF058' : '(private+F058)', # times in 2021-2023: 1
    '\uF05E' : '(private+F05E)', # times in 2021-2023: 1
    '\uF061' : '(private+F061)', # times in 2021-2023: 1
    '\uF073' : '(private+F073)', # times in 2021-2023: 1
    '\uF074' : '(private+F074)', # times in 2021-2023: 1
    '\uF0E8' : '(private+F0E8)', # times in 2021-2023: 1
    '\uF8FF' : '(private+F8FF)', # times in 2021-2023: 1
    '\uE008' : '(private+E008)', # times in 2021-2023: 210
    '\uF0A7' : '(private+F0A7)', # times in 2021-2023: 23
    '\uF007' : '(private+F007)', # times in 2021-2023: 29
    '\U00100B36' : '(private+100B36)', # times in 2021-2023: 2
    '\uE001' : '(private+E001)', # times in 2021-2023: 2
    '\uE814' : '(private+E814)', # times in 2021-2023: 2
    '\uF070' : '(private+F070)', # times in 2021-2023: 2
    '\uF279' : '(private+F279)', # times in 2021-2023: 2
    '\uF041' : '(private+F041)', # times in 2021-2023: 31
    '\uF0A1' : '(private+F0A1)', # times in 2021-2023: 31
    '\uF0FC' : '(private+F0FC)', # times in 2021-2023: 36
    '\uF0E0' : '(private+F0E0)', # times in 2021-2023: 38
    '\uE014' : '(private+E014)', # times in 2021-2023: 3
    '\uE01E' : '(private+E01E)', # times in 2021-2023: 3
    '\uE61F' : '(private+E61F)', # times in 2021-2023: 3
    '\uF063' : '(private+F063)', # times in 2021-2023: 3
    '\uF109' : '(private+F109)', # times in 2021-2023: 3
    '\U00100191' : '(private+100191)', # times in 2021-2023: 4
    '\uE000' : '(private+E000)', # times in 2021-2023: 4
    '\uF06C' : '(private+F06C)', # times in 2021-2023: 5
    '\uF072' : '(private+F072)', # times in 2021-2023: 5
    '\uF02D' : '(private+F02D)', # times in 2021-2023: 6

    # BiDi: overrides to be avoided where possible, embeddings
    # discouraged since 2013 (in favour of isolates), and there is a
    # likelihood of abuse - indeed *all* LRE and LRO seem merely
    # redundant in 2021-2023, and the *one* RLO *might* be a correct
    # use but also is potentially dangerous when tokenized; after
    # ocular inspection threatened to never end, removing all of these
    # as harmless at best (even the appropriate uses seem to be around
    # RTL characters that arrange themselves, large number of odd uses
    # are setting even a single character to LTR in LTR context,
    # typically LRO-PDF pairs in Bible references, and LRM is either
    # thoroughly redundant or just too weird, as itemizing some list
    # or what? let them go now)
    '\u200E' : None, # '(LRM)', # 3140 of these - LR, why should one need these?
    '\u200F' : None, # '(RLM)', # 249 of these - should one be worried?
    '\u202A' : None, # '(LRE)', # discouraged since 2023, yet 82 in 2021-2023
    '\u202C' : None, # '(PDF)', # pop? 1229 of these
    '\u202D' : None, # '(LRO)', # avoided where possible, yet 1301 in 2021-2023
    '\u202E' : None, # '(RLO)', # avoided where possible, just 1 in 2021-2023
    '\u2066' : None, # '(LRI)', # 36 of these - LR, why should one need these?
    '\u2069' : None, # '(PDI)', # 24 of these - to pop LRI?
})
