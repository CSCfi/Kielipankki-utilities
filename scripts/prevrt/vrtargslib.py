# Hm - nothing about VRT here? Yet?
# Might rename to something general.

from argparse import ArgumentParser, ArgumentTypeError
from tempfile import mkstemp
import os, sys, traceback

class BadData(Exception): pass # stack trace is just noise
class BadCode(Exception): pass # this cannot happen

def trans_args(*, description, version):
    '''Return an initial argument parser for a command line tool that
    transforms a single input stream to a single output stream.

    '''

    parser = ArgumentParser(description = description)

    parser.add_argument('infile', nargs = '?', metavar = 'file',
                        help = 'input file (default stdin)')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--out', '-o',
                       dest = 'outfile', metavar = 'file',
                       help = 'output file (default stdout)')
    group.add_argument('--in-place', '-i',
                       dest = 'inplace', action = 'store_true',
                       help = '''replace input file with final output''')
    group.add_argument('--backup', '-b', metavar = 'bak', help =
                       '''
                       replace input file with final output,
                       keep input file with the added suffix bak''')

    parser.add_argument('--version',
                        action = 'version',
                        version = '%(prog)s {}'.format(version))

    return parser

def inputstream(infile, as_text):
    if infile is None:
        return (sys.stdin if as_text else
                sys.stdin.buffer)
    return ( open(infile, mode = 'r', encoding = 'UTF-8')
             if as_text else
             open(infile, mode = 'br') )

def outputstream(outfile, as_text):
    if outfile is None:
        return (sys.stdout if as_text else
                sys.stdout.buffer)
    return ( open(outfile, mode = 'w', encoding = 'UTF-8')
             if as_text else
             open(outfile, mode = 'bw') )

def trans_main(args, main, *, in_as_text = True, out_as_text = True):

    # TODO exclusion makes some of these tests redundant

    if (args.backup is not None) and '/' in args.backup:
        print('usage: --backup suffix cannot contain /', file = sys.stderr)
        exit(1)

    if (args.backup is not None) and not args.backup:
        print('usage: --backup suffix cannot be empty', file = sys.stderr)
        exit(1)

    if (args.backup is not None) and not args.inplace:
        print('usage: --backup requires --in-place', file = sys.stderr)
        exit(1)

    if args.inplace and (args.infile is None):
        print('usage: --in-place requires input file', file = sys.stderr)
        exit(1)

    if args.inplace and (args.outfile is not None):
        print('usage: --in-place not allowed with --out', file = sys.stderr)
        exit(1)

    if (args.outfile is not None) and os.path.exists(args.outfile):
        # easier to check this than that output file is different than
        # input file, though it be annoying when overwrite is wanted
        print('usage: --out file must not exist', file = sys.stderr)
        exit(1)

    if args.inplace or (args.outfile is not None):
        head, tail = os.path.split(args.infile
                                   if args.inplace
                                   else args.outfile)
        fd, temp = mkstemp(dir = head, prefix = tail)
        os.close(fd)
    else:
        temp = None

    def do():
        status = 1
        try:
            status = main(args, inf, ouf)
        except BadData as exn:
            print(args.prog + ':', exn, file = sys.stderr)
        except BrokenPipeError:
            print(args.prog + ':', 'broken pipe from main',
                  file = sys.stderr)
        except Exception as exn:
            print(traceback.format_exc(), file = sys.stderr)

        return status

    try:
        with inputstream(args.infile, in_as_text) as inf, \
             outputstream(temp, out_as_text) as ouf:
            status = do()
    except BrokenPipeError:
        print(args.prog + ':', 'broken pipe outside main',
              file = sys.stderr)
    except Exception as exn:
        print(traceback.format_exc(), file = sys.stderr)

    try:
        # TODO not rename temp if error status
        args.backup and os.rename(args.infile, args.infile + args.backup)
        args.inplace and os.rename(temp, args.infile)
        args.outfile and os.rename(temp, args.outfile)
        exit(status)
    except IOError as exn:
        print(exn, file = sys.stderr)
        exit(1)
