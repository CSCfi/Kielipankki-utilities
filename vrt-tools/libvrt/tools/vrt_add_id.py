# -*- mode: Python; -*-

'''Implementation of vrt-add-id.'''

from argparse import ArgumentTypeError
from hashlib import sha1
from itertools import count, chain
from collections import defaultdict, OrderedDict
import math
import random
import re
import sys

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

# Maximum number of bytes to read from a random seed file
MAX_SEED_BYTES = pow(2, 20)

def affix(arg):
    if re.fullmatch('[A-Za-z0-9_\-+/.:]*', arg):
        return arg
    raise ArgumentTypeError('affix out of spec')

def intpow(arg):
    '''argparse argument type check for non-negative integer, 0x... or n^k'''
    if re.fullmatch('[0-9]+|0x[0-9A-Fa-f]+', arg):
        return int(arg, base = 0)
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

    epilog = '''

    The program contains two alternative methods of adding id
    attributes: a slower one with more features and a faster one with
    fewer features. The slower one is used in following cases: (1)
    with one or more of the options --no-optimize, --force, --sort and
    --rename; (2) if an id format refers to other replacement fields
    than {id}, {idnum[elem]}, {hash} and {hashN}; (3) if {id} or
    {idnum[elem]} for a certain element occurs with several different
    format specifications; or (4) if a format specification does not
    match the regular expression "[0-9]*[dxX]?".

    '''

    parser = transput_args(description = description, epilog = epilog)

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

    parser.add_argument('--no-optimize', action = 'store_false',
                        dest = 'optimize',
                        default = True,
                        help = '''

                        use the slower method even if the faster one
                        could be used (see below)

                        ''')

    parser.add_argument('--verbose', action = 'store_true',
                        help = '''

                        output to stderr the method used and the
                        number of ids added

                        ''')

    parser.add_argument('--element', '-e', metavar = 'name',
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
                       choices = ['random', 'counter'],
                       default = 'random',
                       help = '''

                       type of id values: "random" for unique random
                       integers, "counter" for integers based on a
                       counter ("random")

                       ''')

    group.add_argument('--seed', metavar = 'string',
                       action = grouped_arg(),
                       default = '',
                       help = '''

                       random number generator seed for random ids; if
                       specified before any --element, the element
                       name is included in the seed, producing a
                       different seed for each element type; to use
                       the same seed for multiple element types,
                       specify it explicitly after each --element; if
                       string begins with "<", the rest is the name of
                       the file whose content (up to 1 MiB) to use as
                       the seed (default: "" = non-reproducible)

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
                       with the integer id value, "{idnum[elem]}" with
                       the integer id value for element elem, and
                       "{elem[attr]}" with the string value of the
                       existing attribute attr in the current or an
                       enclosing element (the current element can also
                       be referred to as "this"); formatting string
                       values is extended with regular expression
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
    args.prog = prog or parser.prog
    # If no elements have been specified, make all options pertain to
    # default_element
    if not args.element:
        args.element = {default_element: args}
    # Faster method cannot overwrite existing attributes nor sort them
    explain_slower(args,
                   [(not args.optimize, '--no-optimize'),
                    (args.force, '--force'),
                    (args.sort, '--sort')])
    args.optimize = args.optimize and not (args.force or args.sort)
    # print(args)
    elem_names = [name.decode('UTF-8') for name in args.element.keys()]
    # Set some defaults for all elements
    for elem, elem_args in args.element.items():
        set_defaults(elem, elem_args, args)
        check_format(elem_args.format, elem_names, args.prog)
        optimizable, reason = check_optimizable(elem, elem_args)
        if args.optimize and not optimizable:
            explain_slower(args, reason)
            args.optimize = False
    return args

def explain_slower(args, tests):
    '''Explain why the slower method is used.

    tests is either a list of pairs (test, reason), where test is a
    Boolean and reason a string, or a single string corresponding to
    [(True, string)]. If args.verbose and at least one of the tests is
    True, print to stderr the reason corresponding to the first test
    that is True.
    '''

    if args.verbose:
        if not isinstance(tests, list):
            tests = [(True, tests)]
        for test, reason in tests:
            if test:
                print_verbose(
                    args, f'using the slower method because of {reason}')
                break

def print_verbose(args, *print_args, **kwargs):
    '''If args.verbose, print *print_args (with **kwargs)'''
    if args.verbose:
        print(args.prog + ':', *print_args, **kwargs, file=sys.stderr)

def set_defaults(elem, elem_args, args):
    '''Set some defaults in `elem_args` (for element `elem`) from `args`.'''
    if not elem_args.type:
        elem_args.type = 'random'
    if not elem_args.seed:
        elem_args.seed = None
    else:
        # If using the seed specified as a default, prepend element
        # name to use different seeds for different elements
        prefix = elem if elem_args.seed == args.seed else b''
        if elem_args.seed[0] == '<':
            elem_args.seed = read_file_content(elem_args.seed[1:].strip(),
                                               MAX_SEED_BYTES, args.prog)
        else:
            elem_args.seed = elem_args.seed.encode('UTF-8')
        elem_args.seed = prefix + elem_args.seed
    elem_args.format = elem_args.prefix + (
        expand_hashes(elem_args.format, args.hash) or (
            '{id'
            + (':0' + str(get_hexvalue_len(elem_args.end)) + 'x}'
               if elem_args.type == 'random'
               else '}'))
    )

def read_file_content(filename, max_bytes, prog='vrt-add-id'):
    '''Return up to max_bytes bytes from the beginning of file filename.

    An IOError when trying to read the file causes the program to
    terminate with an error message and exit code 1.
    '''

    try:
        with open(filename, 'rb') as f:
            return f.read(max_bytes)
    except IOError as e:
        error(prog, f'cannot read random seed from file {filename}: {e}')
    # Should never get here
    return None

def error(prog, *args):
    '''Print "{prog}: error: {*args}" to stderr and exit with code 1.'''
    print(f'{prog}: error:', *args, file=sys.stderr)
    exit(1)

def check_format(fmt, elem_names, prog):
    '''If fmt contains an invalid replacement field or format, exit with error.

    elem_names is a list of element names (str) to which to add ids;
    prog is the name of the script (for error messages).
    '''

    def _error(repl_field, msg):
        '''Error message ending in msg: {repl_field}.'''
        error(prog, f'{msg}: {{{repl_field}}}')

    def check_formatspec(repl_field, formatspec, type_):
        '''Error if formatting using formatspec for type_ fails.'''
        typestr = 'an integer' if type_ == int else 'a string'
        try:
            f'{{:{formatspec}}}'.format(type_(1))
        except ValueError as e:
            msg = str(e).rstrip('.')
            msg = msg[0].lower() + msg[1:]
            _error(repl_field,
                   f'invalid format specification for {typestr}-valued'
                   f' format replacement field: {msg}')

    repl_fields = get_format_fields(fmt)
    elemnames_re = '(?:' + '|'.join(elem_names) + ')'
    for repl_field in repl_fields:
        mo = re.fullmatch(r'(.*?)(?:(/.*?/.*?/))?(?::(.*?))?', repl_field)
        fieldname, subst, formatspec = mo.groups()
        if re.fullmatch(r'hash([1-9][0-9]?)?', fieldname):
            # {hashN} for specified hash values have already been
            # expanded
            num = int(fieldname[4:] or 1)
            msgpart = 'no' if num == 1 else f'fewer than {num}'
            _error(repl_field, ('invalid format replacement field as'
                                f' {msgpart} --hash options were specified'))
        elif not re.fullmatch(
                r'(id|([a-z][a-z0-9]*)\[([a-z0-9_]+)\])', fieldname):
            # Replacement field name must be "id", "idnum[elem]" or
            # "elem[attr]"
            _error(repl_field, 'unsupported format replacement field')
        elif (re.fullmatch(r'idnum\[.*?\]', fieldname)
              and not re.fullmatch(rf'id|idnum\[{elemnames_re}\]', fieldname)):
            # idnum[elem] only works if ids are added to elem
            _error(repl_field,
                   'elem in format replacement field idnum[elem] must be the'
                   ' name of one of the elements to which ids are added')
        elif re.fullmatch(rf'id|idnum\[{elemnames_re}\]', fieldname):
            # id and idnum[elem] are int-valued
            if subst:
                _error(repl_field,
                       'substitutions not allowed for integer-valued format'
                       ' replacement fields id and idnum[elem]')
            elif formatspec:
                # If a format specification is specified, try to
                # format an integer to see if it works
                check_formatspec(repl_field, formatspec, int)
        elif formatspec:
            # Others are string-valued; if a format specification is
            # specified, try to format a string to see if it works
            check_formatspec(repl_field, formatspec, str)

def get_format_fields(fmt):
    '''Return replacement fields (no curly brackets) in format string fmt.'''
    fmt = fmt.replace('{{', '').replace('}}', '')
    return re.findall(r'\{(.*?)\}', fmt)

def check_optimizable(elem, elem_args):
    '''Check if elem_args for elem would allow using a faster method.

    Return a pair (optimizable: bool, reason: str), where reason
    explains why the faster method cannot be used, or (True, None), if
    the faster method can be used.
    '''

    # The faster method cannot rename attributes
    if elem_args.rename:
        return (False, '--rename')

    # Format can contain only {id} and {idnum[*]}, optionally with
    # simple formatting :[0-9]*[dxX]?
    # idnum[elem] is the same as id
    fmt = elem_args.format.replace(
        '{idnum[{' + elem.decode('UTF-8') + '}]', '{id')
    repl_fields = get_format_fields(fmt)
    non_optimizable_fields = [
        repl_field for repl_field in repl_fields
        if not re.fullmatch(r'(id|idnum\[[a-z0-9]+\])(:.*)?', repl_field)]
    if non_optimizable_fields:
        return (False,
                '--format replacement field other than {id} or {idnum[elem]}: {'
                + non_optimizable_fields[0] + '}')
    too_complex_format = [
        repl_field for repl_field in repl_fields
        if not re.fullmatch(r'([^:]+)(:[0-9]*[dxX]?)?', repl_field)]
    if too_complex_format:
        return (False,
                'format specification not matching "[0-9]*[dxX]?": {'
                + too_complex_format[0] + '}')

    # Check that the same idnum[elem] is not used with different
    # formats; use the keys of OrderedDict to preserve the input order
    # unlike set
    id_formats = defaultdict(OrderedDict)
    for repl_field in repl_fields:
        fieldname, _, format_ = repl_field.partition(':')
        id_formats[fieldname][format_] = ''
        if len(id_formats[fieldname]) > 1:
            return (False, ('using {' + fieldname + '} with different format'
                            ' specifications: '
                            + ', '.join(id_formats[fieldname].keys())))

    return (True, None)

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

    # If args.optimize == True, check if the faster method in
    # fast_main can be used: check the first instance of each type of
    # element for not having an attribute with the name of the id
    # attribute, process the lines that far in this function and the
    # rest in fast_main; otherwise, process all lines here.

    id_elem_names_list = list(args.element.keys())
    # Names of elements to which to add ids
    id_elem_names = set(elem for elem in id_elem_names_list)

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
    # Number of ids added (used only with --verbose)
    id_counts = dict((elem, 0) for elem in id_elem_names_list)

    # Whether to check for optimization
    check_optimize = args.optimize
    # The names of elements whose contents have been checked for
    # optimization
    checked_elems = set()
    verbose = args.verbose

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

                    if check_optimize:
                        if elem_args.idn in attrs:
                            # If the id attribute already exists,
                            # cannot optimize (and this causes
                            # "element has id already")
                            check_optimize = False
                        else:
                            checked_elems.add(elem)
                            if checked_elems == id_elem_names:
                                # If all types of elements have been
                                # checked, use the faster method for
                                # this line and the rest of ins
                                print_verbose(args, 'using the faster method')
                                fast_main(args, chain([line], ins),
                                          ous, id_elem_names, ids, idnums,
                                          id_counts)
                                break

                    if (args.force or elem_args.rename
                            or elem_args.idn not in attrs):
                        if elem_args.rename and elem_args.idn in attrs:
                            rename_attr(attrs, elem_args.idn, elem_args.rename)
                        id = next(ids[elem])
                        idnums[elem] = id
                        try:
                            attrs[elem_args.idn] = (
                                formatter.format(
                                    elem_args.format,
                                    id = id,
                                    this = attrs,
                                    idnum = idnums,
                                    **elem_attrs
                                ).encode('UTF-8'))
                        except KeyError as e:
                            estr = str(e).replace('b\'', '\'')
                            raise BadData(
                                'format replacement field '
                                f'{elem_args.format}: key {estr} not found')
                        if verbose:
                            id_counts[elem] += 1
                    else:
                        raise BadData('element has id already')
                    line = starttag(elem, attrs, sort = args.sort)

        ous.write(line)

    if check_optimize and verbose:
        # Some element types did not occur
        non_occurring_elems = [
            elem.decode('UTF-8')
            for elem in sorted(id_elem_names - checked_elems)]
        if non_occurring_elems:
            explain_slower(
                args, 'not finding elements ' + ', '.join(non_occurring_elems))
    elems_added = ', '.join(f'{id_counts[elem]} {elem.decode("UTF-8")} ids'
                            for elem in id_elem_names_list)
    print_verbose(args, 'added ' + elems_added)

def fast_main(args, ins, ous, id_elem_names, ids, idnums_curr, id_counts):
    '''A faster main loop.

    args, ins and ous are as for main. id_elem_names are the names of
    elements to which to add ids (bytes), ids is a dict of id
    generators and idnums_curr are the currently active numeric id
    values.

    This function does not work with --force, --sort, --rename, nor
    with id formats that contain other replacement fields than {id},
    {idnum[elem]} (and {hash*}, which are expanded earlier), nor if
    the same {id} or {idnum[elem]} occur with different format
    specifications, nor if a format specification does not match the
    regular expression "[0-9]*[dxX]?". These should be checked in
    advance.
    '''

    def make_format_funcs(elem, fmt, idnums):
        '''Make formatting functions for idnum and whole id of elem with fmt.'''
        # It seems that idnums need to be passed as an argument for it
        # to be accessible in the eval'ed lambda: it does not work if
        # it is defined in the outer function above this one even if
        # passing globals() and/or locals() to eval().

        # Protect double curly brackets
        fmt = fmt.replace('{{', '\x01').replace('}}', '\x02')
        idnum_format_func = None
        # Split fmt to replacement fields and fixed strings
        parts = re.findall(r'{.*?}|[^{]+', fmt)

        for i, part in enumerate(parts):
            if part[0] == '{':
                # Replacement field
                part = part[1:-1]
                # Split replacement field to field name and format
                # spec
                part, _, formatspec = part.partition(':')
                if part in ('id', f'idnum[{elem}]'):
                    # Id num for the current element
                    part = f'idnums[{elem}]'
                    # f'{id}' seems to be faster than str(id), at
                    # least in Python 3.10.12
                    func_text = (
                        'lambda id: f"{id'
                        + (':' + formatspec if formatspec else '')
                        + '}"')
                    # print(func_text)
                    idnum_format_func = eval(func_text)
                else:
                    # Id num for an enclosing element
                    part = re.sub(r'idnum\[(.*?)\]', r'idnums[b"\1"]',
                                  part)
                parts[i] = part
            else:
                # Fixed string
                part = part.replace('\x01', '{{').replace('\x02', '}}')
                parts[i] = f'b"{part}"'

        func_text = 'lambda: ' + ' + '.join(parts)
        # print(func_text)
        format_func = eval(func_text, locals())
        return format_func, idnum_format_func

    def append_attr(line, name, value):
        '''Return line (VRT/XML start tag) with name="value" appended.'''
        return line[:-2] + b' ' + name + b'="' + value + b'">\n'

    # Whole id formatting functions for each element type
    format_id = {}
    # Id number formatting functions for each element type
    format_idnum = {}

    # The formatted id numbers for each element type
    idnums = dict((elem, None) for elem in id_elem_names)

    verbose = args.verbose

    for elem in args.element:
        # Make the whole id and id number formatting functions for
        # elem
        format_id[elem], format_idnum[elem] = make_format_funcs(
            elem, args.element[elem].format, idnums)
        # Format the current id numbers for the start tags to which
        # ids were added in main
        if idnums_curr[elem]:
            idnums[elem] = format_idnum[elem](idnums_curr[elem]).encode('UTF-8')

    for line in ins:
        if ismeta(line) and isstarttag(line):
            elem = element(line)
            if elem in id_elem_names:
                elem_args = args.element[elem]
                id = next(ids[elem])
                idnums[elem] = format_idnum[elem](id).encode('UTF-8')
                if verbose:
                    id_counts[elem] += 1
                line = append_attr(line, elem_args.idn, format_id[elem]())
        ous.write(line)

def get_idgen(args):
    '''Return id generator based on args.'''

    if args.type == 'counter':
        # Generator for an integer counter
        return (
            k for k in count(start = args.start)
        )

    else:
        return randint_uniq(args.end, args.seed)

def randint_uniq(end, seed = None):
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
    order of attributes in attrs changes.
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
