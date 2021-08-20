# -*- mode: Python; -*-

'''Implementation of hrt-stat-meta.'''

from libvrt.args import BadCode, BadData
from libvrt.args import nat
from libvrt.args import transput_args
from libvrt.stat import quant, sum_of_lengths, number_of_runs, max_length

from collections import defaultdict, Counter

import re

def parsearguments(args, *, prog = None):

    description = '''

    Show some statistic on structure-starting tags in an "HRT"
    document. This should work for "VRT" as well.

    '''

    parser = transput_args(description = description,
                           inplace = False)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--len', action = 'store_true',
                       dest = 'length',
                       help = '''

                       the number of code points

                       ''')

    group.add_argument('--num', choices = [ 'w', 'W', 's', 'S', 'shy' ],
                       dest = 'num_such',                       
                       help = '''

                       the number of such codes (word character, not
                       word character, space, not space)

                       ''')

    group.add_argument('--run', choices = [ 'w', 'W', 's', 'S', 'shy' ],
                       dest = 'num_runs',
                       help = '''

                       the number of maximal runs of such codes

                       ''')

    group.add_argument('--max', choices = [ 'w', 'W', 's', 'S', 'shy' ],
                       dest = 'max_length',
                       help = '''

                       the maximal length of a maximal run of such
                       codes

                       ''')

    parser.add_argument('--sum', dest = 'summ',
                        default = None,
                        choices = [ 'h5', 'v5', 'h11', 'v11' ],
                        help = '''

                        summarize instead of reporting each

                        ''')

    parser.add_argument('--elem', '-e', metavar = 'NAMES',
                        default = [],
                        action = 'append',
                        help = '''

                        restrict to named elements (repeat, or
                        separate with commas or spaces)

                        ''')

    parser.add_argument('--attr', '-a', metavar = 'NAMES',
                        default = [],
                        action = 'append',
                        help = '''

                        restrict to named attributes (repeat, or
                        separate with commas or spaces)

                        ''')

    parser.add_argument('--limit', metavar = 'N',
                        type = nat,
                        default = 0,
                        help = '''

                        observe only so many meta lines (except
                        default 0 means all)

                        ''')

    args = parser.parse_args()
    args.prog = prog or parser.prog

    return args

REX = dict(w = r'\w+',
           W = r'\W+',
           s = r'\s+',
           S = r'\S+',
           shy = '\xAD+',)

def main(args, ins, ous):
    '''Transput HRT input stream in ins to TSV report in ous.

    TODO: adapt to ignore such tags that are allowed within sentences
    (need an option to list such); either allow or do not allow
    comments.

    '''

    meta = (triple for triple in parse_meta(args, ins))
    if args.length:
        report_stats(meta,
                     len, 'len',
                     args.summ, ous)
    elif args.num_such:
        regex = REX[args.num_such]
        report_stats(meta,
                     sum_of_lengths(regex), 'num_' + args.num_such,
                     args.summ, ous)
    elif args.num_runs:
        regex = REX[args.num_runs]
        report_stats(meta,
                     number_of_runs(regex), 'runs_' + args.num_runs,
                     args.summ, ous)
    elif args.max_length:
        regex = REX[args.max_length]
        report_stats(meta,
                     max_length(regex), 'maxlen_' + args.max_length,
                     args.summ, ous)
    else:
        print('sorry, forgot to have a default stat', file = ous)

def parse_meta(args, ins):
    '''Yield each relevant meta line as a triple of the line number,
    element name, and attribute dict.

    '''

    # if elemi or attri is non-empty, only report on elements and
    # attributes with those names (from --elem, --attr options)

    elemi = set(name for name in
                re.findall(r'\S+', ' '.join(args.elem).replace(',', ' ')))

    attri = set(name for name in
                re.findall(r'\S+', ' '.join(args.attr).replace(',', ' ')))

    occurrences = 0
    for k, line in enumerate(ins, start = 1):
        mo = re.match('<([a-z._]+)', line)
        if not mo: continue

        occurrences += 1
        elem = mo.group(1)
        if elemi and elem not in elemi: continue
        attr = dict((key, val)
                    for key, val in re.findall(r'(\S+)="(.*?)"', line)
                    if not attri or key in attri)

        yield k, elem, attr

        if occurrences == args.limit:
            return

def report_stats(meta, stat, what, summ, ous):
    '''Report on stat(value) for each attribute value in meta.

    '''
    if summ:
        mem = defaultdict(Counter)
        for _, elem, attr in meta:
            for key, val in attr.items():
                mem[elem, key][stat(val)] += 1
        summarize(mem, summ, what, ous)
        return

    # report each observation

    print('line', 'elem', 'attr', what, sep = '\t', file = ous)
    for line, elem, attr in meta:
        for key, val in attr.items():
            print(line, elem, key, stat(val),
                  sep = '\t', file = ous)

def summarize(mem, summ, what, ous):
    head5 = ('min', 'lo', 'med', 'hi', 'max')
    head11 = ('min', 'd1', 'd2', 'd3', 'd4',
              'med', 'd6', 'd7', 'd8', 'd9', 'max')
    if summ == 'h5':
        print('elem', 'attr', 'stat', *head5, sep = '\t', file = ous)
        for elem, attr in sorted(mem):
            print(elem, attr, what, *quant(mem[elem, attr], 4),
                  sep = '\t', file = ous)
    elif summ == 'v5':
        for elem, attr in sorted(mem):
            for key, val in zip(head5, quant(mem[elem, attr], 4)):
                print(elem, attr, what, key, val, sep = '\t', file = ous)
    elif summ == 'h11':
        print('elem', 'attr', 'stat', *head11, sep = '\t', file = ous)
        for elem, attr in sorted(mem):
            print(elem, attr, what, *quant(mem[elem, attr], 10),
                  sep = '\t', file = ous)
    elif summ == 'v11':
        for elem, attr in sorted(mem):
            for key, val in zip(head11, quant(mem[elem, attr], 10)):
                print(elem, attr, what, key, val, sep = '\t', file = ous)
    else:
        raise BadCode(summ + ' not implemented')
