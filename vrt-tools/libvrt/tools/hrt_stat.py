# -*- mode: Python; -*-

'''Implementation of hrt-stat.'''

from libvrt.args import BadData, nat
from libvrt.args import multiput_args
from libvrt.args import transput

from libvrt.tools import hrt_stat_meta
from libvrt.tools import hrt_stat_data

from datetime import datetime as datetime
def _secs(): return datetime.now().isoformat(' ', timespec = 'seconds')

def parsearguments(argv, *, prog = None):

    description = '''

    Report a selection of statistics on an "HRT" document, either in
    sibling files to the input file or in a specified directory.

    '''

    parser = multiput_args(description = description)

    parser.add_argument('--quiet', '-q', action = 'store_true',
                        help = '''

                        do not report steps in stdout

                        ''')

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, infile, outfile):
    '''Direct statistic reports on the HRT in infile to output files with
    names obtained by extending the outfile with appropriate suffixes.

    '''

    now = _secs()
    args.quiet or print('{} -- {} (meta len)'.format(now, args.prog))
    args.quiet or print('{} -- length of each attribute value in code points'
                        .format(now))
    args.quiet or print('{} {}.meta.len'.format(now, outfile))
    transput(hrt_stat_meta.parsearguments
             (
                 [
                     '--out', outfile + '.meta.len',
                     '--len',
                     '--sum=h5',
                     infile
                 ],
                 prog = '{} (meta len)'.format(args.prog)
             ),
             hrt_stat_meta.main)

    now = _secs()
    args.quiet or print('{} -- {} (meta maxw)'.format(now, args.prog))
    args.quiet or print('{} -- longest word-code-run in each attribute'
                        .format(now))
    args.quiet or print('{} {}.meta.maxw'.format(now, outfile))
    transput(hrt_stat_meta.parsearguments
             (
                 [
                     '--out', outfile + '.meta.maxw',
                     '--max=w',
                     '--sum=h5',
                     infile
                 ],
                 prog = '{} (meta maxw)'.format(args.prog)
             ),
             hrt_stat_meta.main)

    now = _secs()
    args.quiet or print('{} -- {} (data len)'.format(now, args.prog))
    args.quiet or print('{} -- length of each paragraph in code points'
                        .format(now))
    args.quiet or print('{} {}.data.len'.format(now, outfile))
    transput(hrt_stat_data.parsearguments
             (
                 [
                     '--out', outfile + '.data.len',
                     '--len',
                     '--sum=h5',
                     infile
                 ],
                 prog = '{} (data len)'.format(args.prog)
             ),
             hrt_stat_data.main)

    now = _secs()
    args.quiet or print('{} -- {} (data maxw)'.format(now, args.prog))
    args.quiet or print('{} -- longest word-code-run in each paragraph'
                        .format(now))
    args.quiet or print('{} {}.data.maxw'.format(now, outfile))
    transput(hrt_stat_data.parsearguments
             (
                 [
                     '--out', outfile + '.data.maxw',
                     '--max=w',
                     '--sum=h5',
                     infile
                 ],
                 prog = '{} (data maxw)'.format(args.prog)
             ),
             hrt_stat_data.main)

    now = _secs()
    args.quiet or print('{} -- {} (data maxnw)'.format(now, args.prog))
    args.quiet or print('{} -- longest non-word-code-run in each paragraph'
                        .format(now))
    args.quiet or print('{} {}.data.maxnw'.format(now, outfile))
    transput(hrt_stat_data.parsearguments
             (
                 [
                     '--out', outfile + '.data.maxnw',
                     '--max=W',
                     '--sum=h5',
                     infile
                 ],
                 prog = '{} (data maxnw)'.format(args.prog)
             ),
             hrt_stat_data.main)

    now = _secs()
    args.quiet or print('{} -- {} (done)'.format(now, args.prog))
