'''A vrt tool implementation to combine the values of a sentence
attribute into summary attributes in containing paragraph and text
elements, assuming sentence elements are contained in paragraph and
text elements.

Initially meant to combine language codes, and in any case meant to
combine values that can be meaningfully counted.

'''

from collections import Counter
from re import search, findall

from libvrt.args import transput_args
from libvrt.elements import text_elements
from libvrt.metaline import mapping

# hm libvrt.metaname appears to have similar so one is once again
# duplicating one's efforts?
from libvrt.nameargs import nametype, prefixtype, suffixtype

def parsearguments(argv, *, prog = None):

    description = '''

    Count the occurrences of different values of a sentence attribute
    into corresponding summary attributes in containing paragraph and
    text elements. Counts are listed in decreasing order, ties in the
    alphabetical order of the value.

    '''

    parser = transput_args(description = description)

    parser.add_argument('--attr', '-a', metavar = 'name',
                        required = True,
                        type = nametype,
                        help = '''

                        sentence attribute to summarize

                        ''')
    
    parser.add_argument('--prefix', '-p', metavar = 'fix',
                        default = 'sum_',
                        type = prefixtype,
                        help = '''

                        prefix to the summary attribute names
                        (default "sum_")

                        ''')

    parser.add_argument('--suffix', '-s', metavar = 'fix',
                        default = '',
                        type = suffixtype,
                        help = '''

                        suffix to the summary attribute names
                        (default empty)

                        ''')

    parser.add_argument('--missing', metavar = 'value',
                        default = b'NSA', # No Such Attribute
                        type = str.encode,
                        help = '''

                        imputed value when sentence does not have the
                        attribute (default NSA, for No Such Attribute)

                        ''')

    # parser.add_argument('--sort', choices = ['value', 'count'],
    #                    default = 'value',
    #                    help = '''
    #
    #                    primary sort key (default is decreasing count,
    #                    break ties by code) [option has no effect]
    #
    #                    ''')

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog
    return args

def main(args, ins, ous):
    '''Transput VRT (bytes) in ins to VRT (bytes) in ous.'''

    # regex matches the sentence attribute, captures the value
    observed = b'(?<= )' + args.attr + b'="(.*?)"'

    # summary name to use in paragraph and text elements
    reported = args.prefix + args.attr + args.suffix

    for group in text_elements(ins, ous,
                               as_text = False):
        # lines outside any text element are shipped to ous, while
        # lines inside are collected, annotated, then shipped here
        text = list(group)
        summarize(text, observed, reported, args)
        for line in text:
            ous.write(line)

def summarize(text, observed, reported, args, *,
              paradist = Counter(), textdist = Counter()):
    '''

    '''
    for k, line in enumerate(reversed(text), start = 1 - len(text)):
        if line.startswith((b'<sentence ', b'<sentence>')):
            mo = search(observed, line)
            value = (mo.group(1) if mo else args.missing)
            paradist[value] += 1
            textdist[value] += 1
        elif line.startswith((b'<paragraph ', b'<paragraph>')):
            meta = mapping(line)
            meta[reported] = renderdist(paradist, _bycount, args)
            text[-k] = renderstart(b'paragraph', meta)
        elif line.startswith((b'<text ', b'<text>')):
            meta = mapping(line)
            meta[reported] = renderdist(textdist, _bycount, meta)
            text[-k] = renderstart(b'text', meta)
        elif line.startswith(b'</text>'):
            textdist.clear()
        elif line.startswith(b'</paragraph>'):
            paradist.clear()
        pass

def _bycount(pair):
    '''Sort key to sort (b'key', count) by decreasing count, breaking ties
    by key.

    '''
    key, val = pair
    return (-val, key)

def renderdist(dist, by, args):
    '''Render the observed distribution as |-separated key:count
    assignments in the order on (b'key', count) specified by by.
    Decreasing order by count may work well for some purposes in Korp.

    '''
    if not dist:
        return b'|'

    return b'|'.join((b'',
                      *(key + b':' + str(value).encode('utf-8')
                        for key, value
                        in sorted(dist.items(), key = by)),
                      b''))

def renderstart(name, meta):
    '''Render start tag line for the element name (paragraph or text) and
    the meta dict (values already rendered).

    '''
    return b''.join((b'<', name,
                     *(b' ' + key + b'="' + value + b'"'
                       for key, value in sorted(meta.items())),
                     b'>\n'))
