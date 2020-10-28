import os

from libvrt.bad import BadData

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
    try:
        os.makedirs(path, exist_ok = True)
    except OSError as exn:
        # in Python 3.4.0 (and earlier), a mode mismatch may lead here
        # even if path is all right
        if os.path.isdir(path): return
        raise exn

def setup(args):
    '''Make sure the log directory exists. Return suitable pathnames for
    the log directory and the outfile (or None).

    Except with the --cat option only output pathnames without
    creating any filesystem entries. TODO reconsider

    '''

    logpath = simplepath(args.log)
    args.cat or ensuredir(logpath)

    if args.out is None:
        return logpath, None
    
    outfile = simplepath(args.out)
    if '<' in outfile or '>' in outfile:
        raise BadData('cannot have "<" or ">" in outfile: {}'
                      .format(outfile))

    head, tail = os.path.split(outfile)
    if not tail:
        raise BadData('no basename part for outfile: {}'
                      .format(args.out))

    # ensure a "/" for "${outfile%/*}" in shell;
    # do not use any smart high-level operation
    # that might know to omit that './'
    if '/' not in outfile: outfile = './' + outfile

    # for "${outfile/<>/$stem}" in shell
    return logpath, outfile.replace('{}', '<>')

