# -*- mode: Python; -*-

'''Implement hrt-normalize-lines.

'''

from itertools import filterfalse, groupby

from libvrt.args import transput_args

def parsearguments(argv):
    description = '''

    Remove all empty lines outside <paragraph>, leading and trailing
    empty lines inside <paragraph>, and duplicate internal empty lines
    inside <paragraph>. Count any Unicode all-whitespace line as
    empty, counting NO-BREAK SPACE as another whitespace character.
    Normalize remaining empty lines so that they are actually empty
    (up to whatever line termination indicator they happen to have).
    All input is expected to be in <paragraph> and none in <sentence>.

    '''

    parser = transput_args(description = description)
    args = parser.parse_args(argv)
    args.prog = parser.prog
    return args

def isparatag(line):
    return line.startswith(('<paragraph>',
                            '<paragraph ',
                            '</paragraph>'))

def main(args, ins, ous):

    inside = False
    for istags, lines in groupby(ins, isparatag):
        if istags:
            for line in lines:
                inside = line.startswith(('<paragraph>', '<paragraph '))
                print(line, end = '', file = ous)

        elif inside:
            datalines = groupby(lines, str.isspace)

            # omit any leading and trailing space lines
            isspace, data = next(datalines)
            isspace or print(*data, sep = '', end = '', file = ous)

            previsspace = False
            for isspace, data in datalines:
                if previsspace: print(file = ous)
                previsspace = isspace
                isspace or print(*data, sep = '', end = '', file = ous)
            else:
                pass

        else:
            print(*filterfalse(str.isspace, lines),
                  sep = '', end = '', file = ous)
