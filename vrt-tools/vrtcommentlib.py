#! /usr/bin/env python3
# -*- mode: Python; -*-


"""
Module vrtcommentlib

Utility functions for processing special VRT comments of the form
<!-- #vrt keyword: value -->.
"""


import re

from vrtargslib import BadData


_vrt_comment_expr = R"""
    <!-- \s \# vrt \s
    (?P<keywword> [A-Za-z0-9_-]+) : \s
    (?P<value> .+) \s
    --> \r? \n?
    """


_vrt_comment_re = re.compile(_vrt_comment_expr, re.ASCII | re.VERBOSE)
_bin_vrt_comment_re = re.compile(_vrt_comment_expr.encode('utf-8'),
                                 re.ASCII | re.VERBOSE)


def isvrtcomment(s):
    """Test if s is a special VRT comment line (string)."""
    return _vrt_comment_re.fullmatch(s) is not None


def isbinvrtcomment(bs):
    """Test if bs is a special VRT comment line (bytes)."""
    return _bin_vrt_comment_re.fullmatch(bs) is not None


def getvrtcomment(s):
    """Return pair (keyword, value) of special VRT comment line s."""
    matchobj = _vrt_comment_re.fullmatch(s)
    if matchobj is None:
        raise BadData('invalid special VRT comment')
    return matchobj.groups()


def getbinvrtcomment(bs):
    """Return pair (keyword, value) of special VRT comment bytes line bs."""
    matchobj = _bin_vrt_comment_re.fullmatch(bs)
    if matchobj is None:
        raise BadData('invalid special VRT comment')
    return matchobj.groups()


def makevrtcomment(keyword, value):
    """Return a special VRT comment line with keyword and value."""
    return '<!-- #vrt ' + keyword + ': ' + value + ' -->\n'


def makebinvrtcomment(keyword, value):
    """Return a special VRT comment bytes line with keyword and value."""
    return b'<!-- #vrt ' + keyword + b': ' + value + b' -->\n'
