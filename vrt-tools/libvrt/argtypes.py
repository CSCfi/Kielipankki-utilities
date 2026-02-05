
"""
Module libvrt.argtypes

This module contains functions that can be used as argument types in
argparse argument specifications.
"""


import re

from argparse import ArgumentTypeError

from libvrt.iterutils import find_duplicates


def encode_utf8(s):
    """Argument type function converting str s to UTF-8 bytes."""
    return s.encode('UTF-8')


def _listtype_base(s, check_func, unique=True, values_name='values'):
    """Base argument type function for a list of (unique) values.

    Items in the list string s can be separated by commas or spaces.
    Return a list of bytes.

    check_func is a function taking a list item as its argument and
    raising ArgumentTypeError if the item is invalid.

    Raise ArgumentTypeError with message ('duplicate ' + value_names +
    duplicate values), if unique and s contains duplicate values.
    """
    # Split by commas and spaces, and filter out empty strings
    attrs = [attr for attr in re.split(r'[,\s]+', s or '') if attr]
    for attr in attrs:
        check_func(attr)
    if unique:
        dupls = find_duplicates(attrs)
        if dupls:
            raise ArgumentTypeError(
                f'duplicate {values_name}: ' + ', '.join(dupls))
    return [attr.encode('UTF-8') for attr in attrs]


def attrlist(s):
    """Argument type function for a list of unique attribute names.

    The attribute specifications in str s can be separated by commas or spaces.
    Return a list of bytes.

    Raise ArgumentTypeError if the attribute list contains duplicates
    or if an attribute name is invalid.
    """

    def check_attr(attr):
        """Raise ArgumentTypeError if attr is an invalid attribute name."""
        if not re.fullmatch(r'[_a-z][_a-z0-9]*', attr):
            raise ArgumentTypeError(f'invalid attribute name: {attr}')

    return _listtype_base(s, check_attr, True, 'attribute names')


def _attr_regex_list_base(s):
    """Base argument type function for a list of unique attribute regexps.

    The attribute regular expressions in str s can be separated by
    commas or spaces.
    Return a list of regular expression strings (bytes).

    Raise ArgumentTypeError if the attribute regex list contains
    duplicates or if a regex is invalid or would match non-ASCII,
    non-printable or upper-case characters.
    """

    def check_attr(regex):
        """Raise ArgumentTypeError if regex is an invalid attribute regex."""
        msg_base = f'invalid attribute name regular expression: "{regex}"'

        def match_lower(regex):
            """Return True if regex does not match upper-case characters."""
            stripped = re.sub(r'\\[ABDSWZ]|\(\?P|\W|\d|_', '', regex)
            return not stripped or stripped.islower()

        # This does not guarantee in any way that regex matches only
        # valid attribute names, but try to check that it does not
        # match non-ASCII, non-printable or upper-case characters
        tests_types = [
            (lambda r: r.isascii(), 'non-ASCII'),
            (lambda r: r.isprintable(), 'non-printable'),
            (match_lower, 'upper-case'),
        ]
        for test, type_ in tests_types:
            if not test(regex):
                raise ArgumentTypeError(
                    f'{msg_base}: contains {type_} characters')
        try:
            re.compile(regex)
        except re.error as e:
            raise ArgumentTypeError(f'{msg_base}: {e}')

    return _listtype_base(
        s, check_attr, True, 'attribute name regular expressions')


def attr_regex_list_combined(s):
    """Argument type for a list of unique attribute regexps, combined.

    The attribute regular expressions in str s can be separated by
    commas or spaces.
    Return a compiled regular expression (bytes), with the list items
    as alternatives.

    Raise ArgumentTypeError if the attribute regex list contains
    duplicates or if a regex is invalid or would match non-ASCII,
    non-printable or upper-case characters.
    """
    return re.compile(b'|'.join(regex for regex in _attr_regex_list_base(s)))


def attr_regex_list_individual(s):
    """Argument type for a list of unique attribute regexps, individually.

    The attribute regular expressions in str s can be separated by
    commas or spaces.
    Return a list of compiled regular expressions (for bytes), one for
    each input list item.

    Raise ArgumentTypeError if the attribute regex list contains
    duplicates or if a regex is invalid or would match non-ASCII,
    non-printable or upper-case characters.
    """
    return [re.compile(regex) for regex in _attr_regex_list_base(s)]


