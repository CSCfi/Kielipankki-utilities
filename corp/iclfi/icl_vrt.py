#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re

dataset = {'keräyspaikka': '',
'keräysvuosi': '',
'medium': '',
'koodi': '',
'syntymävuosi': '',
'sukupuoli': '',
'syntymäpaikka': '',
'asuinpaikka': '',
'äidinkieli': '',
'äidin äidinkieli': '',
'isän äidinkieli': '',
'puhutaanko kotona suomea': '',
'läheiset opettaneet suomea': '',
'opettajan äidinkieli': '',
'asunut/ollut suomessa, vuosi, kesto, paikka': '',
'oppikirja': '',
'taso tuntimäärän mukaan': '',
'taso CEFR:n mukaan (1. arvioija)': '',
'taso CEFR:n mukaan (2. arvioija)': '',
'taso CEFR:n mukaan (3. arvioija)': '',
'taso CEFR:n mukaan (4. arvioija)': '',
'opiskellut muita kieliä': '',
'tekstityyppi': '',
'tehtävänanto': '',
'tentti/kirjoituskoe': '',
'rajattu kirjoittamisaika': '',
'missä kirjoitettu': '',
'käytetty apuvälineitä, mitä': ''}

def filterlevel(string):
    if re.match('.*[ABCDEFGH][12345].*', string):
        level = string[-2:]
    else:
        level = ''
    return level

def findlatest(dataset):
    if dataset['taso CEFR:n mukaan (4. arvioija)']:
        return filterlevel(dataset['taso CEFR:n mukaan (4. arvioija)'])
    if dataset['taso CEFR:n mukaan (3. arvioija)']:
        return filterlevel(dataset['taso CEFR:n mukaan (3. arvioija)'])
    if dataset['taso CEFR:n mukaan (2. arvioija)']:
        return filterlevel(dataset['taso CEFR:n mukaan (2. arvioija)'])
    if dataset['taso CEFR:n mukaan (1. arvioija)']:
        return filterlevel(dataset['taso CEFR:n mukaan (1. arvioija)'])
    else:
        return 'XX'

def normalize(kieli):

    kieli = kieli.lower()
    kieli = re.sub('tsekki|t.ekki', 'tsekki', kieli)
    return kieli

def n(place):
    place = place.lower()
    place = re.sub('t(s|sh|.)ekki', 'tsekki', place)
    return place.title()
    
