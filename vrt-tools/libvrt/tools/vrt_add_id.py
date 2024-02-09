# -*- mode: Python; -*-

'''Implementation of vrt-add-id.'''

from argparse import ArgumentTypeError
from hashlib import sha1
from itertools import count
import math
import random
import re

from libvrt.args import BadData
from libvrt.args import transput_args

from libvrt.groupargs import grouping_arg, grouped_arg

from libvrt.metaname import nametype # need checked
from libvrt.metaline import (
    mapping, starttag, ismeta, isstarttag, isendtag, element)

from libvrt.strformatters import PartialFormatter
from libvrt.strformatters import SubstitutingBytesFormatter

# Default maximum random id value (DEFAULT_RAND_END - 1)
DEFAULT_RAND_END = pow(2, 32)

def affix(arg):
    if re.fullmatch('[A-Za-z0-9_\-+/.:]*', arg):
        return arg
    raise ArgumentTypeError('affix out of spec')

def intpow(arg):
    '''argparse argument type check for non-negative integer, 0x... or n^k'''
    if re.fullmatch('[0-9]+|0x[0-9A-Fa-f]+', arg):
        return int(arg, base=0)
    elif re.fullmatch(r'[0-9]+\^[0-9]+', arg):
        base, exp = arg.split('^')
        return pow(int(base), int(exp))
    raise ArgumentTypeError('number out of spec')

def parsearguments(argv, *, prog = None):

    default_element = b'sentence'

    description = '''

    Add or overwrite an "id" attribute to each element of the
    specified kind, based on a counter or unique random values.

    '''

    parser = transput_args(description = description)

    parser.add_argument('--hash', metavar = 'string',
                        action = 'append',
                        help = '''

                        make "{hash}" in the id format string refer to
                        the hex digest of the SHA-1 hash of string; if
                        the option is repeated, "{hashN}" refers to
                        the Nth value

                        ''')

    parser.add_argument('--force', action = 'store_true',
                        help = '''

                        overwriting an existing id

                        ''')

    parser.add_argument('--sort', action = 'store_true',
                        help = '''

                        sort element attributes alphabetically
                        (default: keep input order)

                        ''')

    parser.add_argument('--element', metavar = 'name',
                        action = grouping_arg(),
                        type = nametype,
                        # Default for --element is set only later, to
                        # make it work correctly with grouping_arg
                        # default = b'sentence',
                        help = '''

                        name of the VRT element to use; can be
                        repeated; if no --element is specified, use
                        "sentence"

                        ''')

    group = parser.add_argument_group(
        'element-specific options',
        '''

        The following options can be specified multiple times: each
        occurrence applies to the --element after which it is
        specified. If an option is specified before any --element, it
        becomes the default for all elements.

        ''')

    group.add_argument('--id', dest = 'idn', metavar = 'name',
                       action = grouped_arg(),
                       type = nametype,
                       default = b'id',
                       help = '''

                       name of the "id" attribute ("id")

                       ''')

    group.add_argument('--type',
                       action = grouped_arg(),
                       choices = ['counter', 'random'],
                       default = 'counter',
                       help = '''

                       type of id values: "counter" for integers based
                       on a counter, "random" for unique random
                       integers ("counter")

                       ''')

    group.add_argument('--seed', metavar = 'string',
                       action = grouped_arg(),
                       default = '',
                       help = '''

                       random number generator seed for random ids
                       (default: "" = non-reproducible)

                       ''')

    group.add_argument('--start', metavar = 'number',
                       action = grouped_arg(),
                       type = int,
                       default = 1,
                       help = '''

                       initial value for the counter (1)

                       ''')

    group.add_argument('--end', metavar = 'number',
                       action = grouped_arg(),
                       type = intpow,
                       default = DEFAULT_RAND_END,
                       help = '''

                       maximum random id value is number - 1; a
                       non-negative integer, hexadecimal if prefixed
                       with "0x", or n^k for n to the power of k
                       (default: 2^32)

                       ''')

    group.add_argument('--format', metavar = 'format',
                       action = grouped_arg(),
                       help = '''

                       format string for id, with Python
                       str.format-style formatting: "{id}" is replaced
                       with the id value, "{idnum[elem]}" with the id
                       value for element elem, and "{elem[attr]}" with
                       the value of the existing attribute attr in the
                       current or an enclosing element (the current
                       element can also be referred to as "this");
                       formatting is extended with regular expression
                       substitutions: "{elem[attr]/regexp/subst/}" is
                       "{elem[attr]}" with all matches of regexp
                       replaced with subst; subst may refer to groups
                       in regexp as \\N, \\g<N> or \\g<name>; multiple
                       substitutions are separated by commas,
                       semicolons or spaces (default: with
                       --type=counter, "{id}"; with --type=random,
                       "{id:0*x}" where * is the minimum number of hex
                       digits to represent the maximum value)

                       ''')

    group.add_argument('--prefix', metavar = 'affix',
                       action = grouped_arg(),
                       type = affix,
                       default = '',
                       help = '''

                       additional prefix text to each formatted id,
                       prepended to the format string specified with
                       --format ("")

                       ''')

    group.add_argument('--rename', metavar = 'name',
                       action = grouped_arg(),
                       nargs = '?',
                       type = lambda s: s.encode('UTF-8'),
                       # const value used if no argument
                       const = b'{}_orig',
                       help = '''

                       rename possible existing id attribute to name;
                       name may contain "{}" to be replaced with the
                       original name; if also the renamed attribute
                       already exists, append to the name "_N" where N
                       is the smallest positive integer for which the
                       resulting attribute does not exist; if name is
                       omitted, "{}_orig" is used

                       ''')

    args = parser.parse_args()
    # If no elements have been specified, make all options pertain to
    # default_element
    if not args.element:
        args.element = {default_element: args}
    # Set some defaults for all elements
    for elem_args in args.element.values():
        set_defaults(elem_args, args)
    args.prog = prog or parser.prog
    return args

