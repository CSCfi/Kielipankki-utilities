# -*- coding: utf-8 -*-
import re
from sys import stdout
import time

nick_list = dict()

def restart_line():
    stdout.write('\r')
    stdout.flush()

def split_sents(inp):
    naamarit = r'([\:\;Xx=]-?[D\(\)POSDFEI])'
    left_context = r'(\(|-|<quote>|<quote2>)? ?[\@\dA-ZÄÖÅÃ]'
    #term = '({smiley}|[\.\!\?]+?"?\)?\]?"? ? ?{smiley})'.format(smiley=naamarit)
    term = '(</quote>|</quote2>)? ?({smiley}|[\.\!\?]+ ? ?{smiley}?) ?(</quote>|</quote2>)?'.format(smiley=naamarit)

    if inp.startswith(' '):
        inp = inp[1:]
    if inp[0].islower():
        inp[0].upper() + inp[1:]

    inp = '`SENTENCE`\n%s' % inp

    '''
      Huomioidaan
      + ylim. välilyönnit
      + lyhenteet ja päivämäärät
      + amerikkalaiset desimaalierottimet
      + järjestysluvut
      + tietyt muut lyhenteet, N.N. ja erisnimet (J. Edgar Hoover)
      + hymiöt hyväksytään isoina välimerkkeinä
      + huomioidaan pienellä aloitetut lauseet

    '''
    line = re.sub('<.+?>|<|>', '', inp) #tuhoa HTML-jäänteet
    line = re.sub('@', '', line)
    line = re.sub('"(.+?)"', r' <quote> \1 </quote> ', line)
    line = re.sub("'(.+?)'", r' <quote2> \1 </quote2> ', line)
    line = re.sub(' +', r' ', line)
    line = re.sub('([\(\" ])(aik|alk|ark|as|ed|eKr|ekr|jKr|jkr|eaa|tod|henk|ym|koht|jaa|esim|huom|jne|joht|k|ks|lk|lkm|lyh|läh|miel|milj|mm|mrd|myöh|n|nimim|ns|nyk|oik|os|p|ps|par|per|pj|prof|puh|kok|kes|virh|vas|pvm|rak|s|siht|synt|t|tark|til|tms|toim|v|vas|vast|vrt|yht|yl|ym|yms|yo|ao|em|ko|ml|po|so|ts|vm|etc)\.  ?([a-zäöå\d]|[A-ZÄÖÅ]+)', r'\1\2´ \3', line)
    line = re.sub('(\d+)\. ?([a-z])', r'\1´ \2', line) #jarjestusluvut
    line = re.sub('(\d\d?)\.(\d\d?)\.(\d\d.+)', r'\1´\2´\3', line)
    line = re.sub('(\d(\d\d)?)\.(\d\d\d)', r'\1´\3', line)
    line = re.sub('(\d(\d\d)?) (\d\d\d)', r'\1`VALI`\3', line)
    line = re.sub('(\d+),(\d+)', r'\1`PILKKU`\2', line)
    line = re.sub('(\d+)\. ([a-zäöå])', r'\1´ \2', line)
    line = re.sub('N\.N\.', 'N´N´', line)
    line = re.sub('( [A-ZÄÖÅ])\. ?([A-ZÄÖÅ][a-zöåo]+)', r'\1´ \2', line)
    line = re.sub('( [A-ZÄÖÅ])\. ?(A-ZÄÖÅ])\. ?([A-ZÄÖÅ][a-zöåo]+)', r'\1´\2´ \3', line)
    line = re.sub(r'(%s.+?%s)' % (left_context, term),\
                  r'\1\n</sentence>\n<sentence>\n', line)
    line = re.sub('({term}|\[\.+\]|\: |\;|"|\'|\)|,|\(|\[|\]|@|\?+|\.+|\!+|_+)'.format(term=term), r' \1 ', line)
    line = re.sub(' +', ' ', line)
    line = re.sub(' ', '\n', line)
    line = re.sub('´', '.', line)
    line += '\n</sentence>\n'
    line = re.sub('(<sentence>\n\n</sentence>\n)', '', line) # poista tyhjät lauseet
    line = re.sub('\n\n', '\n', line)
    line = re.sub('`VALI`', ' ', line) # palauta numeroiden erottimet
    line = re.sub('`PILKKU`', ',', line)
    line = re.sub('</?quote>', '"', line)
    line = re.sub('</?quote2>', "'", line)
    line = re.sub('`CHAP`', '<paragraph>\n', line)
    line = re.sub('`SENTENCE`', '<sentence>', line)
    return line

def enumerate_sents(output, out = ''):
    j = 1
    print 'Numeroidaan ...'
    process = range(0, len(output.split('\n')), len(output.split('\n'))/1000)
    out = str()
    for line in output.split('\n'):
        if re.match('^<sent.+', line):
            out += re.sub('<sentence>', '<sentence id="%i">\n' % j, line)
            j += 1
            if j in process:
                stdout.write(str(j))
                restart_line()
        else:
            out += '%s\n' % line
    return out
        
def format_file(file):
    print 'Virkkeistetään ...'
    output = str()
    j = 0
    q = 500
    for line in file:
        line = line.split('\t')
        if j > 0:
            if line[3] not in nick_list.keys():
                if line[3] == "HS.fi":
                    nick_list[line[3]] = 'HS.fi'
                else:
                    nick_list[line[3]] = 'anon_%s' % str(j)
            
            output += '\n<text no="{no}" id="{id}" time="{time}" datefrom="{datefrom}" '\
            'dateto="{dateto}" hiddennick="{hiddennick}" publicnick="{publicnick}" title="{title}">\n<paragraph>\n{comment}</paragraph>\n</text>'.format(
                no=line[0], id=line[1], dateto=line[2][0:10].replace('-', ''),
                datefrom=line[2][0:10].replace('-', ''), time=line[2],\
                hiddennick=line[3], publicnick=nick_list[line[3]], title=re.sub("[\'\"]", "«", line[4]), comment=split_sents(line[5]))
        else: pass
        j += 1
        if j == q:
            stdout.write(str(j))
            restart_line()
            q += 500
    file.close()
    return output

t1 = time.clock()
output = format_file(open('testi2.txt', 'r'))
t2 = time.clock()
f = open('hsfi.vrt', 'w')
f.writelines('<corpus name="HSfi">{out}</corpus>\n'.format(out = enumerate_sents(output)))
f.close()
print(':: time: %.2f ms' % ((t2-t1)*1000))
