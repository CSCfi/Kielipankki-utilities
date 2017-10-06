#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys


"""
 asahala/finclarin

 pyytton skripti.py < infile.html > outfile.vrt

 the input file should be .docx converted into .html

"""

ignore = r'\/|P|HTML|META|STYLE|BODY|FONT|TITLE|SPAN|A|!'

regions = {'Moray': 'North', 'Invernessshire': 'North', 'Sutherland': 'North', 'Ross': 'North',
           'Aberdeenshire': 'North-East', 'Angus': 'North-East', 'Perthshire': 'Central', 'Lanarkshire': 'Central',
           'Fife': 'South-East', 'East Lothian': 'South-East', 'Lothian': 'South-East',
           'Stirlingshire': 'South-East', 'Border': 'South-East',
           'Argyllshire': 'South-West', 'Ayrshire': 'South-West', 'South-West': 'South-West',
           'unspecified': 'Unlocalised', 'unlocalised': 'Unlocalised', 
           'Court': 'Court', 'Professional': 'Professional',
           'Borders': 'South-East', 'Home': 'Home'}

def fix(line):
    line = line.replace('(sor', 'sor')
    line = line.replace('(which', '( which')
    line = line.replace('(thankes', '( thankes')
    line = line.replace('!xiij', 'xiij')
    line = line.replace(',?', ',{&lt;?}')
    line = line.replace(',whither', ', whither')
    line = line.replace(':Glascuen', ': Glascuen')
    line = line.replace(' ;? ', ' ;{&lt;?} ')
    line = line.replace(';france', 'france')
    line = line.replace('affect:', 'affect :')
    line = line.replace('also,', 'also ,')
    line = line.replace('Ap:', 'Ap :')
    line = line.replace('you,', 'you ,')
    line = line.replace('},', '} ,')
    line = line.replace('};', '} ;')
    line = line.replace('{space}', ' {space} ')
    line = line.replace('&gt;)', '&gt;}')
    line = line.replace('space vertically ', 'space vertically} ')
    line = line.replace('}{', '} {')
    line = line.replace('{grace}', '{=grace}')
    line = re.sub('\{([-\.\?])\}', r'\1', line)
    line = line.replace('{\\}', '\\')
    line = line.replace('{b}', '(b) {&lt;possibly added later}')
    line = line.replace('{hime}', '{ins}')
    line = line.replace('{trouble', '{=trouble')
    line = line.replace('{correcting another', '{&lt;correcting another')
    line = re.sub('{&lt;([a-zA-Z])&gt;', r'{&lt;&lt;\1&gt;', line)
    line = re.sub('‘(.)’', r'&lt;\1&gt;', line)
    line = line.replace('{y correcting e}', '{&lt;&lt;y&gt; correcting &lt;e&gt;}')
    line = line.replace('{u correcting y}', '{&lt;&lt;u&gt; correcting &lt;y&gt;}')
    line = line.replace('{i probably correcting j}', '{&lt;&lt;i&gt; probably correcting &lt;j&gt;}')
    line = line.replace('{a correcting i}', '{&lt;&lt;a&gt; correcting &lt;i&gt;}')
    line = line.replace('{z replacing', '{&lt;&lt;z&gt; replacing')
    line = line.replace('{v correcting o?}', '{&lt;&lt;v&gt; possibly correcting &lt;o&gt;}')
    line = line.replace('{the second', '{&lt;the second')
    line = line.replace('{e correcting is}', '{&lt;&lt;e&gt; correcting &lt;is&gt;}')
    line = line.replace('{first', '{&lt;the first')
    line = line.replace('{O correcting', '{&lt;&lt;O&gt; correcting')
    line = line.replace('{l correcting r}', '{&lt;&lt;l&gt; corecting &lt;r&gt;}')
    line = line.replace('{o correcting d}', '{&lt;&lt;o&gt; correcting &lt;d&gt;}')
    line = re.sub('\{&lt; ', '\{&lt;', line)
    line = re.sub(' &gt\}; ', '&gt;\}', line)
    line = line.replace("(end}", "{end}")
    line = line.replace("[&lt;reduced}", "{&lt;reduced}")
    line = line.replace("[ins}", "{ins}")
    line = line.replace("[space}", "{space}")
    line = line.replace('except ofr', 'except for')
    line = line.replace('exept for', 'except for')
    line = line.replace('corecting', 'correcting')
    line = line.replace('damamged', 'damaged')
    line = line.replace('wirds danaged', 'words damaged')
    line = line.replace('preceiding', 'preceding')
    line = line.replace('superfluos', 'superfluous')
    line = line.replace('verticlaly', 'vertically')
    line = line.replace("{=AGAIN}", "{=again}")
    line = line.replace("{=AGO}", "{=ago}")
    line = line.replace("{=AN}", "{=an}")
    line = line.replace("{=BECAUSE}", "{=because}")
    line = line.replace("{=BEFORE}", "{=before}")
    line = line.replace("{=BYGONES}", "{=bygones}")
    line = line.replace("{=CAN NOT}", "{=can not}")
    line = line.replace("{=HAVE}", "{=have}")
    line = line.replace("{=INCREDULOUS}", "{=increndulous}")
    line = line.replace("{=MAY}", "{=may}")
    line = line.replace("{=NOTE}", "{=note}")
    line = line.replace("{=THE}", "{=the}")
    line = line.replace("{=UN-}", "{=un-}")
    line = line.replace("{=UNANSWERED}", "{=unanswered}")
    line = line.replace("{address&gt;}", "{address&gt;} ")
    line = line.replace("{centred&gt;}", "{centred&gt;} ")
    line = line.replace("{f2}", " {f2} ")
    line = line.replace("{adjacent&lt;}", "{&lt;adjacent}")
    line = line.replace("{&gt;adjacent}", "{adjacent&gt;}")
    line = line.replace("{&lt;a?s?&gt; cancelled}", "{&lt;a?s?&gt; cancelled}")
    line = line.replace("{hand 1&gt; ", "{hand 1&gt;} ")
    line = line.replace("{del\ an", "{del} an")
    line = line.replace("{ins]", "{ins}")
    line = line.replace("{hand 1&gt;}}", "{hand 1&gt;}")
    line = line.replace("tyme }", "tyme )")
    return line

    