def set_defaults(elem_args, args):
    '''Set some defaults in `elem_args` from `args`.'''
    if not elem_args.type:
        elem_args.type = 'counter'
    if not elem_args.seed:
        elem_args.seed = None
    elem_args.format = elem_args.prefix + (
        expand_hashes(elem_args.format, args.hash) or (
            '{id'
            + (':0' + str(get_hexvalue_len(elem_args.end)) + 'x}'
               if elem_args.type == 'random'
               else '}'))
    )

def expand_hashes(format_, strlist):
    '''Expand {hashN} in format_ to SHA-1 hex digest of strlist[N].

    {hash} is an alias for {hash1}.

    As hash values are constant for all ids, it suffices to expand
    them once in the id format string, avoiding the need to re-expand
    them for each id.
    '''

    if not strlist:
        return format_

    hashvals = {}
    for i, s in enumerate(strlist):
        hashvals[f'hash{i + 1}'] = sha1(s.encode('UTF-8')).hexdigest()
    hashvals['hash'] = hashvals['hash1']

    # This keeps the non-hash format specs in format_ intact
    return PartialFormatter(None).format(format_, **hashvals)

def main(args, ins, ous):
    '''Transput VRT (bytes) in ins to VRT (bytes) in ous.'''

    # Names of elements to which to add ids
    id_elem_names = set(elem for elem in args.element.keys())

    # Id generators for each element
    ids = {}
    for elem in id_elem_names:
        ids[elem] = get_idgen(args.element[elem])

    formatter = SubstitutingBytesFormatter()

    # The numeric, unformatted base ids of each currently open element
    # to which ids are added
    idnums = dict((elem, None) for elem in id_elem_names)
    # elem_attrs keys are string values for elem, as they are used as
    # keyword argument names to formatter.format and bytes values
    # cannot be used as keyword argument names
    elem_attrs = {}

    for line in ins:
        if ismeta(line):
            elem = element(line)
            elem_s = elem.decode('UTF-8')
            if isendtag(line):
                del elem_attrs[elem_s]
            elif isstarttag(line):
                attrs = elem_attrs[elem_s] = mapping(line)
                if elem in id_elem_names:
                    # Element-specific options
                    elem_args = args.element[elem]
                    if (args.force or elem_args.rename
                            or elem_args.idn not in attrs):
                        if elem_args.rename and elem_args.idn in attrs:
                            rename_attr(attrs, elem_args.idn, elem_args.rename)
                        id = next(ids[elem])
                        idnums[elem] = id
                        attrs[elem_args.idn] = (
                            formatter.format(
                                elem_args.format,
                                id=id,
                                this=attrs,
                                idnum=idnums,
                                **elem_attrs
                            ).encode('UTF-8'))
                    else:
                        raise BadData('element has id already')
                    line = starttag(elem, attrs, sort=args.sort)
        ous.write(line)

def get_idgen(args):
    '''Return id generator based on args.'''

    if args.type == 'counter':
        # Generator for an integer counter
        return (
            k for k in count(start = args.start)
        )

    else:
        # Multiple generators use different seeds
        if args.seed:
            args.seed += '1'
        return randint_uniq(args.end, args.seed)

def randint_uniq(end, seed=None):
    '''Generator for unique random integers in [0, end[ with seed.'''

    # Values already generated
    used = set()
    rnd = random.Random(seed)
    errmsg = f'more than {end} elements encountered; please increase --end'

    while True:
        if len(used) >= end:
            raise BadData(errmsg)
        r = rnd.randrange(0, end)
        i = 0
        while r in used:
            r = rnd.randrange(0, end)
            i += 1
            # If 1000 consecutive random numbers have already been
            # used, raise an error (1000 is arbitrary)
            if i > 1000:
                raise BadData(errmsg)
        used.add(r)
        yield r

def rename_attr(attrs, old, new):
    '''Rename attribute old to new in dict attrs.

    If new contains "{}", replace it with old. If an attribute with
    the resulting name exists in attrs, append "_N" to the name where
    N is the smallest positive integer for which the resulting
    attribute name does not exist in attrs.

    Effectively adds new with the value of old and deletes old, so the
    order attributes in of attrs changes.
    '''

    if b'{}' in new:
        new = new.replace(b'{}', old)
    new_base = new + b'_'
    n = 1
    while new in attrs:
        new = new_base + str(n).encode('UTF-8')
        n += 1
    attrs[new] = attrs[old]
    del attrs[old]

def get_hexvalue_len(value):
    '''Return the number of hex digits required to represent value - 1'''
    return math.ceil(math.log(value) / math.log(16))
