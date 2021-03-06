# -*- mode: Python; -*-

# Implementation of a command-line tool ../rel-miss,
# hopefully also usable with synthetic arguments in
# a Mylly (Chipster) tool, to be tested.

from .args import transput_args
from .data import readhead, groups

def parsearguments(argv, *, prog = None):
    description = '''

    Records that do not matchd any record in another relation on the
    values in the fields that have the same name.

    '''

    parser = transput_args(description = description, matching = True)

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args, ins1, ins2, ous):

    head1 = readhead(ins1)
    head2 = readhead(ins2)

    key = tuple(name for name in head1 if name in head2)

    ous.write(b'\t'.join(head1))
    ous.write(b'\n')

    body1 = groups(ins1, head = head1, key = tuple(map(head1.index, key)))
    body2 = groups(ins2, head = head2, key = tuple(map(head2.index, key)))
    k1, g1 = next(body1, (None, None))
    k2, g2 = next(body2, (None, None))
    while k1 is not None is not k2:
        if k1 == k2:
            k1, g1 = next(body1, (None, None))
            k2, g2 = next(body2, (None, None))
        elif k1 < k2:
            for r1 in g1:
                ous.write(b'\t'.join(r1))
                ous.write(b'\n')
            k1, g1 = next(body1, (None, None))
        else:
            k2, g2 = next(body2, (None, None))
    else:
        if g1 is not None:
            for r1 in g1:
                ous.write(b'\t'.join(r1))
                ous.write(b'\n')
        for k1, g1 in body1:
            for r1 in g1:
                ous.write(b'\t'.join(r1))
                ous.write(b'\n')
        # any reason to drain g2, body2?

    return 0
