'''A vrt tool implementation to write text elements to different files
based on the value of a specified text attribute. Initially just
separation by a language summary is implemented, but options to use a
different attribute or a different interpretation of that attribute
can be added. The attribute handler should then return a component of
a file name where the text element is then written. Note that all
output files be open at the same time - maybe best not to have like
millions of them? or even hundreds. (Around 150 worked fine in Puhti.)

Any markup lines outside text elements are discarded. This breaks the
VRT format if some such markup starts outside and ends inside a text
element, or starts inside and ends outside, where "outside" may also
be inside a different text element that ends up in a different file.
Please do not have such markup.

'''

from itertools import chain, count
from re import search, findall, fullmatch, ASCII

import os

from libvrt.args import multiput2_args, BadData
from libvrt.elements import text_elements
from libvrt.metaline import mapping
from libvrt.dataline import unescape

# hm libvrt.metaname appears to have similar so one is once again
# duplicating one's efforts?
from libvrt.nameargs import nametype, prefixtype, suffixtype

def parsearguments(argv, *, prog = None):

    description = '''

    Partitions VRT input stream into VRT output files based on text
    attributes. Each text element goes to an output file
    "stem-tag.vrt" where "tag" depends on an interpretation of some
    text attributes. Markup outside text elements is discarded.

    First partition criterion was to account for the majority language
    codes of the sentences, together with any fin, swe, eng, in a text
    element. Second is an attempted to partition by publication year,
    based on a number of attributes that might contain a year.

    '''

    parser = multiput2_args(description = description)

    parser.add_argument('--attr', '-a', metavar = 'spec',
                        type = str.encode,
                        help = '''

                        text attributes on which to partition
                        (interpreted by the particular method)

                        ''')

    method = parser.add_mutually_exclusive_group(required = True)
    method.add_argument('--klk-main-lang', action = 'store_true',
                        help = '''

                        tag by majority language codes and any fin,
                        swe, eng in a summary attribute (sum_lang,
                        unless specified with --attr option)

                        ''')
    method.add_argument('--klk-year', action = 'store_true',
                        help = '''

                        tag by publication year, extracted from
                        datefrom, date, or issue_date attribute
                        (ignores --attr option)

                        ''')

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    if args.stem:
        pass
    elif args.infile is None:
        args.stem = 'stdin'
    else:
        args.stem, *_ = os.path.basename(args.infile).split('.')

    if not fullmatch(r'\w[\w\-]*', args.stem, ASCII):
        raise ValueError('not a stem: {}'.format(repr(args.stem)))

    return args

def main(args, ins, outdir):
    '''Transput text elements of VRT (bytes) in ins to VRT (bytes) in
    different output files depending on args.

    Output files are sibling to input file if named, else in current
    working directory. Output filename stem defaults to input filename
    stem or "stdin" (override "stdin" if not happy with "stdin").

    Output filenames are path/stem-tag.vrt, tagged by the chosen
    partition function (presumably implemented below).

    '''

    tmpname = os.path.join(outdir, '{}-{{}}.vrt.tmp'.format(args.stem))
    outname = os.path.join(outdir, '{}-{{}}.vrt'.format(args.stem))

    # find the positional-attributes line
    # - must be before any text element (as well as before any data line)
    # - discard any preceding lines as being outside text elements
    head = None
    for line in ins:
        if not line.startswith(b'<'):
            raise BadData('data line before positional-attributes line')
        if line.startswith((b'<text>', b'<text ')):
            raise BadData('text element start before positional-attributes line')
        if line.startswith(b'<!-- #vrt positional-attributes: '):
            head = line
            break

    # print('field name line:', head)
    # print('tmpname pattern:', tmpname)
    # print('outname pattern:', outname)
    # print('args.tag:', args.tag)

    # set partition method according to the options
    method = (
        klk_main_lang if args.klk_main_lang else
        klk_year if args.klk_year else
        None # this cannot happen: method group is required in args
    )

    outstreams = dict() # an open output stream for each tag seen so far
    for group in text_elements(ins, open(os.devnull, mode = 'wb'),
                               as_text = False):
        # lines outside any text element are discarded
        # lines inside are shipped to different files
        line = next(group)
        tag = method(line, args) # get file-name component from text start line
        # print('would write to:', tmpname.format(tag))

        # opener opens tmpname.format(tag) if it that is not already
        # in outstreams; otherwise raises FileExistsError on tmpname
        # or outname existing
        ous = opener(outstreams, tag, head, tmpname, outname)
        ous.write(line)
        for line in group:
            ous.write(line)

    # finish each output file
    for tag, ous in outstreams.items():
        ous.close()

        if os.path.exists(outname.format(tag)):
            raise FileExistsError(outname.format(tag))

        # os.rename might raise FileExistsError (since Python 3.3 or
        # so) if the target file already exists - this is the desired
        # behaviour - but apparently does not do so in Linux systems

        os.rename(tmpname.format(tag),
                  outname.format(tag))