def _attr_regex_list_value_base(s):
    """Base argument type function for attribute regex list and string value.

    s is of the form [[attr_regex_list]:]str, where attr_regex_list is
    a list of attribute name regular expressions, separated by commas
    or spaces, and str is a string value. If attr_regex_list is
    omitted, default to ".+"; the colon can then also be omitted
    unless str contains a colon.

    Return a pair (attr_regex_list, str), with str encoded as UTF-8.
    attr_regex_list is str.
    """
    if ':' not in s:
        s = '.+:' + s
    if s[0] == ':':
        s = '.+' + s
    regex_list, _, value = s.partition(':')
    return (regex_list, encode_utf8(value))


def attr_regex_list_combined_value(s):
    """Argument type function for attribute regex list and string value.

    s is of the form [[attr_regex_list]:]str, where attr_regex_list is
    a list of attribute name regular expressions, separated by commas
    or spaces, and str is a string value. If attr_regex_list is
    omitted, default to ".+"; the colon can then also be omitted
    unless str contains a colon.

    Return a pair (compiled_regex, str), where compiled_regex is a
    compiled regular expression (bytes), with the list items as
    alternatives, and str is the input str encoded as UTF-8 bytes.

    Raise ArgumentTypeError if the attribute regex list contains
    duplicates or if a regex is invalid.
    """
    regex_list, value = _attr_regex_list_value_base(s)
    return (attr_regex_list_combined(regex_list), value)


def attr_regex_list_individual_value(s):
    """Argument type function for attribute regex list and string value.

    s is of the form [[attr_regex_list]:]str, where attr_regex_list is
    a list of attribute name regular expressions, separated by commas
    or spaces, and str is a string value. If attr_regex_list is
    omitted, default to ".+"; the colon can then also be omitted
    unless str contains a colon.

    Return a list of pairs [(compiled_regex, str)], where each
    compiled_regex is a compiled regular expression (bytes) of one of
    the items in attr_regex_list and str is the input str encoded as
    UTF-8 bytes (the same for all pairs).

    Raise ArgumentTypeError if the attribute regex list contains
    duplicates or if a regex is invalid.
    """
    regex_list, value = _attr_regex_list_value_base(s)
    return [(regex, value) for regex in attr_regex_list_individual(regex_list)]


def check_unique(values, values_name='values'):
    """Raise `ArgumentTypeError` if `values` contains duplicates.

    The error message uses `values_name` to indicate what kind of
    values are in question (default ``values``).
    """
    dupls = find_duplicates(values)
    if dupls:
        raise ArgumentTypeError(
            f'duplicate {values_name}: ' + ', '.join(dupls))
    return values


def obtain_check_unique(values_name='values'):
    """Return a function checking that the values of an iterable are unique.

    The returned function takes one argument (an iterable). In case of
    duplicate values, the error message uses `values_name`.
    """
    return lambda values: check_unique(values, values_name)


def obtain_check_match(regex, value_name='value'):
    """Return a function checking that the argument matches `regex`.

    The returned function takes one argument (`str`), to be checked
    for matching `regex`. If it does not match, the function raises
    `ArgumentTypeError` with a message using `value_name`.
    """

    def _check_match(value):
        if not re.fullmatch(regex, value):
            raise ArgumentTypeError(f'invalid {value_name}: {value}')
        return value

    return _check_match


# TODO: Perhaps move the following function to a library module for
# functional programming utilites.

def compose_unary_rev(funcs, get_func=None):
    """Return a (reverse) composition of unary functions in iterable `funcs`.

    For a value ``[f1, f2, f3]``, return a function effectively
    working as ``f3(f2(f1(x)))`` (functions are applied in the order
    they are listed). If `get_func` is not `None`, get the actual
    functions to be composed by calling `get_func(f)` for each item
    `f` in `funcs`.
    """
    get_func = get_func or (lambda x: x)
    if len(funcs) == 1:
        return get_func(funcs[0])
    else:
        return lambda x: compose_unary_rev(funcs[1:], get_func)(
            get_func(funcs[0])(x))


