#! /usr/bin/env python
# -*- coding: utf-8 -*-

''' 
asahala/FIN-CLARIN

Suomi24 API JSON -> VRT Converter
Usage: $python3 s24conv.py [input.json]

You must have cid_database.txt in the same dictionary with this script.
If you don't have one, either skip self.feed_cid_db() at first run by
commenting it out or create a blank file containing character 0 in the first
line.

The latest comment_id database can be downloaded from IDA /Suomi24/
'''

import vrt_tools
import json
import sys
import datetime
import re
import os

class JSON_to_VRT_converter:

    def __init__(self):
        """ 
        ´progress_message´ contains all runtime information printed by this script
        ´output´ container for the parsed JSON
        ´VRT´ container for the formatted VRT
        ´data´ container for JSON dictionary
        ´cid_db´ container for comment id database
        ´dupes´ duplicate counter
        """
        self.progress_message = '=============================================='
        self.output = {}
        self.VRT = []
        self.data = {}        
        self.cid_db = {str(i):[] for i in range(0, 1000)}
        self.dupes = 0
        self.cid_db_filename = "s24_all_cids.txt" #"comment_id_db.list"
        self.feed_cid_db() #comment this out if you don't have cid_database.txt


    def feed_cid_db(self):
        """ Read file containing all comment ids from previous JSON dumps.
        These are used to remove duplicates caused by API page permutations"""
        self.progress_message += '\n>>> reading comment id database'
        self.progress()
        f = open(self.cid_db_filename, 'r')
        for line in f:
            l = line.strip('\n')
            if l:
                self.cid_db[l[0:3]].append(l)
        f.close()
               
    def progress(self):
        """ Print progress messages"""
        os.system('cls' if os.name == 'nt' else 'clear')
        sys.stdout.write(self.progress_message)

    def readjson(self, filename):
        """ Read JSON """
        self.progress_message += '\n>>> reading %s' % filename
        self.progress()
        with open(filename, encoding='utf-8') as data_file:
            self.data = json.loads(data_file.read())

    def format_time(self, value):
        """ Format two different time stamps used by S24 API into
        DD.MM.YYYY HH:MM:SS"""
        if isinstance(value, int):
            value /= 1000
            time = datetime.datetime.fromtimestamp(
                int(value)).strftime('%d.%m.%Y %H:%M')
        else:
            time = re.sub('(\d+?)-(\d+?)-(\d+?)T(.+?)Z',
                          r'\3.\2.\1 \4', value)
        return time.split(' ')

    def nested(self, data, thread_id, title, titles, pdata, comment_data = {}):
        """ Add nested entries from JSON (e.g. thread comments).
        Count and ignore duplicates """

        cid = str(self.check_key(data, 'comment_id'))
        #print(cid)
        if cid != '':
            if cid not in self.cid_db[cid[0:3]]:
                self.cid_db[cid[0:3]].append(cid)
                skip = False
            else:
                self.dupes += 1
                skip = True
        else:
            skip = True
            self.progress_message += '\n>>>> %s' % ':'.join(data.keys())
            self.progress_message += '\n>>> WARNING: nested comment skipped, no comment id at thread %s''' % thread_id
            self.progress()
        
        if not skip:
            date, time = self.format_time(data['created_at'])
            datef = date.split('.')[2] + date.split('.')[1] + date.split('.')[0]
            comment_data = {'titles': titles,
                        'title': title,
                        'datefrom' : datef,
                        'dateto': datef,
                        'year': datef[0:4],
                        'tid': thread_id,
                        'anonnick': self.check_key(data, 'anonnick'),
                        'views': pdata['views'],
                        'comms': str(len(pdata['comments'])),
                        'date': date,
                        'time': time,
                        'body': self.check_key(data, 'body'),
                        'deleted' : self.check_key(data, 'deleted'),
                        'cid': cid,
                        'views': self.check_key(data, 'views'),
                        'closed': self.check_key(data, 'closed')}

            self.output[thread_id]['comments'][data['comment_id']] = comment_data

    def check_key(self, page, key):
        """ Check for possible key errors (some exist in the JSON) """

        if key in page.keys():
            return page[key]
        else:
            if key in ['anonnick', 'body', 'cid']:
                self.progress_message += '\n>>> WARNING: key not found: %s''' % key
                self.progress()
            return ''
            
    def parse(self):

        i = 1
        print_range = [j for j in range(0, len(self.data), 500)]
        self.progress_message += '\n>>> parsing...'
        self.progress()

        """ Parse each page from JSON containin n threads """
        for page in self.data:
            if i in print_range:
                self.progress()
                print(' %i / %i' % (i, len(self.data)))
            titles = []
            date, time = self.format_time(page['created_at'])
            datef = date.split('.')[2] + date.split('.')[1] + date.split('.')[0]

            for title in page['topics']:
                titles.append(title['title'])

            title = self.check_key(page, 'title')
          
            # dupe code, could be merged with the ´nested´ function.
            self.output[page['thread_id']] = {'titles': titles,
                                              'title': title,
                                              'datefrom': datef,
                                              'dateto': datef,
                                              'year': datef[0:4],
                                              'comms' : str(len(page['comments'])),
                                              'tid': page['thread_id'],
                                              'anonnick': self.check_key(page, 'anonnick'),
                                              'date': date,
                                              'time': time,
                                              'deleted' : self.check_key(page, 'deleted'),
                                              'body': self.check_key(page, 'body'),
                                              'cid': 'unspecified',
                                              'views': self.check_key(page, 'views'),
                                              'closed': self.check_key(page, 'closed'),
                                              'comments': {}}

            #temporary code, but max recursion is fulfilled
            """ Parse nested JSON data """
            if 'comments' in page.keys():
                for sub_page in page['comments']:
                    self.nested(sub_page, page['thread_id'], title, titles, page)
                    if 'comments' in sub_page.keys():
                        for ssub_page in sub_page['comments']:
                            self.nested(ssub_page, page['thread_id'], title, titles, page)
                            if 'comments' in ssub_page.keys():
                                for sssub_page in ssub_page['comments']:
                                    self.nested(sssub_page, page['thread_id'], title, titles, page)
                                    if 'comments' in sssub_page.keys():
                                        for ssssub_page in sssub_page['comments']:
                                            self.nested(ssssub_page, page['thread_id'], title, titles, page)


            i += 1

        self.progress_message += '\n>>> %i duplicates removed.' % self.dupes
        self.progress()
        
    def formvrt(self, data, thread_id):
        """ Format data into VRT """

        def kill_chars(string):
            """Format titles and nicknames so that they won't break the VRT
            i.e. remove or replace reserved symbols.
            This could (or should) be done with html.encode()"""
            string = string.strip('\n').strip()
            string = re.sub('\\\\', '&#92;', string)
            string = re.sub('\/', '&#47;', string)
            string = re.sub('\!', '&#33;', string)
            string = re.sub('\+', '&#43;', string)
            string = re.sub('<', '&lt;', string)
            string = re.sub('>', '&gt;', string)
            string = re.sub('"', '&quot;', string)
            return string

        data['title'] = kill_chars(data['title'])
        data['anonnick'] = kill_chars(data['anonnick'])

        """Generate section titles (number of subsections vary)"""
        sects = [' sect', 'subsect', 'ssubsect', 'sssubsect',
                 'ssssubsect', 'sssssubsect', 'ssssssubsect']
        names = ['', '', '', '', '', '', '']
        section_attrs = []
        grouped_sects = []
        main_sect = ''

        """Assign found subsection titles names into array of fixed length """
        i = 0
        while i < len(data['titles']):
            names[i] = data['titles'][i]
            i += 1
        
        i = 0
        for m in zip(sects, names):
            section_attrs.append('="'.join(m) + '"')
            if m[1]:
                if i == 0:
                    main_sect = m[1]
                else:
                    grouped_sects.append(m[1])
            i += 1

        """Form subsect > sub_subsect > sub_sub_subsect"""
        grouped_sects = ' &gt; '.join(grouped_sects)
        
        """Generate urls (thread and comment)"""
        baseurl = 'http://keskustelu.suomi24.fi/t/'
        if data['cid'] == 'unspecified':
            curl = ''
        else:
            curl = '#comment-' + str(data['cid'])

        """Generate text element"""
        text = '<text discussionarea="{da}" subsections="{ss}"'.format(da=main_sect,
                                                                       ss=grouped_sects)
        for key in data.keys():
            if key in ['datefrom', 'dateto', 'anonnick', 
                       'date', 'time', 'year', 'cid', 'tid', 'title',
                       'views', 'comms', 'deleted']:
                text += ' %s="%s"' % (key, data[key])
        text += '%s urlboard="%s" urlmsg="%s">' % (' '.join(section_attrs),
                                                   baseurl + str(data['tid']),
                                                   baseurl + str(data['tid']) + curl)
        self.VRT.append(text)

        """Tokenize and split into sentences (uses my vrt_tools module).
        Also split exceedingly long strings into 256 chars (VRT max str lenght is 4096)"""
        paragraphs = re.sub('<p>', '', data['body']).split('</p>')

        for p in paragraphs:
            if p:
                self.VRT.extend(['<paragraph>', vrt_tools.tokenize(p, 256), '</paragraph>'])
          
        self.VRT.append('</text>')
        #print('\n'.join(self.VRT))

    def save_database(self):
        """ Update comment ID database """
        print('\n>>> saving comment id database')
        f = open(self.cid_db_filename, 'w')
        keys = []
        for key in self.cid_db.keys():
            keys.extend(self.cid_db[key])
        f.writelines('\n'.join(keys))
        f.close()

    def iterate_data(self):
        """ Feed parsed JSON into VRT-formatter """
        i = 0
        printrange = [j for j in range(0, len(self.output), 500)]
        print(len(self.output), 'out')
        self.progress_message += '\n>>> tokenizing and converting into VRT...'''
        self.progress()
        for thread_id in self.output.keys():
            if i in printrange:
                self.progress()
                print(' %i / %i' % (i, len(self.output))) 
            self.formvrt(self.output[thread_id], thread_id)
            for comment_id in self.output[thread_id]['comments']:
                self.formvrt(self.output[thread_id]['comments'][comment_id], thread_id)                            
            i += 1
        
        return self.VRT, self.progress_message

    def write(self, fname, mode, data, printprogress):
        if printprogress:
            self.progress_message += '\n>>> writing VRT...'
            self.progress()       
        f = open(fname, mode)
        f.writelines(data)
        f.close()
        self.progress_message += '\n>>> written %s' % fname
        self.progress()

def main(argv):
    if len(argv) < 1:
        print(">>> Usage: jsonvrt.py [inputfile]\n")
        sys.exit(1)
    else:
        filename = sys.argv[1]

    j = JSON_to_VRT_converter()
    j.readjson(filename)
    j.parse()
    j.save_database()

    vrt, messages = j.iterate_data()
    j.write('vrt/'+filename.split('.')[0] + '.vrt', 'w', '\n'.join(vrt), True)
    j.write('error2.log', 'a', messages, False)
    j.save_database()

    print('\n')

if __name__ == "__main__":
    main(sys.argv[1:])
