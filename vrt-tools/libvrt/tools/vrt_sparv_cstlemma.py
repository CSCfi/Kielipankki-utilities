# -*- mode: Python; -*-

'''New implementation of Swedish VRT lemmatizer, using the "pr1"
machinery, following pr1 test implementation and the old version of
vrt-sparv-cstlemma.

'''

from argparse import ArgumentTypeError
from itertools import groupby
from subprocess import Popen, PIPE
import codecs, re, sys

from libvrt.args import transput_args
from libvrt.bad import BadData, BadCode
from libvrt.pr1 import transput

try:
    from outsidelib import CSTLEMMA, CSTLEMMAMODELS
except ImportError as exn:
    # So it will crash when actually trying to launch the underlying
    # tool and CSTLEMMA is not defined, but --help and --version
    # options will work!
    print('Import Error:', exn, file = sys.stderr)

CSTFORMATOPTIONS = [
    # These CSTFORMAT options specify the input/output formats, not
    # including a separate character encoding option:

    # input is tagged, word TAB tag NL
    '-t',
    '-I', r'$w\t$t\n',

    # output is word TAB info TAB dictionary lemma TAB rule-based
    # lemma NL and lemmas turned out to be *sometimes* not UTF-8 (but
    # Latin-1?)  NEEDS INVESTIGATED BUT WORKAROUNDIT FOR NOW; note
    # that that was observed and workarounded for UTF-8 input/output
    # (-eU) to cstlemma before attempting to use the other encodings
    # because there were missing letters in UTF-8 output from it -
    # maybe it does not quite work?

    # From cstlemma -h for the option -c:
    #    $i info:  -    full form not in dictionary.
    #              +    full form has more than one lemma in the dictionary.
    #                   (If that is the case, the lemmatiser also generates lemma(s)
    #                   using the flex pattern rules, so you can choose.)
    #           (blank) full form in dictionary.
    '-c', '$w\t$i\t$b\t$B\n',
    '-b', '$w',
    '-B', '$w',

    # separate alternative lemmas with unit separator, U+001F, rather
    # than the default vertical pipe, because cannot prevent vertical
    # pipes from occurring in the input (it must be one argument: -s
    # alone is another option); will split cstlemma output at U+001F
    # and then replace any vertical bars, U+007C, in base forms with
    # broken vertical bars, U+00A6, and join alternative lemmas with
    # vertical bars (iso-8859-2 does not contain broken bar at all)
    R'-s\x1f',
]

CSTENCODING = {
    # $ cstlemma -h
    # -e<n> ISO8859 Character encoding. 'n' is one of 1,2,7 and 9 (ISO8859-1,2, etc).
    # -eU turns out to produce garbage (missing and malcoded letters)
    'Latin-1' : [ '-e1' ],
    'Latin-2' : [ '-e2' ],
    'Latin/Greek' : [ '-e7' ],
    'Latin/Turkish' : [ '-e9' ],
    'UTF-8' : [ '-eU' ]
}

def highlight_errors(exn):
    '''Handles UnicodeDecodeError. Because some but not all occurrences of
    the usual letters were mal-encoded in the output of cstlemma.

    '''

    bad = (
        codecs
        .encode(exn.object[exn.start:exn.end], 'hex')
        .decode('ASCII')
    )
    return '[UTF-8?{}]'.format(bad), exn.end

def interpret_errors(exn):
    '''Handles UnicodeDecodeError. Because some but not all occurrences of
    the usual letters were mal-encoded in the output of cstlemma.
    Interpret them in Latin-1.

    '''

    bad = exn.object[exn.start:exn.end]

    # only handle graphic characters
    if all(b > 0xa0 for b in bad):
        return bad.decode('iso-8859-1'), exn.end

    return highlight_errors(exn)

codecs.register_error('highlight', highlight_errors)
codecs.register_error('interpret', interpret_errors)

def fixutf8(args, word):
    '''Error handling according to args.strict or not args.strict, because
       cstlemma *seems* broken with -eU (possibly it is losing bytes
       rather than characters and sometimes just happens to lose the
       first byte of a double-byte UTF-8 character - or something else
       is happening that one just failed to understand properly).

    '''

    if STRICTUTF8: # set from args.strict
        word = word.decode('UTF-8', errors = 'highlight')
    else:
        word = word.decode('UTF-8', errors = 'interpret')

    return word.encode('UTF-8')

def _name(arg):
    # librarify this already!
    if re.fullmatch('[A-Za-z][A-Za-z0-9]*', arg):
        return arg.encode('UTF-8')
    raise ArgumentTypeError('bad name: {}'.format(repr(arg)))

