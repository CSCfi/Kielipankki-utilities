# -*- mode: Python; -*-

'''Implementation of hrt-stat-data.'''

from libvrt.args import BadCode, BadData
from libvrt.args import nat
from libvrt.args import transput_args
from libvrt.stat import quant, sum_of_lengths, number_of_runs, max_length

from collections import defaultdict, Counter

import re

def parsearguments(args, *, prog = None):

    description = '''

    Show some statistic on the content of paragraph elements in an
    "HRT" document.

    '''

    parser = transput_args(description = description,
                           inplace = False)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--len', action = 'store_true',
                       dest = 'length',
                       help = '''

                       the number of code points

                       ''')

    group.add_argument('--num', choices = [ 'w', 'W', 's', 'S' ],
                       dest = 'num_such',                       
                       help = '''

                       the number of such codes (word character, not
                       word character, space, not space)

                       ''')

    group.add_argument('--run', choices = [ 'w', 'W', 's', 'S' ],
                       dest = 'num_runs',
                       help = '''

                       the number of maximal runs of such codes

                       ''')

    group.add_argument('--max', choices = [ 'w', 'W', 's', 'S' ],
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

    parser.add_argument('--limit', metavar = 'N',
                        type = nat,
                        default = 0,
                        help = '''

                        observe only so many paragraph elements
                        (except default 0 means all)

                        ''')

    args = parser.parse_args()
    args.prog = prog or parser.prog

    return args

REX = dict(w = r'\w+',
           W = r'\W+',
           s = r'\s+',
           S = r'\S+',)

def main(args, ins, ous):
    '''Transput HRT input stream in ins to TSV report in ous.

    TODO: adapt to ignore such tags that are allowed within sentences
    (need an option to list such); either allow or do not allow
    comments.

    '''

    data = (pair for pair in find_data(args, ins))
    if args.length:
        report_stats(data,
                     len, 'len',
                     args.summ, ous)
    elif args.num_such:
        regex = REX[args.num_such]
        report_stats(data,
                     sum_of_lengths(regex), 'num_' + args.num_such,
                     args.summ, ous)
    elif args.num_runs:
        regex = REX[args.num_runs]
        report_stats(data,
                     number_of_runs(regex), 'runs_' + args.num_runs,
                     args.summ, ous)
    elif args.max_length:
        regex = REX[args.max_length]
        report_stats(data,
                     max_length(regex), 'maxlen_' + args.max_length,
                     args.summ, ous)
    else:
        print('sorry, forgot to have a default stat', file = ous)

def find_data(args, ins):
    '''Yield each paragraph content block as a pair of the start tag line
    number and the content as a string.

    '''

    occurrences = 0
    klines = enumerate(ins, start = 1)
    while True:
        k, line = next(klines, (None, None))
        if line is None:
            return

        if line.startswith(('<paragraph>', '<paragraph ')):
            occurrences += 1

            yield k, ''.join(read_paragraph_lines(klines))
            if occurrences == args.limit:
                return

def read_paragraph_lines(klines):
    '''Read numbered lines, yield each line until </paragraph>.'''

    while True:
        _, line = next(klines)
        if line.startswith('</paragraph>'):
            return
        yield line

def report_stats(data, stat, what, summ, ous):
    '''Report on stat(para) for each para in data.

    '''
    if summ:
        mem = Counter()
        for _, para in data:
            mem[stat(para)] += 1
        summarize(mem, summ, what, ous)
        return

    # report each observation

    print('line', what, sep = '\t', file = ous)
    for line, para in data:
        print(line, stat(para), sep = '\t', file = ous)

def summarize(mem, summ, what, ous):
    head5 = ('min', 'lo', 'med', 'hi', 'max')
    head11 = ('min', 'd1', 'd2', 'd3', 'd4',
              'med', 'd6', 'd7', 'd8', 'd9', 'max')
    if summ == 'h5':
        print('stat', *head5, sep = '\t', file = ous)
        print(what, *quant(mem, 4), sep = '\t', file = ous)
    elif summ == 'v5':
        for key, val in zip(head5, quant(mem, 4)):
            print(what, key, val, sep = '\t', file = ous)
    elif summ == 'h11':
        print('stat', *head11, sep = '\t', file = ous)
        print(what, *quant(mem, 10), sep = '\t', file = ous)
    elif summ == 'v11':
        for key, val in zip(head11, quant(mem, 10)):
            print(what, key, val, sep = '\t', file = ous)
    else:
        raise BadCode(summ + ' not implemented')
