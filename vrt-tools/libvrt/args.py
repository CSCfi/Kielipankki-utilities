# Eventually replace ../vrtargslib.py with libvrt.args (this module)
# and other library modules in .. with other modules here, including
# modules that implement various tools, so that (1) the parent
# directory becomes cleaner and (2) Mylly tool scripts can import the
# tool implementations directly instead of calling them through the
# command-line tools - TODO testing this with rel tools first.

from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path
from string import ascii_letters, digits as ascii_digits
from tempfile import mkstemp
import re, os, sys, traceback

from .bad import BadData, BadCode

VERSION = '0.8.6 (2021-08-20)'

def version_args(*, description, epilog = None):
    '''Return an initial argument parser for a command line tool that
    specifies its own options but identifies itself as part of the vrt
    tools.

    '''
    parser = ArgumentParser(description = description, epilog = epilog)

    parser.add_argument('--version',
                        action = 'version',
                        version = '%(prog)s: vrt tools {}'.format(VERSION))

    return parser

def transput_args(*, description, epilog = None, inplace = True):
    '''Return an initial argument parser for a command line tool that
    transforms a single input stream to a single output stream.

    '''

    parser = ArgumentParser(description = description, epilog = epilog)

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
                       dest = 'sibling', metavar = 'EXT',
                       type = sibext,
                       help = '''

                       write to a sibling file, adding .EXT to the
                       input file name, or replacing .OLD with .NEW
                       when EXT is OLD/NEW (allow ASCII letters,
                       digits, underscore, hyphen, and separating
                       period)

                       ''')

    parser.add_argument('--version',
                        action = 'version',
                        version = '%(prog)s: vrt tools {}'.format(VERSION))

    return parser

def multiput_args(*, description, epilog = None):
    '''Return an initial argument parser for a command line tool that
    produces for a single input file a number of output files, as
    siblings with names derived from the input file name, possibly
    removed to a parallel output directory hierarchy.

    '''

    parser = ArgumentParser(description = description, epilog = epilog)

    parser.add_argument('infile', metavar = 'file',
                        help = 'input file')

    parser.add_argument('--infix', '-I',
                        dest = 'infix', metavar = 'EXT',
                        type = sibext,
                        help = '''

                        add .EXT to input file name, or replace .OLD
                        with .NEW when EXT is OLD/NEW (allow ASCII
                        letters, digits, undescore, hyphen, and
                        separating period), before adding output file
                        extension

                        ''')

    parser.add_argument('--outdir', '-D', metavar = 'DIR',
                        help = '''

                        output directory, created as needed, extended
                        with infile path components after any parent
                        reference (infile must be relative)

                        ''')

    parser.add_argument('--version',
                        action = 'version',
                        version = '%(prog)s: vrt tools {}'.format(VERSION))

    return parser

