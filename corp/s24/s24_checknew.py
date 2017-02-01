#!/usr/bin/env python
# -*- coding: utf-8 -*

import urllib2
import re
import sys

"""
asahala/FIN-CLARIN

Use this script to check how many API pages have been added
since the last update.

You should always update ´newest´ after retrieving a JSON set
from the API or include the last retrieved page in a readme file
distributed with the latest JSON/VRT files retrieved.

Please ask Matti Vähätalo to open the API endpoint for your
IP before using it.
"""

def connect():

    if len(sys.argv) > 1:
        newest = int(sys.argv[1])
    else:
        newest = 64317
        print('\n>>> Usage: $python s24_checknew.py [page_count]')
        print('>>> where [page_count] is the last retrieved page in your JSON dataset.')
        print('>>> Using pre-defined value: %i' %newest)

    print('>>> Please wait...')
    aResp = urllib2.urlopen("http://api.suomi24.fi/threads/newest?count=150&page=100000")
    page = aResp.read();
    page_count = re.sub('.*page_count":(\d+?),".*', r'\1', page)
    print('>>> Your data is %s pages behind.' % str(int(page_count) - int(newest)))

connect()