def klk_main_lang(line, args):
    '''Extract a file-name component from the args.attr (sum_lang) in the
    line - this is a possible (initially the only) "part" function in
    the main loop - assume decreasing count for language codes, ignore
    any xxx or und, then take most frequent language, with any ties,
    and the languages generally of most interest to the Language Bank
    of Finland (those being fin, swe, eng).

    '''

    # expecting b'wev=10,xxx=10,etc=8' syntax,
    # or was it b'|wev:10|xxx:10|etc:8|' -
    # allow both! or some other punctuation.
    # (language codes consist of ASCII letters,
    # their counts consist of ASCII digits, ok)

    meta = mapping(line)
    counts = meta[args.attr or b'sum_lang']

    proper = [
        (lang, int(freq.decode('UTF-8')))
        for lang, freq in findall(br'(\w+)[:=](\d+)', counts)
        if not lang in (b'xxx', b'und')
    ]

    if not proper:
        # no proper language identified in any text sentence,
        # so in particular no proper most frequent language
        return 'und'

    most, *rest = proper
    top, top_freq = most

    # keep the most frequent code and those tied with it,
    # and any language of main interest in this corpus
    # (rather arbitrary, but is the job of this function)

    result = [
        code for code, freq in proper
        if (
                freq == top_freq or
                code in (b'fin', b'swe', b'eng')
        )
    ]

    return b'-'.join(result).decode('UTF-8')

def klk_year(line, args):
    '''Return a best publication year from line, which is the start tag of
    a text element. Ignore args. This attempt to interpret KLK
    attributes may be somewhat opaque to the user, but the result
    should alway be a sequence of four digits. Say, 0000 for no valid
    year found? And otherwise slightly heuristic due to the variation
    and incompleteness in the attributes.

    '''
    # extract the attributes
    meta = mapping(line)

    # extract a year (or fall on "0000")
    YYYY_MM_DD = b'(?x: ( [0-9]{4} ) (?: - [0-9]{2} (?: - [0-9]{2} )? )? )'
    DD_MM_YYYY = b'(?x: (?: [0-9]{2} [.] (?: [0-9]{2} [.] )? )? ( [0-9]{4} ) )'
    YYYYMMDD = b'(?x: ( [0-9]{4} ) [0-9]{4} )'
    year = (
        # datefrom="19230401"
        fullmatch(YYYYMMDD, meta.get(b'datefrom', b''))
        or
        # date="_" but no year there
        # date="1923"
        # date="1923-04"
        # date="1923-04-01"
        # date="04.1923"
        # date="01.04.1923"
        fullmatch(YYYY_MM_DD, meta.get(b'date', b'')) or
        fullmatch(DD_MM_YYYY, meta.get(b'date', b''))
        or
        # issue_date="01.04.1923"
        # issue_date="04.1923"
        # issue_date="1923"
        # or ... can be (yyyy[-mm[-dd]]) so ... act accordingly
        fullmatch(YYYY_MM_DD, meta.get(b'issue_date', b'')) or
        fullmatch(DD_MM_YYYY, meta.get(b'issue_date', b''))
        or
        # found no year, find "0000" as a fallback
        fullmatch(b'(0000)', b'0000')

    ).group(1)
    return year.decode()

def opener(streams, tag, head, tmpname, outname):
    '''Return the output stream that points to an output file with "tag"
    in its name.

    Open a new file if one is not already open (not already in
    streams). Then write "head" (positional attributes) to that file.

    '''
    if tag not in streams:
        if os.path.exists(outname.format(tag)):
            raise FileExistsError(outname.format(tag))

        # mode 'x' means to open a *new* file for writing,
        # else to raise FileExistsError
        streams[tag] = open(tmpname.format(tag), 'bx')
        streams[tag].write(head)

    return streams[tag]