def list_opts(seps=None, process_item=None, process_result=None,
              return_bytes=False, item_name='item'):
    """Return argument type function for a list of values, with options.

    Return an argument type function for a list of values separated by
    any of the characters in `seps` (`str`), each item processed with
    `process_item` and the whole result processed with
    `process_result`. The result is a list. If `return_bytes` ==
    `True`, convert the items to `bytes`. `item_name` is used in
    `ArgumentTypeError` messages.

    `process_item` can be a function of one `str` argument, a regular
    expression (`str`) or a list whose items are either of those. A
    function can return a modified value or check that the value is
    appropriate and return the value intact or raise
    `ArgumentTypeError` for an invalid value. A regular expression
    checks that the value fully matches the expression. If the value
    is a list, the functions are applied to the item in the order they
    are in the list, each function applied to the value returned by
    the previous one.

    `process_result` is similar to `process_item` but the functions
    take a list argument and return a list, and regular expressions
    are not supported.
    """

    def obtain_processor(process_value):
        """Return a function for processing values, based on `process_value`.

        If `process_value` is a callable, it is returned as such. If
        it is a list (of functions), return a composition of the
        functions, first function innermost. Otherwise, return an
        identity function. The functions should take one `str`
        argument and return the value (modified or intact) or raise
        `ArgumentTypeError`.
        """
        if isinstance(process_value, list):
            return compose_unary_rev(process_value, obtain_processor)
        elif callable(process_value):
            return process_value
        else:
            return lambda val: val

    def obtain_item_processor(process_value):
        """Return a function for processing items, based on `process_value`.

        Similar to `obtain_processor` but process_value (or its items)
        can also be regular expressions, in which case it is tested
        that a value fully matches the expression.
        """
        if isinstance(process_value, list):
            return compose_unary_rev(process_value, obtain_item_processor)
        elif isinstance(process_value, str):
            return obtain_check_match(process_value, item_name)
        else:
            return obtain_processor(process_value)

    # If the result should be converted to bytes, append encoding
    # function to process_item
    if return_bytes:
        process_item.append(encode_utf8)
    process_item = obtain_item_processor(process_item)
    process_result = obtain_processor(process_result)
    if seps is None:
        seps = ', '

    def _list(s):
        """Return a list from `s`.

        The list is processed according to arguments passed to the
        outer function.
        """
        if seps == '':
            return process_item(s)
        else:
            return process_result([process_item(item)
                                   for item in re.split(fr'[{seps}]+', s)])

    return _list


