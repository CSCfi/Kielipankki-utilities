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

def parsearguments(argv, *, prog = None):

    description = '''

    Write various reports on the quality of a named "HRT" document,
    either as siblings to the input file or in a specified directory.

    '''

    parser = multiput_args(description = description)

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

    transput(hrt_check_utf8.parsearguments
             (
                 [
                     '--out', outfile + '.utf8',
                     '--limit=10',
                     infile
                 ],
                 prog = 'hrt-check(utf8)'
             ),
             hrt_check_utf8.main,
             in_as_text = False)

    transput(hrt_check_meta.parsearguments
             (
                 [
                     '--out', outfile + '.meta',
                     # hrt-check-meta does not have --limit (yet?)
                     # '--limit=100',
                     infile
                 ],
                 prog = 'hrt-check(meta)'
             ),
             hrt_check_meta.main,
             in_as_text = False,
             out_as_text = False)

    transput(hrt_check_control.parsearguments
             (
                 [
                     '--out', outfile + '.ctl',
                     '--limit=100',
                     infile
                 ],
                 prog = 'hrt-check(control)'
             ),
             hrt_check_control.main)

    transput(hrt_check_nonchar.parsearguments
             (
                 [
                     '--out', outfile + '.non',
                     '--limit=100',
                     infile
                 ],
                 prog = 'hrt-check(nonchar)'
             ),
             hrt_check_nonchar.main)

    transput(hrt_check_private.parsearguments
             (
                 [
                     '--out', outfile + '.priv',
                     '--limit=100',
                     infile
                 ],
                 prog = 'hrt-check(private)'
             ),
             hrt_check_private.main)

    transput(hrt_check_tags.parsearguments
             (
                 [
                     '--out', outfile + '.tag',
                     '--limit=100',
                     infile
                 ],
                 prog = 'hrt-check(tags)'
             ),
             hrt_check_tags.main)

    transput(hrt_check_bidi.parsearguments
             (
                 [
                     '--out', outfile + '.bidi',
                     '--limit=100',
                     infile
                 ],
                 prog = 'hrt-check(bidi)'
             ),
             hrt_check_bidi.main)

    transput(hrt_check_shy.parsearguments
             (
                 [
                     '--out', outfile + '.shy',
                     '--limit=100',
                     infile
                 ],
                 prog = 'hrt-check(shy)'
             ),
             hrt_check_shy.main)
