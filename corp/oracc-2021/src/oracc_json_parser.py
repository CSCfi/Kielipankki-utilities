import os
import sys
import json
import zipfile
import re
from collections import defaultdict

import xlit_tools

XT = xlit_tools.XLITTools(err_file='../norm/cams-gkab.txt')
LT = xlit_tools.LemmaTools('../norm/oracc-errors.tsv')

p = ['atae-burmarina.zip', 'atae-tilbarsip.zip', 'atae-samal.zip',
     'atae-marqasu.zip','atae-ctn1.zip', 'atae-imgurenlil.zip']
p = ['akklove.zip', 'atae-ctn1.zip']
p = ['atae-huzirina.zip', 'aemw-amarna.zip']
#p = os.listdir('../jsonzip')[0:15]
p = ['saao-saa01.zip']
#p = ['hbtin.zip']
#p = ['epsd2-admin-ur3.zip', 'atae-burmarina.zip']
#p = ['atae-samal.zip']
""" ============================================================
    Oracc JSON to VRT                        asahala 2021-06-14
                                             github.com/asahala

    This script reads downloaded Oracc corpus files and trans-
    forms them into VRT format.

    Code inside parse_projects() is slightly modified from
    Niek Veldhuis' code (see at 2_1_Data_Acquisition_ORACC):
    
    https://github.com/niekveldhuis/compass (as of 2021-07-06)

    VRT is ran through normalizations to fix certain inconsis-
    tencies in Oracc:

        - Unify determinatives to {UPPERCASE}
        - Fix a selection of broken lemma in Oracc
        - Use Helsinki normalizations for DN and GN
        - Normalize /h/
        - Convert accents to indices
        - Simplify POS tagging
        - Simplify genres
        - Simplify and normalize languages

============================================================ """

MASTER_LOG = defaultdict(set)

def parse_projects(projects):

    data = {}
    meta_d = {"label": None, "id_text": None}

    print('> Reading zip files...')
          
    def parse_json(text, meta_d):
        l = []
        for json_obj in text["cdl"]:
            if "cdl" in json_obj: 
                l.extend(parse_json(json_obj, meta_d))
            if "label" in json_obj: 
                meta_d["label"] = json_obj["label"]        
            if json_obj.get("type") == "field-start":
                # sign, pronunciation, translation (sign lists)
                meta_d["field"] = json_obj["subtype"]
            elif json_obj.get("type") == "field-end":
                meta_d.pop("field", None)
                
            if "f" in json_obj:
                lemma = json_obj["f"]
                lemma["id_word"] = json_obj["ref"]
                lemma["label"] = meta_d["label"]
                lemma["id_text"] = meta_d["id_text"]
                if "field" in meta_d:
                    lemma["field"] = meta_d["field"]
                l.append(lemma)
            elif json_obj.get("strict") == "1":
                # horizontal ruling on tablet; or breakage
                lemma = {}
                lemma["extent"] = json_obj["extent"]
                lemma["scope"] = json_obj["scope"]
                lemma["state"] = json_obj["state"]
                lemma["id_word"] = json_obj["ref"]
                lemma["id_text"] = meta_d["id_text"]
                l.append(lemma)
        return l

    for project in projects:
        print(f' dict <-- {project}')
        """ Initialize container for metadata and text content """
        data[project] = {}
        
        file = f'../jsonzip/{project.replace("/", "-")}'
        try:
            z = zipfile.ZipFile(file)
        except:
            print(f"{file} does not exist or is not a proper ZIP file")
            continue
        
        files = z.namelist()        
        files = (name for name in files if "corpusjson"\
                 in name and name[-5:] == '.json')

        """ Read cataloque """
        path = project[0:-4].replace('-', '/')
        data[project]['meta'] = json.loads(
            z.read(f"{path}/catalogue.json").decode('utf-8'))

        lemm_l = defaultdict(list)

        for filename in files:
            text_no = filename[-13:-5]
            id_text = project + text_no
            meta_d["id_text"] = id_text
            try:
                """ read and decode the json file of one particular text
                make it into a json object (essentially a dictionary) and
                send to the parse_json() function """ 
                st = z.read(filename).decode('utf-8')         
                data_json = json.loads(st)
                lemm_l[text_no[1:]] = (parse_json(data_json, meta_d)) 
            except:
                e = sys.exc_info()
                #print(filename, print(e[0]), print(e[1]))
                print(f"{id_text} is not available or not complete")
        z.close()
        data[project]['content'] = lemm_l

    return data

    
