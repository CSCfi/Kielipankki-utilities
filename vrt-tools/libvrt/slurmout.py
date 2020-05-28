import os
from tempfile import mkstemp


def simplepath(path):
    '''Normalize path as relative to current directory if under the
    current directory and not starting with a component that starts
    with dots, else absolute.

    '''
    absolute = os.path.abspath(path)
    relative = os.path.relpath(path)
    return absolute if relative.startswith('..') else relative

def ensuredir(path):
    '''Attempt to establish that the directory path exists, by creating it
    if not. Do not bother to attempt to check whether anyone in
    particular can write in the directory.

    '''
    path = simplepath(path)
    try:
        os.makedirs(path, exist_ok = True)
    except OSError as exn:
        # in Python 3.4.0 (and earlier), a mode mismatch may lead here
        # even if path is all right
        if os.path.isdir(path): return
        raise exn

def ensuretempfile(outdir, outfile):
    handle, tmppath = mkstemp(prefix = outfile + '.', dir = outdir)
    os.close(handle)
    return tmppath

def setup(args):
    '''Make sure the relevant directories exist. Return suitable pathnames
    for the log dir, outfile (or None), and tempfile (or None). If
    there is to be a tempfile, create the tempfile in advance to claim
    the name. Except with the --cat option only output pathnames (a
    placeholder name for a tempfile) without creating any filesystem
    entries.

    '''

    args.cat or ensuredir(args.log)

    if args.out or args.accept:
        outfile = simplepath(args.out or args.accept)
        head, tail = os.path.split(outfile)
        if not tail:
            print(args.prog + ':gamarray: not a filename: {}'
                  .format(args.out or args.accept),
                  file = sys.stderr)
            exit(1)
    else:
        outfile = None

    if args.out and args.cat:
        # no good way out
        tempfile = os.path.join(head, tail + '.[random]')
    elif args.out:
        tempfile = ensuretempfile(head, tail)
    elif args.accept:
        tempfile = None
    else:
        tempfile = None

    return simplepath(args.log), outfile, tempfile