def keylist_valuelist_opts(
        key_seps=None, process_key=None, process_keylist=None,
        default_key=None, strip_key=False, key_name='key',
        value_seps=None, process_value=None, process_valuelist=None,
        default_value=None, strip_value=False, value_name='value',
        key_value_seps=None, return_bytes=False, arg_type_name=None):
    """Return argument type function for a pair of lists, with options.

    Return an argument type function converting a string to a pair of
    lists (keys and values), list of values separated by any number of
    any of the characters in `key_value_seps` (`str`). If
    `key_value_seps` is `""`, return only a list of values (a single
    `list`).

    Items in the list of keys and values are separated by any of the
    characters in `key_seps` and `value_seps` (`str`), respectively,
    each key and value processed with `process_key` and
    `process_value`, respectively, and the whole lists of keys and
    values processed with `process_keylist` and `process_valuelist`
    (see below for more details). If `strip_key` or `strip_value` is
    `True`, strip spaces from the beginning and end of the list of
    keys or values, respectively. `key_name` and `value_name` are used
    in `ArgumentTypeError` messages.

    If the argument string does not contain any character in
    `key_value_seps`, use `default_key` as the key if specified or
    `default_value` as the value if specified. If neither is
    specified, raise an `ArgumentTypeError`, whose message refers to
    `arg_type_name` if not `None`.

    `process_key` and `process_value` can be functions of one `str`
    argument, regular expressions (`str`) or lists whose items are
    either of those. A function can return a modified value or check
    that the value is appropriate and return the value intact or raise
    `ArgumentTypeError` for an invalid value. A regular expression
    checks that the value fully matches the expression. If the value
    is a list, the functions are applied to the item in the order they
    are in the list, each function applied to the value returned by
    the previous one.

    `process_keylist` and `process_valuelist` are similar to
    `process_key` and `process_value` but the functions take a list
    argument and return a list, and regular expressions are not
    supported.

    If `return_bytes` is `True`, convert all the items in the lists of
    keys and values to `bytes`.
    """

    def error(msg):
        raise ArgumentTypeError(
            msg + (f' in {arg_type_name}' if arg_type_name is not None else ''))

    def strip_if(s, cond):
        return s.strip() if cond else s

    if key_value_seps is None:
        key_value_seps = ':='

    def _keylist_valuelist(s):
        if key_value_seps == '':
            return list_opts(
                process_item=process_value, seps=value_seps,
                process_result=process_valuelist, item_name=value_name,
                return_bytes=return_bytes)(strip_if(s, strip_value))
        else:
            parts = re.split(fr'[{key_value_seps}]+', s, 1)
            if len(parts) == 1:
                if default_key is not None:
                    parts = [default_key, parts[0]]
                elif default_value is not None:
                    parts = [parts[0], default_value]
                else:
                    error(f'no {key_name}-{value_name} separator ('
                          + ', '.join(f'"{c}"' for c in key_value_seps) + ')')
            return (list_opts(process_item=process_key, seps=key_seps,
                              process_result=process_keylist,
                              item_name=key_name,
                              return_bytes=return_bytes)(
                                  strip_if(parts[0], strip_key)),
                    list_opts(process_item=process_value, seps=value_seps,
                              process_result=process_valuelist,
                              item_name=value_name,
                              return_bytes=return_bytes)(
                                  strip_if(parts[1], strip_value)))

    return _keylist_valuelist


def attr_value_opts(attrname_regex=None, attrname_prefix=None,
                    attrname_suffix=None, sepchars=None, strip_value=False,
                    return_bytes=False):
    """Return argument type function for attribute name and value, with options.

    Return an argument type function for an attribute name and string
    value with the specified properties: attribute name matches regexp
    `attrname_regex` (default `"[_a-z][_a-z0-9]*"`, used if `None`)
    that can be prefixed with `attrname_prefix` (`""`) and suffxed
    with `attrname_suffix` (`""`); value is separated from attribute
    name with one of the characters in `sepchars` (`":="`); if
    `strip_value` is `True`, whitespace characters are stripped from the value
    (whitespace is always stripped from the attribute name).

    The returned function takes a string argument and returns a pair
    `(attrname, str)`, both as `str`, or `bytes` if `return_bytes` is
    `True`.
    """

    attrname_regex = attrname_regex or '[_a-z][_a-z0-9]*'
    attrname_prefix = attrname_prefix or ''
    attrname_suffix = attrname_suffix or ''
    sepchars = sepchars or ':='
    enclose_val = r'\s*' if strip_value else ''
    convert_result = encode_utf8 if return_bytes else lambda x: x

    def _attr_value(s):
        """Argument type function for attribute name and string value."""
        mo = re.fullmatch(
            fr'\s*({attrname_prefix}{attrname_regex}{attrname_suffix})\s*'
            fr'[{sepchars}]{enclose_val}(.*?){enclose_val}', s)
        if not mo:
            if not any(c in s for c in sepchars):
                msg = ('no name-value separator ('
                       + ', '.join(f'"{c}"' for c in sepchars) + ')')
            else:
                attrname, val = re.split(fr'[{sepchars}]', s, 1)
                msg = f'invalid attribute name "{attrname.strip()}"'
            raise ArgumentTypeError(
                f'{msg} in attribute-value specification: {s}')
        return (convert_result(mo.group(1)), convert_result(mo.group(2)))

    return _attr_value


def attr_value_str(s):
    """Argument type function for attribute name and string value.

    s is of the form attrname(=|:)str. Whitespace around attrname is
    stripped, whereas that around str is preserved.

    Return a pair (attrname, str), both as str.
    """
    return attr_value_opts()(s)


def attr_value(s):
    """Argument type function for attribute name and string value.

    Similar to attr_value but return a pair (attrname, str), both as
    bytes.
    """
    return attr_value_opts(return_bytes=True)(s)
