
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


def attr_regex_list(s):
    """Argument type function for a list of unique attribute regexps.

    The attribute regular expressions in str s can be separated by
    commas or spaces.
    Return a compiled regular expression (bytes), with the list items
    as alternatives.

    Raise ArgumentTypeError if the attribute regex list contains
    duplicates or if a regex is invalid.
    """

    def check_attr(regex):
        """Raise ArgumentTypeError if attr is an invalid attribute regex."""
        try:
            re.compile(regex)
        except re.error as e:
            raise ArgumentTypeError(
                f'invalid attribute name regular expression: "{regex}": {e}')

    return re.compile(
        b'|'.join(
            regex for regex in _listtype_base(
                s, check_attr, True, 'attribute name regular expressions')))


def attr_regex_list_value(s):
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
    if ':' not in s:
        s = '.+:' + s
    if s[0] == ':':
        s = '.+' + s
    regex_list, _, value = s.partition(':')
    return (attr_regex_list(regex_list), encode_utf8(value))