def read_file(text):
    f = sys.stdin.readlines()
    for line in f:
        if not line.endswith('</P>\n') and line != '\n':
            text += re.sub('\n', ' ', line)
        else:
            if line != '\n':
                text += line

    # Make formatted HTML compatible with the old script
    text = re.sub('<({tags}).+?>'.format(tags=ignore), '', text).strip()
    text = re.sub('<BR>', '&nbsp;', text)
    #print(text)
    #text = re.sub('  \n', ' ', text.strip())
    return ['<p class=MsoNormal>' + fix(y) + '</p>' for y in text.split('\n')]#re.sub('<.+?>', '', text).split('\n')

def clear(string):
    string = re.sub('({.*?}|=\\\|”|\*.+?\%|\?|\=|~|“|_)', '', string)
    string = re.sub('([A-Za-z])\\\([A-Za-z])', r'\1\2', string)
    
    return string

def clear_attr(string):
    string = re.sub('_', ' ', string)
    string = re.sub('[{}]', '', string)
    string = re.sub('&.*;', '', string)
    return string

def parse_letter(letter):
    formatted = ''
    final = []
    temp = []
    conv_space = False
    # Muunna tagien vÃ€lit alaviivoiksi
    for char in letter:
        if char == '{':
            conv_space = True
        if char == '}':
            conv_space = False
        if conv_space and char == ' ':
            formatted += '_'
        else:
            formatted += char
    split_letter = formatted.split(' ')
    
    return split_letter

def parse_people(people, type_):
    from_ = re.sub('.*by (.+?) to.+', r'\1', people)
    to = re.sub('.*to (.+?)', r'\1', people)

    if type_ == 'from':
        return from_.rstrip(',')
    else:
        return to

def parse_date(date_):
    date = date_.split(' ')
    if len(date) == 2:
        date[0] = date[0][0:4]
        if date[1] == '%CO':
            date[1] = 'January'
        if date[1] == '30':
            date[1] == 'January'
        date[1] = date[1].replace('-', '/')
        date[1] = date[1].split('/')[0]
        date.append('01')
    else:
        pass
    
    if len(date) == 3:
        months = {'January':'01',
                  'February':'02',
                  'March':'03',
                  'April':'04',
                  'Aprill': '04',
                  'May':'05',
                  'June':'06',
                  'July':'07',
                  'August':'08',
                  'September':'09',
                  'October':'10',
                  'November':'11',
                  'December':'12',
                  'unspecified':'01'}
        year = date[0][0:4]
        month = months[date[1]]
        if '-' in date[2]:
            date[2] = date[2].split('-')[0]
        if '/' in date[2]:
            date[2] = date[2].split('/')[0]
        
        if len(date[2]) == 1:
            day = '0' + date[2]
        else:
            day = date[2]

        q = year + month + day
            
        return q
    else:
        if date_ == 'unspecified':
            date_ = ''
        else:
            date_ = date_[0:4] + '0101'
            
        return date_

