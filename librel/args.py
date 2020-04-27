'''Common interface to relation tools (rel tools), including a common
version number.

Initially a copy of vrt-tools/vrtargslib.py, with any of the problems
that still plague that about abnormal terminations. Start with the
only differences being version number and identification as a rel
tools instead of a vrt tool. Proceed to allow a second input file
TODO.

'''

from argparse import ArgumentParser, ArgumentTypeError
from string import ascii_letters, digits as ascii_digits
from tempfile import mkstemp
import os, sys, traceback

VERSION = '0.0.0 (2020-04-26)'

class BadData(Exception): pass # stack trace is just noise
class BadCode(Exception): pass # this cannot happen

def version_args(*, description):
    '''Return an initial argument parser for a command line tool that
    specifies its own options but identifies itself as part of
    relation tools.

    '''
    parser = ArgumentParser(description = description)

    parser.add_argument('--version',
                        action = 'version',
                        version = '%(prog)s: rel tools {}'.format(VERSION))

    return parser

def transput_args(*, description, inplace = True):
    '''Return an initial argument parser for a command line tool that
    transforms one or two input streams to a single output stream.

    '''

    parser = ArgumentParser(description = description)

    parser.add_argument('infile', nargs = '?', metavar = 'file',
                        help = 'input file (default stdin)')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--out', '-o',
                       dest = 'outfile', metavar = 'file',
                       help = 'output file (default stdout)')
    if inplace:
        group.add_argument('--in-place', '-i',
                           dest = 'inplace', action = 'store_true',
                           help = '''

                           replace input file with final output

                           ''')
        group.add_argument('--backup', '-b', metavar = 'bak',
                           type = bakfix,
                           help =
                           '''

                           replace input file with final output, keep
                           input file with the added suffix bak

                           ''')
    else: pass

    group.add_argument('--in-sibling', '-I',
                       dest = 'sibling', metavar = 'ext',
                       type = sibext,
                       help = '''

                       write output to a sibling file, replacing (if
                       ext is given as old/new) or adding an extension
                       to the input file name; both extensions must
                       consist of ASCII letters

                       ''')

    parser.add_argument('--version',
                        action = 'version',
                        version = '%(prog)s: rel tools {}'.format(VERSION))

    return parser

def bakfix(arg):
    '''Argument type for --backup: argument must be a valid and proper and
    safe suffix to a filename.

    '''
    if not arg:
        raise ArgumentTypeError('empty suffix')

    if all(c in ascii_letters or
           c in ascii_digits or
           c in '%+,-.=@^_~'
           for c in arg):
        return arg

    raise ArgumentTypeError('scary character in suffix')

def sibext(arg):
    '''Argument type for sibling extension: must be old/new where new must
    not be empty and otherwise both old and new must be sensible
    filename suffix. Consider sensible only ASCII letters.

    '''
    if '/' not in arg:
        if not arg:
            raise ArgumentTypeError('empty extension')
        if all(c in ascii_letters for c in arg):
            return arg
        raise ArgumentTypeError('bad character in extension')
    
    extensions = arg.split('/')
    if len(extensions) != 2:
        raise ArgumentTypeError('old/new must have one slash')

    old, new = extensions
    if not old or not new:
        raise ArgumentTypeError('empty extension')

    if (all(c in ascii_letters for c in old) and
        all(c in ascii_letters for c in new)):
        return arg

    raise ArgumentTypeError('bad character in extension')

def inputstream(infile, as_text):
    if infile is None:
        return (sys.stdin if as_text else
                # .detach() appears to be the magic that allows to
                # read the first line and pass on the rest to a
                # subprocess (buffering could not even be disabled)
                sys.stdin.buffer.detach())
    return ( open(infile, mode = 'r', encoding = 'UTF-8')
             if as_text else
             # .detach() appears to allow to read the first line and
             # pass on the rest to a subprocess (disabling buffering
             # seemed to also work or was anything even needed)
             open(infile, mode = 'br').detach() )

def outputstream(outfile, as_text):
    if outfile is None:
        return (sys.stdout if as_text else
                sys.stdout.buffer)
    return ( open(outfile, mode = 'w', encoding = 'UTF-8')
             if as_text else
             open(outfile, mode = 'bw') )

def transput(args, main, *, in_as_text = False, out_as_text = False):

    infile = args.infile

    if args.inplace and (infile is None):
        print(args.prog + ': --in-place requires input filename',
              file = sys.stderr)
        exit(1)

    if args.backup and (infile is None):
        print(args.prog + ': --backup requires input filename',
              file = sys.stderr)
        exit(1)

    if args.sibling and (infile is None):
        print(args.prog + ': --in-sibling requires input filename',
              file = sys.stderr)
        exit(1)

    if args.backup is not None:
        backfile = infile + args.backup
    else:
        backfile = None

    if args.outfile is not None:
        outfile = args.outfile
    elif args.inplace or args.backup:
        outfile = infile
    elif args.sibling is not None:
        if '/' in args.sibling:
            # replace input extension
            old, new = args.sibling.split('/')
            old = '.' + old
            new = '.' + new
            infilesansext, ext = os.path.splitext(infile)
            if ext == old:
                outfile = infilesansext + new
            else:
                print(args.prog + ':', 'input extension does not match',
                      file = sys.stderr)
                exit(1)
        else:
            # add a further extension
            new = '.' + args.sibling
            outfile = infile + new
    else:
        outfile = None

    if (args.outfile is not None) and os.path.exists(outfile):
        print(args.prog + ': --out file must not exist',
              file = sys.stderr)
        exit(1)

    if (args.sibling is not None) and os.path.exists(outfile):
        print(args.prog + ': --in-sibling file must not exist',
              file = sys.stderr)
        exit(1)

    if outfile is not None:
        head, tail = os.path.split(outfile)
        fd, temp = mkstemp(dir = head, prefix = tail + '.', suffix = '.tmp')
        os.close(fd)
    else:
        temp = None

    def do():
        status = 1
        try:
            status = main(args, inf, ouf)
        except BadData as exn:
            print(args.prog + ': error in data:', exn, file = sys.stderr)
        except BadCode as exn:
            print(args.prog + ': error in code:', exn, file = sys.stderr)
        except BrokenPipeError:
            print(args.prog + ':', 'broken pipe from main',
                  file = sys.stderr)
        except Exception as exn:
            print(traceback.format_exc(), file = sys.stderr)

        return status

    status = 1
    try:
        with inputstream(infile, in_as_text) as inf, \
             outputstream(temp, out_as_text) as ouf:
            status = do()
    except BrokenPipeError:
        print(args.prog + ':', 'broken pipe outside main',
              file = sys.stderr)
    except Exception as exn:
        print(traceback.format_exc(), file = sys.stderr)

    if status:
        print(args.prog + ': non-zero status', status, file = sys.stderr)
        (
            temp is None
            or print(args.prog + ': leaving output in', temp,
                     file = sys.stderr)
        )
        exit(status)

    try:
        backfile is None or os.rename(infile, backfile)
        outfile is None or os.rename(temp, outfile)
        exit(status)
    except IOError as exn:
        print(exn, file = sys.stderr)
        exit(1)
