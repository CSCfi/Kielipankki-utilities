# -*- coding: utf-8 -*-


"""
BYU corpus utilities

Works with at least Python 3.4.
"""


import re


def extract_dateinfo_from_url(url):
    """Extract date information from URL: return year (+ month (+ day))"""
    # This has been extracted from byu-wlp2vrt.py.
    # If generalized, this could be moved to korpimport.util.

    def zero_pad(s):
        s = s or ''
        if len(s) == 1:
            return '0' + s
        else:
            return s

    url_path = url.split('/', 3)[-1]
    mo = re.search(
        r'''\b (?P<year> (?: 19[89]\d | 200\d | 201[0-6] ) ) \b
            (?: (?P<sep> [-/] ) (?P<month> 0?[1-9] | 1[012] ) \b
                (?: (?P=sep) (?P<day> 0?[1-9] | [12][0-9] | 3[01] )
                    (?: (?P=sep) | [/.] | $ ) )?
            )?''',
        url_path, re.X)
    if not mo or not mo.group('month'):
        # If the above regex does not match or finds only a year, try
        # to find ISO short date yyyymm(dd), but only starting from
        # 2000.
        mo2 = re.search(
            r'''\b (?P<year> 200[0-9] | 201[0-6] )
                   (?P<month> 0[1-9] | 1[012] )
                   (?P<day> 0[1-9] | [12][0-9] | 3[01] )?
                \b''',
            url_path, re.X)
        if mo2:
            mo = mo2
        elif not mo:
            return ''
    year = mo.group('year')
    month = zero_pad(mo.group('month'))
    day = zero_pad(mo.group('day'))
    # This may return a year or a year and month only, which need
    # to be expanded later on (timespans-adjust-granularity.py
    # called by korp-convert-timedata.sh).
    return year + month + day
