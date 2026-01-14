# -*- mode: Python; -*-

'''Implementation of vrt-from-sparv-xml.'''

import re, sys
from itertools import chain, islice

from libvrt.args import BadData
from libvrt.args import transput_args

from libvrt.metaname import nametype_txt

def parsearguments(argv, *, prog = None):

    description = '''

    Translate the XML annotated with Sparv (or Stanza at least) back
    to VRT (line by line). Attributes in the VRT are named and ordered
    as in the XML, except input annotations to tokens are pushed to
    the end, assuming the input prefix is specified truthfully. Note
    that the XML cannot end any attribute name with a slash.

    '''

    parser = transput_args(description = description,
                           inplace = False)


    parser.add_argument('--document', metavar = 'name',
                        type = nametype_txt,
                        default = 'whatever',
                        help = '''

                        name of the document element in the XML, to be
                        skipped [whatever]

                        ''')

    parser.add_argument('--inprefix', metavar = 'prefix',
                        type = nametype_txt,
                        default = '_in_.',
                        help = '''

                        prefix of attribute names that were in the
                        input to Stanza (or another Sparv annotator,
                        maybe), only used to push the input
                        annotations of tokens to the end [_in_.]

                        ''')

    parser.add_argument('--token', '-t', metavar = 'name',
                        type = nametype_txt,
                        default = 'token',
                        help = '''

                        name of the token element in the XML [token]

                        ''')

    parser.add_argument('--word', '-w', metavar = 'name',
                        type = nametype_txt,
                        default = 'word',
                        help = '''

                        name for the word field in the VRT [word]

                        ''')

    args = parser.parse_args()
    args.prog = prog or parser.prog

    return args

# - make Kielipankki vrt from Sparv xml after Stanza
# - counterpart to a vrt-to-spart-xml (TODO from .py script)
# - WATCH OUT assume the xml is equally line-oriented! (!)
# - OBSOLETE read one xml, write corresponding vrt as sibling
# - (eventually could read many xml, or stdin, now keep simple)
# - TODO was there some escaping to unescape?
# - TODO yes, there was! &apos; and &quot; in token annotations
# - TODO mainly or only baseform, but why only &quot; occurs?
# - TODO seems apostrophes fail to be escaped, how can that be?
# - TODO perhaps Sparv has undone &apos; already?

def main(args, ins, ous):
    # read ahead to find field names
    # reify to be able to read again
    head = tuple(islice(ins, 100))
    token = next(line.strip() for line in head
                 if line.strip().startswith(('<token ', '<token>')))
    # found a first token line
    # else would have crashed
    start, word = (
        re.fullmatch(r'(<token.*?>)(.*?)</token>', token).groups()
    )
    # wonder how brittle the following might be
    # it assumes space before name,
    # no space before equals
    # and double quotes
    # all of which we do enfore in vrt
    names = re.findall(r' (\S+?)=".*?"', start)
    namesout = tuple(name for name in names if not name.startswith(args.inprefix))
    namesin = tuple(name for name in names if name.startswith(args.inprefix))
    # the names parameter will control the *order* of the output
    # fields, though the order does seem consistent throughout the
    # xml, and also facilitate checking that they are always there;
    # ship the output fields first after token itself, then input,
    # leave the stripping of the input prefix, slashing of multi-value
    # attribute names, and the final order for post-processing
    print('<!-- #vrt positional-attributes:',
          args.word,
          *namesout,
          *namesin,
          '-->',
          file = ous)
    process(args, chain(head, ins), ous,
            names = namesout + namesin)

def process(args, ins, ous, *, names):
    DOC = (args.document, '/' + args.document)
    # expected in each LINE: element name, attributes, possibly
    # followed by a token; in end tags, "/name" counts as "name" and
    # the optional parts are hopefully not there (not checked?)
    LINE = fr'<(/?[\w\-.]+)((?: [\w\-.]+?=".*?")*)>(.+?</{args.token}>)?'
    TOKEN = fr'(.+?)</{args.token}>'
    # self-closing element, which should not exist but somehow
    # sometimes do; log in stderr, expand for post-processing
    EMPTY = r'<(([\w\-.]+)(?: [\w\-.]+?=".*?")*) ?/>'
    def unescape(mo):
        entity = mo.group(0)
        if entity == '&apos;': return "'"
        if entity == '&quot;': return '"'
        return entity
    for line in ins:
        if line.startswith('<?xml '):
            # ignore XML declaration
            continue
        mo = re.fullmatch(LINE, line.strip())
        if mo is None:
            emo = re.fullmatch(EMPTY, line.strip())
            if emo is None:
                # technically "token" might be something else, depending
                # on options, but let "token" stand in for args.token in
                # the error message
                raise(ValueError('expected <NAME[ ATTR="VAL"]*>[TEXT</token>],'
                                 + ' observed ' + line.strip()))
            # expand self-closing element to start tag, end tag
            print('expanding:', line.strip(),
                  file = sys.stderr)
            print(f'<{emo.group(1)}>',
                  f'</{emo.group(2)}>',
                  sep = '\n',
                  file = ous)
            continue
        name, attrs, tail = mo.groups()
        if name in DOC:
            # ignore document element tags
            continue
        if name == args.token:
            # extract actual token from the tail of the match
            token, = re.fullmatch(TOKEN, tail).groups()
            # parse attributes and ship their values in the order of
            # the names parameter; unescape &quot; and &apos; (though
            # it seems that Sparv has already unescaped any &apos;)
            pairs = dict((k, re.sub(r'&\w+;', unescape, v))
                         for k, v in re.findall(r'(\S+?)="(.*?)"', attrs))
            assert len(pairs) == len(names)
            print(token, *(pairs[k] for k in names),
                  sep = '\t',
                  file = ous)
            continue
        # the line has to be a sructure tag, to be shipped as is,
        # except input attribute names do have a prefix to strip
        # afterwards, and possibly slashes added
        print('<', name, attrs, '>', sep = '', file = ous)
    pass
