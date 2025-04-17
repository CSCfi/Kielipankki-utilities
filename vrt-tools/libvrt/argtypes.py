
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


def attr_value_str(s):
    """Argument type function for attribute name and string value.

    s is of the form attrname(=|:)str. Whitespace around attrname is
    stripped, whereas that around str is preserved.

    Return a pair (attrname, str), both as str.
    """
    mo = re.match(r'\s*([_a-z][_a-z0-9]*)\s*[:=](.*)', s)
    if not mo:
        if ':' not in s and '=' not in s:
            msg = 'no ":" nor "="'
        else:
            attrname, val = re.split(r'[:=]', s, 1)
            msg = f'invalid attribute name "{attrname.strip()}"'
        raise ArgumentTypeError(f'{msg} in attribute-value specification: {s}')
    return (mo.group(1), mo.group(2))


def attr_value(s):
    """Argument type function for attribute name and string value.

    Similar to attr_value but return a pair (attrname, str), both as
    bytes.
    """
    return tuple(encode_utf8(val) for val in attr_value_str(s))
