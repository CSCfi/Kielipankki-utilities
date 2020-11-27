# -*- mode: Python; -*-

'''Implement pr1 for vrt-finnish-nertag.

'''

from itertools import groupby
from subprocess import Popen, PIPE
import html, re, sys

from libvrt.args import transput_args
from libvrt.bad import BadData, BadCode
from libvrt.pr1 import transput

def _name(arg): return arg.encode('UTF-8')

def parsearguments(argv):
    description = '''

    Annotate tokens with FiNER, the Finnish name classifier.

    '''
    parser = transput_args(description = description)

    parser.add_argument('--word', '-w', metavar = 'name',
                        default = 'word',
                        type = _name,
                        help = '''

                        input field name ("word")

                        ''')
    parser.add_argument('--tag', '-t', metavar = 'tag',
                        # default depends on args.form
                        type = _name,
                        help = '''

                        output field name ("nertag" for --max,
                        "nertags/" for --all, "nerbio" for --bio)

                        ''')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--max', action = 'store_const',
                       dest = 'form', const = 'max',
                       help = '''

                       annotate maximal names

                       ''')
    group.add_argument('--all', action = 'store_const',
                      dest = 'form', const = 'all',
                      help = '''

                      annotate all ways that names overlap

                      ''')
    group.add_argument('--bio', action = 'store_const',
                       dest = 'form', const = 'bio',
                       help = '''

                       annotate maximal names in Begin/In/Out format

                       ''')
    parser.set_defaults(form = 'all')

    args = parser.parse_args(argv)

    # default depends on args.form so here goes
    args.tag = args.tag or dict(max = b'nertag',
                                all = b'nertags/',
                                bio = b'nerbio')[args.form]
    args.prog = parser.prog
    return args

def main(args, ins, ous):

    # when working where there is no finnish-nertag
    fake = [ 'python3', 'fake-nertag.py',
             dict(max = '--max',
                  all = '--all',
                  bio = '--bio')[args.form] ]
    real = [ 'finnish-nertag',
             *dict(max = [],
                   all = [ '--show-nested' ],
                   bio = [ '--bio' ])[args.form] ]
    proc = Popen(real,
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = None)

    return transput(args, sys.modules[__name__], proc, ins, ous)

WORD = None
FORM = None

def pr1_init(args, old):
    '''Return new names. Establish the context for the protocol (in this
    case, just the field index WORD).

    '''
    global WORD, FORM

    if args.word not in old:
        raise BadData('no such field: {}'
                      .format(repr(args.word.decode('UTF-8'))))

    if args.tag in old:
        raise BadData('already such field: {}'
                      .format(args.tag.decode('UTF-8')))

    WORD = old.index(args.word)
    FORM = args.form

    new = old[:]
    new.insert(WORD + 1, args.tag)
    return new

def _attr(tag, attr):
    '''The value of the attr in the tag. Defaults to b"".
    (This function might belong to some library or other.)

    '''
    for a, v in re.findall(b' ([^" ]+)="([^"]*)"', tag):
        if a == attr: return v
    return b''

class _state: now = True
def pr1_test(*, meta = (), tags = ()):
    '''Establish whether to send the next sentence to the external tool.
    The current plan is to skip any sentence element with the value
    "finnish-nertag" in the multi-valued attribute _skip.

    '''
    for tag in tags:
        if tag == b'</sentence>\n':
            _state.now = True
        elif ( tag.startswith(b'<sentence ') and
               b'|finnish-nertag|' in _attr(tag, b'_skip') ):
            _state.now = False
        else: pass
    else:
        return _state.now

def pr1_send(sentence, proc):
    '''Write the sentence (an iterator of token records) to the external
    process in the desired format (in this case, just each "word" on
    their own lines, followed by an empty line).

    '''
    for record in sentence:
        # unescape the word
        proc.stdin.write(record[WORD]
                         .replace(b'&lt;', b'<')
                         .replace(b'&gt;', b'>')
                         .replace(b'&amp;', b'&'))
        proc.stdin.write(b'\n')
    else:
        proc.stdin.write(b'\n')

def pr1_read(ins):
    '''Return a reader of sentences (iterators of token records) from the
    external process, one sentence at a time (in this case, a sequence
    of non-empty lines, with empty lines between sentences).

    This reader produces annotations for each token as a list of tags,
    empty when there is none.
    '''
    for kind, group in groupby(ins, bytes.isspace):
        if not kind:
            yield (
                # word tab tab-separated-tags => tags
                # where there may be leading empties
                # before actual tags
                line.rstrip(b'\t\r\n').split(b'\t')[1:]
                for line in group
            )

def rewrite(tag, depth = None):
    '''Rewrite XML-like tags into a more friendly format (when used as
    annotations on tokens rather than structural markup). Preserve the
    "depth" aka position among nested annotations, indicated by depth
    is not None.

    '''

    # tentative rewriting may change yet

    ds = (b'' if depth is None else b'-' + bytes(str(depth), 'UTF-8'))

    if tag.startswith(b'</'):
        return tag.strip(b'</>') + b'-E' + ds # End a name
    elif tag.endswith(b'/>'):
        return tag.strip(b'</>') + b'-F' + ds # Full name
    else:
        return tag.strip(b'<>') + b'-B' + ds # Begin a name

def pr1_join(old, new, ous):
    if FORM == 'max':
        # new is either [ b'<SomeTag>' ] or [ ]
        # because reader above strips empties
        # which maybe was not a right idea?
        new = (rewrite(*new) if new else b'_')
    elif FORM == 'all':
        # TODO somehow make sure this does the right thing
        # there may be leading empty tag fields before a
        # proper tag
        new = ( b'|'.join((b'',
                           *(rewrite(tag, depth) for
                             depth, tag in enumerate(new)
                             if tag),
                           b''))
                if new
                else b'|'
        )
    elif FORM == 'bio':
        # new is [ b'BIOTAG' ]
        # so there should never be a bar or a WHAT
        new = b'|'.join(new) or b'WHAT'
    else:
        # *this cannot happen*
        new = repr(FORM).encode('UTF-8')

    ous.write(b'\t'.join((*old[:WORD + 1],
                          new,
                          *old[WORD + 1:])))
    ous.write(b'\n')

def pr1_keep(old, ous):
    ous.write(b'\t'.join((*old[:WORD + 1],
                          (b'_', b'|')[FORM == 'all'],
                          *old[WORD + 1:])))
    ous.write(b'\n')
