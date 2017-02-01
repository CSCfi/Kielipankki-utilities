#!/usr/bin/env python
# -*- coding: utf-8 -*

import requests
import json
import sys
import time
import os

"""
Aller Suomi24 API JSON retriever
asahala / FIN-CLARIN

You need to install requests in order to use this script
http://docs.python-requests.org/

From command line:

   $python collect.py [start] [end]

e.g. $python collect.py 0 100 retrieves the 100 most recent
pages from Suomi24 API, every page containing 150 threads by default.

You may change the amount of threads per page by giving `count` variable
a new value. The maximum value currently allowed by the API is 150.

`save_interval` defines the size of each JSON dump. For example with
value 100 the data is saved as s24_dump_00000-00100.json,
s24_dump_00101-00200.json etc.

Save early, save often. If the API crashes (as it does sometimes) all
unsaved data will be lost!
"""

count = 150
save_interval = 100

def count_time(time_per_page, end, current_page):
    #count estimated time left. retrieving large datasets
    #may take several days
    time_left = float((end-1-current_page) * time_per_page)
    m, s = divmod(time_left, 60)
    h, m = divmod(m, 60)
    os.system('cls' if os.name == 'nt' else 'clear')

    print('>>> estimated processing'\
          ' time: %sh %smin %ssec' % (str(int(h)).zfill(2),
                                      str(int(m)).zfill(2),
                                      str(int(s)).zfill(2)))
    print('>>> retrieving page %i / %i' % (current_page,
                                           end-1))

def dump_data(data, beg, end):
    json.dump(data, open('s24_dump_%s-%s.json'\
                         % (beg.zfill(5),
                            end.zfill(5)), 'w'))

def retrieve(start, end):
    data = []
    save = 0
    save_pos = [i-1 for i in range(start, end,
                                         save_interval)] + [end-1]
    if save_pos[0] < 0:
        save_pos[0] = 0

    for i in range(start, end):
        t1 = time.time()
        url = 'http://api.suomi24.fi/threads/newest?count=%s&page=%s'\
              % (str(count), str(i))
        r = requests.get(url)
        d = r.json()['data']['threads']
        ids = map(lambda x: x['thread_id'], d)

        for id in ids:
            #retrieve data from given id
            url = 'http://api.suomi24.fi/threads/' + id
            r = requests.get(url)
            if 'data' in r.json().keys():
                d = r.json()['data']
                data.append(d)
            else:
                print(r.json()['message'], r.json()['code'])

        count_time(time.time() - t1, end, i)

        if i in save_pos and i-start != 0:
            #save when defined interval is met
            #this is crucial as the API may be quite unstable
            print('>>> dumping JSON. length: %i' % len(data))
            save += 1

            if save > 1:
                add = 1
            else: add = 0

            dump_data(data,
                      str(save_pos[save-1] + add),
                      str(save_pos[save]))
            data = []

retrieve(int(sys.argv[1]), int(sys.argv[2]))