class Converter:

    """ This class must be initialized with parse_projects()

    self.data has the following format

       project
          |     
          +---- {meta, content}
          |       |        |
         ...  {metadata} {PNUM: {data}, ...}

    """

    def __init__(self, data):
        self.data = data
        self.tree = []
        self.empty = '_'
        self.korp_norm = self.read_normalizations()
        
        self.number_of_texts = 0
        self.skipped_texts = 0

    def _escape(self, x):
        x = x.replace('&amp;', '&')
        x = x.replace('&', '&amp;')
        x = x.replace('"', '”')
        x = x.replace("'", "’")
        x = x.replace('<', '‹')
        x = x.replace('>', '›')
        x = re.sub(' +', ' ', x)
        return x

    def _reconstruct(self, gdl):
        """ Reconstruct transliteration from GDL. This can be used
        to fix transliteration errors in certain corpora such as
        CAMS/GKAB """

        ## Apparently parsing GDL is too hard and not worth the effort
        ## here http://oracc.museum.upenn.edu/ns/gdl/1.0/
        
        if gdl is None:
            return
        
        xlit = ''
        for x in gdl:
            print(x)
            if x.get('det', False) == 'semantic':
                xlit += '{'
                for s in x['seq']:
                    xlit += s['v'] + s.get('delim', '')
                xlit += '}'
            elif x.get('det', False) == 'phonetic':
                xlit += '{+'
                for s in x['seq']:
                    xlit += s['v'].lower() + s.get('delim', '')
                xlit += '}'
            elif x.get('v', False):
                xlit += x['v'] + x.get('delim', '')
            elif x.get('s', False):
                xlit += x['s'] + x.get('delim', '')

        return xlit
            
    def read_normalizations(self):
        """ Read normalizations from /norm/ and assign them
        to dictionary behind relevant keys """
        path = '../norm/'
        files = {'period': 'korp_period',
                 'language': 'korp_languagesToChange',
                 'genre': 'korp_broadGenres',
                 'pos': 'korp_broadPOS',
                 'long_pos': 'korp_POSexplanations',
                 'word_lang': 'korp_word_lang',
                 'DN': 'godsToChange',
                 'GN': 'korp_placesToChange'}
        replace = {}
        for abbr, filename in files.items():
            #print(filename)
            replace[abbr] = {}
            with open(path + filename, 'r', encoding='utf-8') as f:
                for l in f.read().splitlines():
                    if not l.startswith('#') and l:
                        if abbr in ('DN', 'GN'):
                            target, sources = l.split(' == ')
                            for s in sources.split(','):
                                replace[abbr][s.strip()] = target.strip()
                        else:                            
                            source, target = l.split(' == ')
                            replace[abbr][source] = target.strip()
        return replace
                    
    def _make_text_elem(self, metadata, cdli_number):

        def normalize(metadata, key):
            """ Run normalizations for text metadata """
            x = metadata.get(key, self.empty)
            if key in self.korp_norm:
                normalized = self.korp_norm[key].get(x, x)
                if normalized == x:
                    MASTER_LOG[key].add(x)
                x = normalized
            
            """ Remove illegal symbols from attrs """

            return self._escape(x)
        
        """ Generate VRT text header """
        keys = ('period', 'provenience', 'language', 'genre', 'subgenre')       
        header = [f'cdlinumber="{cdli_number}"'] +\
                 [f'{key}="{normalize(metadata, key)}"' for key in keys] +\
                 ['datefrom=""', 'dateto=""']
        return '<text ' + ' '.join(header) + '>'
                
    def make_vrt(self):

        def normalize(string, key):
            """ Run normalizations for word data """
            if key in self.korp_norm:
                normalized = self.korp_norm[key].get(string, string)
                if normalized == string:
                    MASTER_LOG[key].add(string)
                string = normalized
            return string
        
        print('> Transforming to VRT...')

        for project, data in self.data.items():

            print(' {:<20s} {:<1s}'.format(project, '--> VRT'))

            VRT = []

            """ Project url tail """
            proj_slash = project.replace('.zip', '').replace('-', '/')

            para_num = 1
            for p_number, content in data['content'].items():
                """ New text starts """
                text_metadata = data['meta']['members'].get(p_number, None)
                if text_metadata is None:
                    self.skipped_texts += 1
                    print(f' \----> Warning: {p_number} has no metadata!')
                    text_metadata = {'period':'',
                                     'provenience':'',
                                     'language':'',
                                     'genre':'',
                                     'subgenre':''}
                else:
                    self.number_of_texts += 1
                
                cdli_number = proj_slash + '/' + p_number
                text_header = self._make_text_elem(text_metadata, cdli_number)

                """ Skip if transliteration does not exist """
                if not content:
                    continue

                VRT.append(text_header)
                VRT.append('<paragraph id="%i">' % para_num)
                VRT.append('<sentence id="%i">' % para_num) 
                
                """ Create and normalize VRT word attributes; first
                build a dictionary to group words by their ID to merge
                compound words """
                words = defaultdict(list)
                order = []

                last_wid = ''
                
                for word in content:
                    lang = word.get('lang', self.empty)
                    xlit = word.get('form', self.empty)

                    """ Interrupt if ruling """
                    if xlit == '_':
                        continue
                    
                    lemma = word.get('cf', self.empty)
                    transcr = word.get('norm', self.empty)
                    guide_word = word.get('gw', self.empty)
                    sense = word.get('sense', self.empty)
                    guide_word_pos = word.get('pos', self.empty)
                    sense_pos = word.get('epos', self.empty)
                    word_id = word.get('id_word', self.empty)
                    morph = word.get('morph', self.empty)
                    sum_norm = word.get('norm0', self.empty)
                    auto_lema = lemma
                    url = f'http://oracc.org/{proj_slash}/{word_id}'

                    """ Nomalize transliteration """
                    xlit = XT.normalize_all(xlit, id_='xlit', lang=lang)
                    lemma = LT.fix_lemma(lemma, guide_word_pos)
                    auto_lemma = lemma
        
                    """ Attempt to fix errors in cams-gkab """
                    if project == 'cams-gkab.zip':
                        xlit = XT.fix_gkab(xlit)
                        
                    """ Use normalization for Sumerian """
                    if transcr == '_' and sum_norm != '_':
                        transcr = sum_norm

                    """ Use lemma instead of guide word if not specified """
                    if guide_word == '1':
                        guide_word = lemma
                        sense = lemma

                    """ Apply Helsinki normalizations for GN and DN """
                    if guide_word_pos in ('DN', 'GN'):
                        norm_name = self.korp_norm[
                            guide_word_pos].get(lemma, lemma)
                    else:
                        norm_name = '_'
                        
                    vrt_line = [xlit,
                                lemma,
                                guide_word,
                                sense,
                                transcr,
                                guide_word_pos,
                                guide_word_pos,
                                norm_name,
                                normalize(lang, 'word_lang'),#.replace(' ', ''),
                                morph,
                                auto_lemma,
                                url]

                    """ Make ordered set of word ids """
                    if last_wid != word_id:
                        order.append(word_id)
                        last_wid = word_id
                        
                    words[word_id].append(vrt_line)

                """ Iterate word ids in order and merge compound words;
                normalize combined POS according to Heidi's lists """
                for o in order:
                    if len(words[o]) > 1:
                        # zip all words that share the same id and join them with
                        # ampersand. never allow longer compound words than 3 parts!
                        # some oracc texts do have errors where compound word repeats
                        # several times, e.g. in ATAE hurizina
                        # o = key, [0][0] = xlit
                        items = ['&amp;&amp;'.join(d[0:3]) for d in zip(*words[o])][1:7]
                        vrt_line = [words[o][0][0]] + items + words[o][0][7:]
                    else:
                        vrt_line = words[o][0]
                    
                    vrt_line[5] = normalize(vrt_line[5], 'pos').replace(' ',  '')
                    vrt_line[6] = normalize(vrt_line[6], 'long_pos')

                    """ Make sure all ampersands are html-entities """
                    vrt_line = [self._escape(x) for x in vrt_line]
                    VRT.append('\t'.join(vrt_line))

                VRT.append('</sentence>')
                VRT.append('</paragraph>')
                VRT.append('</text>')
                para_num += 1

            if VRT:
                vrt_filename = project.replace('.zip', '.vrt')
                # rename files to make correct groups
                if vrt_filename == 'contrib-amarna':
                    vrt_filename = 'aemw-contrib'
                with open('../vrt/' + vrt_filename, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(VRT))

        
#parsed_json = Converter(parse_projects(p))
#parsed_json.make_vrt()
#print(parsed_json.number_of_texts, parsed_json.skipped_texts)

def save_logs():
    xlit_tools.save_log('../logs/xlit-lemma-changes.txt')
    print('\n\nList of new values for normalizations')
    for k, vals in MASTER_LOG.items():
        print('===================================')
        for v in vals:
            print(k, v)

#save_logs()


#for key, vals in parsed_json.all_meta.items():
#    for v in vals:
#        print(key, v)
