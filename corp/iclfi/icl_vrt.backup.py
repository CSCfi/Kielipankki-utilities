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
    if string:
        level = re.sub('taso CEFR:n mukaan (\d. arvioija): ', '', string)
    else:
        level = ''
    return level

def process(f,filename):
    sents = ''
    for line in f:
        if line.startswith('<'):
            data = re.sub('<|>', '', line.strip('\n'))
            for key in dataset.keys():
                if data.startswith(key):
                    dataset[key] = re.sub(key + ': ', '', data.rstrip())

        else:
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
            else:
                sents += '</sentence>\n<sentence>\n'

    for key in dataset.keys():
        dataset[key] = re.sub('\"|\'|\/|\\\\', "'", dataset[key])


    text_attrs = 'place="{place}" year="{year}" datefrom="{datefrom}" dateto="{dateto}" medium="{medium}" code="{code}" dob="{dob}" sex="{sex}" pob="{pob}" infloc="{infloc}" inflang="{inflang}" infmotherlang="{infmotherlang}" inffatherlang="{inffatherlang}" finnishathome="{finnishathome}" taugthfinnish="{taugthfinnish}" teacherlang="{teacherlang}" beentofinland="{beentofinland}" book="{book}" levelhour="{levelhour}" levelcerfone="{levelcerfone}" levelcerftwo="{levelcerftwo}" levelcerfthree="{levelcerfthree}"  levelcerffour="{levelcerffour}" otherlangs="{otherlangs}" texttype="{texttype}" exercise="{exercise}" examtype="{examtype}" limitedtime="{limitedtime}" wherewritten="{wherewritten}" aids="{aids}" filename="{fname}"'.format(
        place=dataset['keräyspaikka'],
        year=dataset['keräysvuosi'],
        datefrom=dataset['keräysvuosi'] + '0101',
        dateto=dataset['keräysvuosi'] + '1231',
        medium=dataset['medium'],
        code=dataset['koodi'],
        dob=dataset['syntymävuosi'],
        sex=dataset['sukupuoli'],
        pob=dataset['syntymäpaikka'],
        infloc=dataset['asuinpaikka'],
        inflang=dataset['äidinkieli'],
        infmotherlang=dataset['äidin äidinkieli'],
        inffatherlang=dataset['isän äidinkieli'],
        finnishathome=dataset['puhutaanko kotona suomea'],
        taugthfinnish=dataset['läheiset opettaneet suomea'],
        teacherlang=dataset['opettajan äidinkieli'],
        beentofinland=dataset['asunut/ollut suomessa, vuosi, kesto, paikka'],
        book=dataset['oppikirja'],
        levelhour=dataset['taso tuntimäärän mukaan'],
        levelcerfone=filterlevel(dataset['taso CEFR:n mukaan (1. arvioija)']),
        levelcerftwo=filterlevel(dataset['taso CEFR:n mukaan (2. arvioija)']),
        levelcerfthree=filterlevel(dataset['taso CEFR:n mukaan (3. arvioija)']),
        levelcerffour=filterlevel(dataset['taso CEFR:n mukaan (4. arvioija)']),
        otherlangs=dataset['opiskellut muita kieliä'],
        texttype=dataset['tekstityyppi'],
        exercise=dataset['tehtävänanto'],
        examtype=dataset['tentti/kirjoituskoe'],
        limitedtime=dataset['rajattu kirjoittamisaika'],
        wherewritten=dataset['missä kirjoitettu'],
        aids=dataset['käytetty apuvälineitä, mitä'],
        fname=filename)

    output = '<text %s>\n<paragraph>\n<sentence>\n%s\n</paragraph>\n</text>\n' % (re.sub(' +|\t', ' ', text_attrs), sents)

    if dataset['taso CEFR:n mukaan (4. arvioija)']:
        level = dataset['taso CEFR:n mukaan (4. arvioija)']
    elif dataset['taso CEFR:n mukaan (3. arvioija)']:
        level = dataset['taso CEFR:n mukaan (3. arvioija)']
    elif dataset['taso CEFR:n mukaan (2. arvioija)']:
        level = dataset['taso CEFR:n mukaan (2. arvioija)']
    elif dataset['taso CEFR:n mukaan (2. arvioija)']:
        level = dataset['taso CEFR:n mukaan (2. arvioija)']
    else:
        pass
            
    #return output
    return [re.sub('<sentence>\n\n', '', output), level]

#    file = open(directory+'/'+xml_file.split("/")[-1][:-4]+'.vrt', 'w', encoding='utf8')
            
def main(filename, directory):
    file = open(filename, mode="r")
    output, level = process(file, filename)
    out = open(directory+'/'+level+'_'+filename + '.vrt', mode="w")
    out.writelines(output)
    out.close()
    file.close()
    
main(sys.argv[1], sys.argv[2])
