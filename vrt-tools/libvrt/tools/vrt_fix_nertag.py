# -*- mode: Python; -*-

'''Implement vrt-fix-finnish-nertag.

Fix a specific, quite rare, issue in vrt-finnish-nertag output,
require fields for all three formats. Apparently the issue comes from
finnish-nertag omitting a tab between first two levels in certain
three-deep nestings, resulting in >< in nertag, nertags between the
longest, second-longest start tags, and nerbio class taken from the
second level instead of the first.

'''

brokentag = {
    # start tag correction
    b'EnamexOrgCrp><EnamexLocPpl-B' :
    b'EnamexOrgCrp-B',
    
    b'_' : b'_', # there are no proper inside tags

    # end tag is already correct
    b'EnamexOrgCrp-E' :
    b'EnamexOrgCrp-E' 
}

brokentags_2 = {

    # correct level 2 start tags when there are further level 2 words
    b'|EnamexOrgCrp><EnamexLocPpl-B-0|EnamexLocPpl-B-1|' :
    b'|EnamexOrgCrp-B-0|EnamexLocPpl-B-1|EnamexLocPpl-B-2|',

    # correct level 2 start tags when there is only one level 2 word
    b'|EnamexOrgCrp><EnamexLocPpl-B-0|EnamexLocPpl-F-1|' :
    b'|EnamexOrgCrp-B-0|EnamexLocPpl-B-1|EnamexLocPpl-F-2|',

    # correct level 2 end tags (encountered before level 1)
    b'|EnamexLocPpl-E-1|' :
    b'|EnamexLocPpl-E-2|',

    b'|' : b'|' # there are no proper inside tags
}
brokentags_1 = {

    # level 1 end tags are already correct
    b'|EnamexLocPpl-E-1|' :
    b'|EnamexLocPpl-E-1|',

    b'|' : b'|' # there are no proper inside tags
}
brokentags_0 = {

    # level 0 end tags are already correct
    b'|EnamexOrgCrp-E-0|' :
    b'|EnamexOrgCrp-E-0|',

    b'|' : b'|' # there are no proper inside tags
}
brokenbio = {
    b'B-LOC' : b'B-ORG', # start tag correction
    b'I-LOC' : b'I-ORG', # inside tag correction
    b'I-ORG' : b'I-ORG'  # end tag is already correct
}

from itertools import chain, filterfalse, islice
import sys, traceback

from libvrt.args import transput_args
from libvrt.bad import BadData, BadCode
from libvrt.dataline import record
from libvrt.nameargs import nametype
from libvrt.nameline import isnameline, parsenameline

def parsearguments():
    description = '''

    Fix a rare issue in the output of vrt-finnish-nertag (using
    finnish-nertag 1.6) where a missing tab between first and second
    levels of three levels of tags has resulted in first level
    EnamexOrgCrp><EnamexLocPpl and EnamexLocPpl as second level, with
    concomitant other issues.

    The input must have all three formats from vrt-finnish-nertag.

    '''

    parser = transput_args(description = description)

    parser.add_argument('--tag', metavar = 'name',
                        default = 'nertag2',
                        type = nametype,
                        help = '''

                        max (longest level) tag field name (nertag2)

                        ''')

    parser.add_argument('--tags', metavar = 'name',
                        default = 'nertags2/',
                        type = nametype,
                        help = '''

                        all-level tags field name (nertags2/)

                        ''')

    parser.add_argument('--bio', metavar = 'name',
                        default = 'nerbio2',
                        type = nametype,
                        help = '''

                        bio tag field name (nerbio2)

                        ''')

    parser.add_argument('--mark', action = 'store_true',
                        help = '''

                        mark BIO tags in affected names with @> so
                        that B becomes @>B and I becomes @>I, for
                        paste of input and output, then grep of the
                        relevant lines, for ocular inspection
                        
                        ''')

    args = parser.parse_args()
    args.prog = parser.prog
    return args

def main(args, ins, ous):

    head = tuple(islice(ins, 100))
    for line in head:
        if not isnameline(line):
            continue
        names = parsenameline(line, required =
                              (args.tag, args.tags, args.bio))
        break
    else:
        raise BadData('no field names found in first 100 lines')

    # broke out of head so names were found
    TAG = names.index(args.tag)
    TAGS = names.index(args.tags)
    BIO = names.index(args.bio)

    # to facilitate the inspection of the transformation,
    # intentionally not allowed in final VRT
    def mark(tag): return b'@>' + tag if args.mark else tag

    def fixin2(rec):
        '''Fix and ship a word in level 2 (the shortest name). Return True if
        the corrected word ends level 2.

        '''
        # print('### enter fixin2', *map(bytes.decode, rec))
        [ rec[TAG], rec[TAGS], rec[BIO] ] = (
            brokentag[rec[TAG]], brokentags_2[rec[TAGS]], mark(brokenbio[rec[BIO]]) )

        ous.write(b'\t'.join(rec))
        ous.write(b'\n')
        return rec[TAGS].endswith((b'-F-2|', b'-E-2|'))

    def fixin1(rec):
        '''Fix and ship a word in level 1 after level 2. Return True if the
        corrected word ends level 1.

        '''
        # print('### enter fixin1', *map(bytes.decode, rec))
        [ rec[TAG], rec[TAGS], rec[BIO] ] = (
            brokentag[rec[TAG]], brokentags_1[rec[TAGS]], mark(brokenbio[rec[BIO]]) )

        ous.write(b'\t'.join(rec))
        ous.write(b'\n')
        return rec[TAGS].endswith(b'-E-1|')

    def fixin0(rec):
        '''Fix and ship a word in level 0 after level 1. Return True if the
        corrected word ends level 0.

        '''
        # print('### enter fixin0', *map(bytes.decode, rec))
        [ rec[TAG], rec[TAGS], rec[BIO] ] = (
            brokentag[rec[TAG]], brokentags_0[rec[TAGS]], mark(brokenbio[rec[BIO]]) )

        ous.write(b'\t'.join(rec))
        ous.write(b'\n')
        return rec[TAGS].endswith(b'-E-0|')

    lines = chain(head, ins)
    while True:
        line = next(lines, None)
        if line is None: break
        if b'><' in line:
            # this line starts one of those names, so read, process,
            # and ship records until and including the record that
            # contains the level-0 end tag
            if not fixin2(record(line)):
                while not fixin2(record(next(lines))): pass
            while not fixin1(record(next(lines))): pass
            while not fixin0(record(next(lines))): pass
        else:
            ous.write(line)

    return 0