def process(f,filename):

    s = 0
    sc = 0
    
    sents = ''
    for line in f:
        if line.startswith('<'):
            line = re.sub('CERF', 'CEFR', line)
            data = re.sub('<|>', '', line.strip('\n'))
            for key in dataset.keys():
                if data.startswith(key):
                    dataset[key] = re.sub(key + ': ', '', data.rstrip())
                    
        else:
            if line.startswith('1\t'):
                sents += '<sentence>\n'
                s += 1
            line = re.sub('<\t', '&lt;\t', line)
            attrs = line.strip('\n').split('\t')
            attrs.extend(['', '', '', '', '', ''])
            no = attrs[0]
            wf = attrs[1]
            lemma = attrs[2]
            rel = re.sub('>.*', '', attrs[3])
            head = re.sub('.*>', '', attrs[3])
            msd = attrs[4]
            if not wf.startswith('<'):
                sents += '\t'.join([wf, lemma, no, rel, head, msd]) + '\n'

            if wf.startswith(('<s', '<p')):
                sents += '</sentence>\n'
                sc += 1

    for key in dataset.keys():
        dataset[key] = re.sub('\"|\'', "&quot;", dataset[key])
        dataset[key] = re.sub('\/|\\\\', "/", dataset[key])
        dataset[key] = re.sub(key + ' ?:', '', dataset[key])
        
    text_attrs = 'place="{place}" year="{year}" datefrom="{datefrom}" dateto="{dateto}" medium="{medium}" code="{code}" dob="{dob}" sex="{sex}" pob="{pob}" infloc="{infloc}" inflang="{inflang}" infmotherlang="{infmotherlang}" inffatherlang="{inffatherlang}" finnishathome="{finnishathome}" taugthfinnish="{taugthfinnish}" teacherlang="{teacherlang}" beentofinland="{beentofinland}" book="{book}" cefrlevel="{cerflevel}" levelhour="{levelhour}" levelcefrone="{levelcerfone}" levelcefrtwo="{levelcerftwo}" levelcefrthree="{levelcerfthree}"  levelcefrfour="{levelcerffour}" otherlangs="{otherlangs}" texttype="{texttype}" exercise="{exercise}" examtype="{examtype}" limitedtime="{limitedtime}" wherewritten="{wherewritten}" aids="{aids}" filename="{fname}"'.format(
        place=n(dataset['keräyspaikka']),
        year=dataset['keräysvuosi'],
        datefrom=dataset['keräysvuosi'] + '0101',
        dateto=dataset['keräysvuosi'] + '1231',
        medium=dataset['medium'].lower(),
        code=dataset['koodi'],
        dob=dataset['syntymävuosi'],
        sex=dataset['sukupuoli'].lower(),
        pob=n(dataset['syntymäpaikka'].title()),
        infloc=n(dataset['asuinpaikka'].title()),
        inflang=normalize(dataset['äidinkieli'].lower()),
        infmotherlang=normalize(dataset['äidin äidinkieli'].lower()),
        inffatherlang=normalize(dataset['isän äidinkieli'].lower()),
        finnishathome=dataset['puhutaanko kotona suomea'].lower(),
        taugthfinnish=dataset['läheiset opettaneet suomea'].lower(),
        teacherlang=normalize(dataset['opettajan äidinkieli'].lower()),
        beentofinland=dataset['asunut/ollut suomessa, vuosi, kesto, paikka'].lower(),
        book=dataset['oppikirja'].capitalize(),
        levelhour=dataset['taso tuntimäärän mukaan'],
        levelcerfone=filterlevel(dataset['taso CEFR:n mukaan (1. arvioija)']),
        levelcerftwo=filterlevel(dataset['taso CEFR:n mukaan (2. arvioija)']),
        levelcerfthree=filterlevel(dataset['taso CEFR:n mukaan (3. arvioija)']),
        levelcerffour=filterlevel(dataset['taso CEFR:n mukaan (4. arvioija)']),
        cerflevel=findlatest(dataset),
        otherlangs=dataset['opiskellut muita kieliä'],
        texttype=dataset['tekstityyppi'].lower(),
        exercise=dataset['tehtävänanto'].lower(),
        examtype=dataset['tentti/kirjoituskoe'].lower(),
        limitedtime=dataset['rajattu kirjoittamisaika'],
        wherewritten=dataset['missä kirjoitettu'],
        aids=dataset['käytetty apuvälineitä, mitä'].lower(),
        fname=filename)

    output = '<text %s>\n<paragraph>\n%s\n</paragraph>\n</text>\n' % (re.sub(' +|\t', ' ', text_attrs), sents)

    levels = []

    if s - sc != 0:
        err = 'ERROR_'
    else:
        err = ''
        
    if dataset['taso CEFR:n mukaan (4. arvioija)']:
        levels.append(err+filterlevel(dataset['taso CEFR:n mukaan (4. arvioija)']))
    if dataset['taso CEFR:n mukaan (3. arvioija)']:
        levels.append(err+filterlevel(dataset['taso CEFR:n mukaan (3. arvioija)']))
    if dataset['taso CEFR:n mukaan (2. arvioija)']:
        levels.append(err+filterlevel(dataset['taso CEFR:n mukaan (2. arvioija)']))
    if dataset['taso CEFR:n mukaan (1. arvioija)']:
        levels.append(err+filterlevel(dataset['taso CEFR:n mukaan (1. arvioija)']))
    else:
        levels.append(err+'XX')
    
    _levels = [x for x in levels if x]

    #return output
    return [output, _levels[0]]
    #return [re.sub('<sentence>\n\n\n*', '', output), _levels[0]]

#    file = open(directory+'/'+xml_file.split("/")[-1][:-4]+'.vrt', 'w', encoding='utf8')
            
def main(filename, directory):
    file = open(filename, mode="r")
    output, level = process(file, filename)
    out = open(directory+'/'+level+'_'+filename + '.vrt', mode="w")
    out.writelines(output)
    out.close()
    file.close()
    
main(sys.argv[1], sys.argv[2])