def _setname(arg):
    # librarify this already!
    if re.fullmatch('[A-Za-z][A-Za-z0-9]*/', arg):
        return arg.encode('UTF-8')
    raise ArgumentTypeError('bad set-valued name: {}'.format(repr(arg)))

def parsearguments(argv):
    description = '''

    Lemmatize Swedish VRT: pass the word and msd fields in a VRT
    document through the CST lemmatizer with some model from SPARV,
    insert set-valued lemma field after word. Input VRT must have
    positional attribute names.

    '''
    parser = transput_args(description = description)

    parser.add_argument('--word', metavar = 'name',
                        default = 'word',
                        type = _name,
                        help = '''

                        input word field name ("word")

                        ''')
    parser.add_argument('--msd', metavar = 'name',
                        default = 'msd',
                        type = _name,
                        help = '''

                        input msd field name ("msd")

                        ''')
    parser.add_argument('--lemma', metavar = 'name',
                        default = 'lemma/',
                        type = _setname,
                        help = '''

                        output lemma field name ("lemma/"),
                        must end in "/"

                        ''')

    parser.add_argument('--origins', action = 'store_true',
                        help = '''

                        also output fields that show the internal
                        origins of the chosen lemma ("<lemma>.lookup"
                        and "<lemma>.dict/" report dictionary lookup
                        of the full form, "<lemma>.flex/" reports
                        rule-generated lemmas)

                        ''')

    # "verbose" option but rename it from --verbose

    parser.add_argument('--model',
                        choices = [ 'saldo', 'suc', 'sucsaldo' ],
                        default = 'saldo',
                        help = '''

                        lemmatisation models to use (saldo is based on
                        a huge list, suc on a short list; default is
                        to use saldo; sucsaldo combines both lists)

                        ''')

    parser.add_argument('--encoding',
                        choices = [
                            'Latin-1', 'Latin-2',
                            'Latin/Greek',   # iso-8859-7
                            'Latin/Turkish', # iso-8859-9
                            'UTF-8'
                        ],
                        default = 'Latin-1',
                        help = '''

                        internal re-encoding of input for cstlemma;
                        where not possible, surface form is used as
                        base form; the available encodings are
                        ISO-8859-1,2,7,9 as indicated in the help text
                        of cstlemma 7.36 (default is Latin-1, since
                        UTF-8 does not seem to work for all lemmas)

                        ''')

    parser.add_argument('--strict', action = 'store_true',
                        help = '''

                        highlight all invalid bytes in lemmas as
                        "[UTF-8?xx]" (default is to interpret hex
                        a0-ff as Latin-1)

                        ''')
    
    # TODO something about skipping sentences? maybe later

    args = parser.parse_args(argv)
    args.prog = parser.prog
    return args

