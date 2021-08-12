# -*- mode: Python; -*-

'''Implementation of hrt-from-s24-2020.'''

from libvrt.args import BadData
from libvrt.args import transput_args

import csv
import re

def parsearguments(argv, *, prog = None):

    description = '''

    Process input like the 2021 dump of Suomi24 into HRT form (after
    dealing with the few NUL bytes in the dump that the Python CSV
    reader would not deal with).

    '''

    parser = transput_args(description = description,
                           inplace = False)
    
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

def main(args, ins, ous):
    '''Transput input stream (database dump) in ins to HRT in ous.

    There would be a head line followed by record lines, either thread
    starters or comments.

    '''

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

    '''

    # paragraph number?
    # paragraph type? (shipping now)

    body = body.replace('&quot;', '"')
    for para in re.split('<br /><br />', body):
        print('<paragraph type="body">', file = ous)
        print(para.replace('<br />', '\n'), file = ous)
        print('</paragraph>', file = ous)