def multiput2_args(*, description, epilog = None):
    '''Return an alternative initial argument parser for a command line
    tool that produces for a single input file a number of output
    files, as siblings with names derived from the input file name,
    possibly removed to a parallel output directory hierarchy.

    This version has a "stem" option to replace the input file stem.

    '''

    parser = ArgumentParser(description = description, epilog = epilog)

    parser.add_argument('infile', nargs = '?', metavar = 'file',
                        help = 'input file (stdin)')

    parser.add_argument('--stem', '-s', metavar = 'name',
                        # default to input stem or "stdin"
                        # should sanity check as filename component;
                        # is str, not bytes
                        help = '''

                        output filename stem
                        (input filename stem, or "stdin" if stdin)

                        ''')

    parser.add_argument('--outdir', '-D', metavar = 'path',
                        dest = 'outdir',
                        help = '''

                        directory where to write the output files
                        (instead of as siblings to the input file or
                        in current working directory), created as
                        needed

                        ''')

    parser.add_argument('--version',
                        action = 'version',
                        version = '%(prog)s: vrt tools {}'.format(VERSION))

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
    filename suffix. Used to consider sensible only ASCII letters,
    found that too restrictive, now allow a (period-separated sequence
    of components that consist of) ASCII letters, digits, underscores
    and hyphens.

    '''
    EXT = r'[\w\-]+(?:\.[\w\-]+)*'

    if '/' not in arg:
        if not arg:
            raise ArgumentTypeError('empty extension')
        if re.fullmatch(EXT, arg, re.ASCII):
            return arg
        raise ArgumentTypeError('not an extension: ' + repr(arg))
    
    extensions = arg.split('/')
    if len(extensions) != 2:
        raise ArgumentTypeError('old/new must have only one slash')

    old, new = extensions
    if not old or not new:
        raise ArgumentTypeError('empty extension')

    if (re.fullmatch(EXT, old, re.ASCII) and
        re.fullmatch(EXT, new, re.ASCII)):
        return arg

    raise ArgumentTypeError('not extensions: '
                            + repr(old) + ' / ' + repr(new))

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

def transput(args, main, *,
             in_as_text = True,
             out_as_text = True):

    '''Arrange to call main(args, ins, ous) with input/output streams as
    specified in args, if args make sense and seem safe in the current
    working directory. Try to handle certain exceptions gracefully.

    '''

    infile = args.infile

    try: args.inplace
    except AttributeError: args.inplace = None

    try: args.backup
    except AttributeError: args.backup = None

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

    status = 1
    try:
        with inputstream(infile, in_as_text) as ins, \
             outputstream(temp, out_as_text) as ous:
            status = main(args, ins, ous)
    except BadData as exn:
        # used to differentiate BadData and BadCode in the message but
        # that may not have been appropriate from user point of view
        print(args.prog + ':', exn, file = sys.stderr)
    except BadCode as exn:
        # this should never happen
        print(args.prog + ':', exn, file = sys.stderr)
    except BrokenPipeError:
        # might want to direct remaining output to /dev/null:
        # https://docs.python.org/3/library/signal.html#note-on-sigpipe
        print(args.prog + ':', 'broken pipe', file = sys.stderr)
    except KeyboardInterrupt:
        print(args.prog + ':', 'keyboard interrupt', file = sys.stderr)
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
        # return succesfully
        # used to exit(0) but new multiput tools need to continue
        # TODO test that old heavy tools still finish, normally
    except IOError as exn:
        print(exn, file = sys.stderr)
        exit(1)

def multiput(args, main):
    '''Arrange to call main(args, infile, outdir) after ensuring that
    outdir exists. Extend args.outdir with a segment of args.infile
    parent names. Pass infile and outdir to main as pathlib objects.

    The purpose is to support tools that produce many output files
    from one input file and base the output filenames on the input
    filename.

    '''

    # verify that input file exists, and is properly relative to . if
    # output directory is specified

    infile = Path(args.infile)
    if not infile.exists():
        print('{}: not found: {}'.format(args.prog, infile),
              file = sys.stderr)
        exit(1)
    elif not infile.is_file():
        # a symlink that points to a regular file should work; mainly
        # detecting directory names early; filename is needed for the
        # naming of the output files; should one allow fifo or such?
        print('{}: not a regular file: {}'.format(args.prog, infile),
              file = sys.stderr)
        exit(1)
    else: pass

    # multiput tools receive outfile name that they extend
    # with their own suffixes, after infix processing here

    outfile = infile.name
    if args.infix and '/' in args.infix:
        old, new = args.infix.split('/')
        if outfile.endswith('.' + old):
            outfile = outfile[:-len(old)] + new
        else:
            print('{}: no such suffix to replace: {}'
                  .format(args.prog, old),
                  '{}: {}'.format(args.prog, outfile),
                  sep = '\n', file = sys.stderr)
            exit(1)
    elif args.infix:
        outfile = outfile + '.' + args.infix

    # if outdir is specified, extend it with those parent names of the
    # input filename that follow the last .., if any, then ensure that
    # the resulting outdir exists

    outdir = args.outdir
    if outdir:
        if infile.is_absolute():
            print('{}: error: --outdir requires relative input filename'
                  .format(args.prog),
                  '{}: input filename: {}'.format(args.prog, infile),
                  sep = '\n', file = sys.stderr)
            exit(1)

        # deliberately off by one so the last index is just past ".."
        starts = (tuple(k for k, part in enumerate(infile.parent.parts,
                                                   start = 1)
                        if part in ('..', '.'))
                  or (0,))
        subdir = Path(*infile.parent.parts[starts[-1]:])
        outdir = Path(args.outdir) / subdir

        try:
            outdir.mkdir(parents = True, exist_ok = True)
        except OSError as exn:
            print('{}: error: could not make output directory: {}'
                  .format(args.prog, outdir))
            print('{}: {}'.format(args.prog, exn))
            exit(1)

    if outdir is None:
        outdir = infile.parent

    main(args, str(infile), str(outdir / outfile))

def multiput2(args, main, *,
              in_as_text = True):
    '''Arrange to call main(args, instream, outdir) after ensuring that
    outdir exists.

    The purpose is to support tools that produce many output files
    from one input file.

    '''

    if args.outdir is None:
        outdir = '.' if args.infile is None else os.path.dirname(args.infile)
    else:
        os.makedirs(args.outdir, exist_ok = True)
        outdir = args.outdir

    if args.infile is None:
        ins = sys.stdin if in_as_text else sys.stdin.buffer
    else:
        ins = open(args.infile, ('r' if in_as_text else 'br'))

    main(args, ins, str(outdir))

def nat(arg):
    '''A "type" for an argument parser to enforce that an int is not
    negative.

    '''
    n = int(arg) # or raise ValueError
    if n < 0:
        # use the same expection that int() raises;
        # the important thing is that this is caught
        # by the argument parser
        raise ValueError('negative literal for nat()')
    return n
