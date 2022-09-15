# -*- mode: Python; -*-

'''Implementation of hrt-check-meta.'''

from libvrt.args import BadData
from libvrt.args import transput_args
from libvrt.check import setup_binary
from libvrt.check import error, warn, info

import re

def parsearguments(argv, *, prog = None):

    description = '''

    Report on well-formedness and consistency of structure-starting
    tags in an "HRT" document.

    '''

    parser = transput_args(description = description,
                           inplace = False)

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, ins, ous):
    '''Transput HRT input stream in ins to TSV report in ous.

    TODO: adapt to ignore such tags that are allowed within sentences
    (need an option to list such); either allow or do not allow
    comments.

    '''

    setup_binary(ous)

    META = br'<[a-z._]+(\s+[a-z._][a-z0-9._]+/?="[^"]*")*>\r?\n?'
    for k, line in enumerate(ins, start = 1):
        if (line.startswith(b'<') and
            not line.startswith(b'</')):

            if not re.fullmatch(META, line):
                error(k, b'meta', b'malformed start tag')
                continue

            name = re.match(b'<([a-z._]+)', line).group(1)
            check_name(args, ous, line, name)

            attr = re.findall(b'(\S+)="(.*?)"', line)
            check_attr(args, ous, line, name, attr)
            
            # print('name:', name)
            # print('attr:', attr)

def check_name(args, ous, line, name):
    if name not in (b'text', b'paragraph'):
        warn(line, b'meta',
             b' '.join((b'unexpected element name:',
                        name)))

def check_attr(args, ous, line, name, attr):
    # to check no duplicate names
    # to check no < > in values
    # to check order of names
    # to check multivalue format
    # to check strict spacing
    # to check some required attributes?
    pass