def main(args, ins, ous):

    proc = Popen([ CSTLEMMA,
                   *CSTFORMATOPTIONS,
                   *CSTENCODING[args.encoding or 'UTF-8'],
                   *CSTMODELS[args.model] ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = None)
    # TODO stderr = PIPE
    # - requires a handler implementation

    return transput(args, sys.modules[__name__], proc, ins, ous)

WORD = None
MSD = None
ENCODING = None
STRICTUTF8 = None
ORIGINS = None

def pr1_init(args, old):
    '''Return new names. Establish the context for the protocol (in this
    case, just the field index WORD).

    '''
    global WORD, MSD, ENCODING, STRICTUTF8

    for name in (args.word, args.msd):
        if name not in old:
            raise BadData('no such field: {}'
                          .format(repr(name.decode('UTF-8'))))

    for name in (args.lemma,):
        if name in old:
            raise BadData('field already in use: {}'
                          .format(name.decode('UTF-8')))

    WORD = old.index(args.word)
    MSD = old.index(args.msd)

    ENCODING = {
        'UTF-8' : 'UTF-8', # does not seem to work right
        'Latin-1' : 'iso-8859-1', # so default ...
        'Latin-2' : 'iso-8859-2',
        'Latin/Greek' : 'iso-8859-7',
        'Latin/Turkish' : 'iso-8859-9',
    }[args.encoding]

    STRICTUTF8 = args.strict # when ENCODING == 'UTF-8'
    ORIGINS = args.origins

    new = old[:]

    new.insert(WORD + 1, args.lemma)
    if ORIGINS:
        lemmaname = lemma.rstrip(b'/')
        flexname = lemmaname + b'.flex/'
        dictname = lemmaname + b'.dict/'
        lookname = lemmaname + b'.look'
        for name in (lookname, dictname, flexname):
            if name in old:
                raise BadData('field already in use: {}'
                              .format(name.decode('UTF-8')))
        new.insert(WORD + 2, flexname)
        new.insert(WORD + 2, dictname)
        new.insert(WORD + 2, lookname)

    return new

def pr1_test(*, meta = (), tags = ()):
    '''Establish whether to send the next sentence to the external tool.
    Current answer: yes. Future answer may depend on lang and _skip.

    '''

    return True

def pr1_send(sentence, proc):
    '''Write the sentence (an iterator of token records) to the external
    process in the desired format (in this case each "word" RE-ENCODED
    with msd on its own line, then a sentinel line that cannot be
    empty because the tool eats empty lines, but maybe also add an
    empty line just in case).

    '''

    for record in sentence:
        # unescape the word (should be librarified)
        word = ( record[WORD]
                 .replace(b'&lt;', b'<')
                 .replace(b'&gt;', b'>')
                 .replace(b'&amp;', b'&')
        )
        word = ( word
                 .decode('UTF-8', errors = 'strict')
                 .encode(ENCODING, errors = 'replace')
        )

        msd = record[MSD]

        if word == b'<< >>': word = b'_'
        proc.stdin.write(b'\t'.join((word, msd)))
        proc.stdin.write(b'\n')
    else:
        proc.stdin.write(b'<< >>\t_\n\n')

def pr1_read(ins):
    '''Return a reader of sentences (iterators of token records) from the
    external process, one sentence at a time (in this case, a sequence
    of lines not starting with << >> which is the sentinel non-word,
    because the underlying tool eats empty lines).

    This reader produces (look, dilemma, rulemmal) for each token,
    where look is a symbol indicating the number of full dictionary
    matches, dilemma a |-separated group of dictionary lemmas, and
    rulemma a |-separated group of rule-generated lemmas.

    '''

    # separator of alternative base forms becomes vertical bar;
    # any vertical bars in base forms become broken bars
    bar = str.maketrans({ '|' : '¦', '\x1f' : '|' })

    lookup = {
        b'-' : b'none', # full form not in dictionary
        b' ' : b'one',  # one lemma in dictionary
        b'+' : b'many', # many lemmas in dictionary
    }

    def grok(word, match, dilemmas, rulemmas):
        '''The options to cstlemma specify whatever output character encoding,
        four tab-separated fields where the last two use a 0x1F (US,
        UNIT SEPARATOR) as a unit separator, because that, as a
        control character, is not allowed in the input word. In VRT,
        the delimiter will be the vertical pipe, so any vertical pipes
        in the lemmas are replaced with a similar-looking broken pipe.

        '''
        if ENCODING == 'UTF-8':
            dilemmas = fixutf8(dilemmas)
            rulemmas = fixutf8(rulemmas)

        dilemmas = dilemmas.decode(ENCODING).translate(bar).encode('UTF-8')
        rulemmas = rulemmas.decode(ENCODING).translate(bar).encode('UTF-8')

        return lookup[match], dilemmas, rulemmas

    for kind, group in groupby(ins, lambda line:
                               line.startswith(b'<< >>\t')):
        if not kind:
            yield (
                grok(*line.rstrip(b'\r\n').split(b'\t'))
                for line in group
            )

def esc(value):
    return (value
            .replace(b'&', b'&amp;') # intentionally first
            .replace(b'<', b'&lt;')
            .replace(b'>', b'&gt;'))

def pr1_join(old, new, ous):
    '''Pass on the old token record, with new lemma/ and such values
    inserted.

    '''

    # look is in { none, one, many } (how many dictionary lemmas)
    # dilemma is |-separated dictionary lemmas
    # rulemma is |-separated rule-generated lemmas
    look, dilemma, rulemma = new

    # presumably dilemma or rulemma is always non-empty so that the
    # last choice of '_' is never used; not using word for that case
    # because word can contain vertical bar, though could replace
    # vertical bar with broken bar there again if desired

    dilemma = esc(b'|' + dilemma + b'|' if dilemma else b'|')
    rulemma = esc(b'|' + rulemma + b'|' if rulemma else b'|')
    lemma = dilemma or rulemma or b'|'
    
    ous.write(b'\t'.join((*old[:WORD + 1],
                          lemma,
                          *((look, dilemma, rulemma) if ORIGINS else ()),
                          *old[WORD + 1:])))
    ous.write(b'\n')

def pr1_keep(old, ous):
    '''Pass on the old token record with placeholder values for the new
    lemma/ and such fields.

    '''
    ous.write(b'\t'.join((*old[:WORD + 1],
                          b'_',
                          *((b'_', b'_', b'_') if ORIGINS else ()),
                          *old[WORD + 1:])))
    ous.write(b'\n')