def rank_gender(meta, type_):

    info = '_U'
    
    if type_ == 'addressee':
        keys = ['AF', 'AM', 'AR']
    else:
        keys = ['IF', 'IM', 'IR']

    for k in keys:
        if meta[k] != 'unspecified':
            info = k

    types = {'M': 'male', 'F': 'female', 'R': 'royal', 'U': 'unspecified'}

    return types[info[1]]
    

def printfile(x):
   
    '''
    meta keys
    id = letter id
    inf = informant
    MS = catalogue number in RNS/NLS
    ST =
    DA = detailed date
    CO = writer and addressee
    BI = information about previous editions
    IF = informant's gender/rank
    AR = addressee's gender/rank
    HD1 = type
    HD2 = type 2
    LC = region of writer, place where letter was written
    FN = filename
    WC = word count
    '''
    meta = {'id':'',
            'inf':'',
            'MS':'unspecified',
            'ST':'unspecified',
            'DA':'unspecified',
            'CO':'unspecified',
            'BI':'unspecified',
            'IF':'unspecified',
            'IM':'unspecified',
            'IR':'unspecified',
            'AF':'unspecified',
            'AM':'unspecified',
            'AR':'unspecified',
            'HD1':'unspecified',
            'HD2':'unspecified',
            'LC':'unspecified',
            'FN':'unspecified',
            'WC':'unspecified',
            'fraser': 'unspecified'}
    letter = ''

    for l in x:
        line = re.sub('</?[pP].*?>', '', l.lstrip())
        line = line.strip()
        if line.startswith('%'):
            key = re.sub('%(.+?):.*', r'\1', line)
            value = line.split(':')[1]
            meta[key] = value.strip()
        elif line.startswith('='):
            meta['inf'] = line.strip('=')
        elif line.startswith('#'):
            meta['id'] = line.strip('# ')
        elif line.startswith('{Fraser'):
            meta['fraser'] = line.strip('{}')
        elif line.startswith('+'):
            pass
        elif len(line) < 70:
            pass
        else:
            letter = line
            
    final = parse_letter(letter)
    """
    if meta['HD1'] == 'unspecified' and meta['HD2'] != 'unspecified':
        meta['HD1'] = meta['HD2']
    """
    
    if ',' in meta['HD1']:
        scripttype = meta['HD1'].split(',')[1].strip()
        lettertype = meta['HD1'].split(',')[0].strip()
    else:
        scripttype = 'information unavailable'
        lettertype = 'information unavailable'
 
    if ',' in meta['HD2']:
        scripttypetwo = meta['HD2'].split(',')[1].strip()
        lettertypetwo = meta['HD2'].split(',')[0].strip()
    else:
        scripttypetwo = 'information unavailable'
        lettertypetwo = 'information unavailable'

    print('<text date="{datetitle}" datefrom="{date}" dateto="{date}" from="{from_}" to="{to}" largeregion="{large}" year="{year}" fraser="{fraser}" lettertype="{lettertype}" scripttype="{scripttype}" lettertypetwo="{lettertypetwo}" scripttypetwo="{scripttypetwo}" id="{id_}" bi="{bi}" ms="{ms}" fn="{fn}" srg="{srg}" arg="{arg}" lcinf="{lci}" lclet="{lcl}" wc="{wc}" st="{st}">'.format(year=re.sub('.*(\d\d\d\d).*', r'\1', meta['DA']),
                  id_=meta['id'],
                  bi=meta['BI'],
                  ms=meta['MS'],
                  fn=meta['FN'],
                  large=regions[meta['LC'].split(',')[0].strip()],
                  arg=rank_gender(meta, 'addressee'),
                  srg=rank_gender(meta, 'sender'),
                  lci=meta['LC'].split(',')[0].strip(),
                  lcl=meta['LC'].split(',')[1].strip(),
                  wc=meta['WC'],
                  scripttype=scripttype,
                  lettertype=lettertype,
                  scripttypetwo=scripttypetwo,
                  lettertypetwo=lettertypetwo,
                  st=meta['ST'],
                  date=parse_date(meta['DA']),                                                                                                                                                                                                                                                                                                                                                   datetitle = meta['DA'],
                  from_=parse_people(meta['CO'], 'from'),
                  to=parse_people(meta['CO'], 'to'),
                  fraser=meta['fraser']
                  ))
    print('<paragraph>')
    print('<sentence>')
    state = ''
    for x in final:
        if re.match('{.+}', x):
            x = re.sub('_', ' ', x)
        print(x)


    print('</sentence>\n</paragraph>\n</text>')
        
printfile(read_file(''))
