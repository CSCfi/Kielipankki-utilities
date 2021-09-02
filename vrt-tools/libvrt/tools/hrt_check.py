# -*- mode: Python; -*-

'''Implementation of hrt-check.'''

from libvrt.args import BadData, nat
from libvrt.args import multiput_args
from libvrt.args import transput

from libvrt.tools import hrt_check_utf8
from libvrt.tools import hrt_check_meta
from libvrt.tools import hrt_check_control
from libvrt.tools import hrt_check_nonchar
from libvrt.tools import hrt_check_private
from libvrt.tools import hrt_check_tags
from libvrt.tools import hrt_check_bidi
from libvrt.tools import hrt_check_shy

from datetime import datetime as datetime
def _secs(): return datetime.now().isoformat(' ', timespec = 'seconds')

def parsearguments(argv, *, prog = None):

    description = '''

    Write various reports on the quality of a named "HRT" document,
    either as siblings to the input file or in a specified directory.

    '''

    parser = multiput_args(description = description)

    parser.add_argument('--quiet', '-q', action = 'store_true',
                        help = '''

                        do not report steps in stdout

                        ''')

    group = parser.add_mutually_exclusive_group()
    # to have --warning, --error some day, maybe,
    # or is this wanted here? should only write
    # preliminary reports to indicate any need to
    # look more closely at something, or not
    group.add_argument('--info', action = 'store_true',
                        help = '''

                        Include merely informative messages (if any).

                        ''')

    # may have defaults here, too, only
    parser.add_argument('--limit', metavar = 'N',
                        default = 10,
                        type = nat,
                        help = '''

                        Exit after reporting N (10) lines that fail.

                        ''')
    parser.add_argument('--no-limit', action = 'store_true',
                        dest = 'no_limit',
                        help = '''

                        Report every line that fails. Overrides any
                        limit.

                        ''')

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, infile, outfile):
    '''Check HRT input file, direct reports to output files, as specified
    in args. Receives infile and outfile as strings, extends outfile
    with appropriate suffix for each output file.

    '''

    # print('infile:', infile)
    # print('outfile:', outfile)

    now = _secs()
    args.quiet or print('{} -- {} (utf8)'.format(now, args.prog))
    args.quiet or print('{} -- whether a line is UTF-8 at all'
                        .format(now))
    args.quiet or print('{} {}.utf8'.format(now, outfile))
    transput(hrt_check_utf8.parsearguments
             (
                 [
                     '--out', outfile + '.utf8',
                     '--limit=10',
                     infile
                 ],
                 prog = '{} (utf8)'.format(args.prog)
             ),
             hrt_check_utf8.main,
             in_as_text = False)

    now = _secs()
    args.quiet or print('{} -- {} (meta)'.format(now, args.prog))
    args.quiet or print('{} -- whether structure lines are well-formed'
                        .format(now))
    args.quiet or print('{} {}.meta'.format(now, outfile))
    transput(hrt_check_meta.parsearguments
             (
                 [
                     '--out', outfile + '.meta',
                     # hrt-check-meta does not have --limit (yet?)
                     # '--limit=100',
                     infile
                 ],
                 prog = '{} (meta)'.format(args.prog)
             ),
             hrt_check_meta.main,
             in_as_text = False,
             out_as_text = False)

    now = _secs()
    args.quiet or print('{} -- {} (control)'.format(now, args.prog))
    args.quiet or print('{} -- whether there are control codes'
                        .format(now))
    args.quiet or print('{} {}.ctl'.format(now, outfile))
    transput(hrt_check_control.parsearguments
             (
                 [
                     '--out', outfile + '.ctl',
                     '--limit=100',
                     infile
                 ],
                 prog = '{} (control)'.format(args.prog)
             ),
             hrt_check_control.main)

    now = _secs()
    args.quiet or print('{} -- {} (nonchar)'.format(now, args.prog))
    args.quiet or print('{} -- whether there are noncharacter codes'
                        .format(now))
    args.quiet or print('{} {}.non'.format(now, outfile))
    transput(hrt_check_nonchar.parsearguments
             (
                 [
                     '--out', outfile + '.non',
                     '--limit=100',
                     infile
                 ],
                 prog = '{} (nonchar)'.format(args.prog)
             ),
             hrt_check_nonchar.main)

    now = _secs()
    args.quiet or print('{} -- {} (private)'.format(now, args.prog))
    args.quiet or print('{} -- whether there are private codes'
                        .format(now))
    args.quiet or print('{} {}.priv'.format(now, outfile))
    transput(hrt_check_private.parsearguments
             (
                 [
                     '--out', outfile + '.priv',
                     '--limit=100',
                     infile
                 ],
                 prog = '{} (private)'.format(args.prog)
             ),
             hrt_check_private.main)

    now = _secs()
    args.quiet or print('{} -- {} (tags)'.format(now, args.prog))
    args.quiet or print('{} -- whether there are tag (flag) codes'
                        .format(now))
    args.quiet or print('{} {}.tag'.format(now, outfile))
    transput(hrt_check_tags.parsearguments
             (
                 [
                     '--out', outfile + '.tag',
                     '--limit=100',
                     infile
                 ],
                 prog = '{} (tags)'.format(args.prog)
             ),
             hrt_check_tags.main)

    now = _secs()
    args.quiet or print('{} -- {} (bidi)'.format(now, args.prog))
    args.quiet or print('{} -- whether there are bidi codes'
                        .format(now))
    args.quiet or print('{} {}.bidi'.format(now, outfile))
    transput(hrt_check_bidi.parsearguments
             (
                 [
                     '--out', outfile + '.bidi',
                     '--limit=100',
                     infile
                 ],
                 prog = '{} (bidi)'.format(args.prog)
             ),
             hrt_check_bidi.main)

    now = _secs()
    args.quiet or print('{} -- {} (shy)'.format(now, args.prog))
    args.quiet or print('{} -- whether there are soft hyphens'
                        .format(now))
    args.quiet or print('{} {}.shy'.format(now, outfile))
    transput(hrt_check_shy.parsearguments
             (
                 [
                     '--out', outfile + '.shy',
                     '--limit=100',
                     infile
                 ],
                 prog = '{} (shy)'.format(args.prog)
             ),
             hrt_check_shy.main)

    now = _secs()
    args.quiet or print('{} -- {} (done)'.format(now, args.prog))
