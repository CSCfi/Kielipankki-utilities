#! /usr/bin/env python
# -*- coding: utf-8 -*-

# asahala/finclarin
# the input file should be .docx document converted into HTML

import sys
import re
import string

class Sinebrychoff:

    def __init__(self):
        default = 'http://kirjearkisto.siff.fi/Home/tabid/37/Default.aspx'
        self.default = default
        self.output = []
        self.data = {}
        self.footnotes = {}
        self.terminator = "margin-bottom: 0in; border-top: none; border-bottom: 0.75pt solid #00000a;"
        self.names = {'PS': ['Paul Sinebrychoff', 'http://kirjearkisto.siff.fi/Sinebrychoff/tabid/55/Default.aspx'],
                      'OS': ['Osvald Sirén', 'http://kirjearkisto.siff.fi/Dealers/OsvaldSir%C3%A9n/tabid/60/Default.aspx'],
                      'AD': ['Axel Durling', 'http://kirjearkisto.siff.fi/Dealers/AxelDurling/tabid/59/Default.aspx'],
                      'AH': ['A. F. Hildén', default],
                      'AL': ['Axel Lundblad', default],
                      'AM': ['A. Matsson', 'http://kirjearkisto.siff.fi/Dealers/AMatsson/tabid/104/Default.aspx'],
                      'AN': ['Arvid Nordqvist', default],
                      'AD': ['Ad. Pantaenius', default],
                      'AT': ['A. Trädgårdsmästar', default],
                      'AW': ['A. Willandt', default],
                      'BK': ['Henryk Bukowski', 'http://kirjearkisto.siff.fi/Dealers/HBukowskisKonsthandel/tabid/66/Default.aspx'],
                      'CA': ['Carl Armfelt', default],
                      'CGH': ['C. G. Hallberg', default],
                      'CGS': ['C. G. Standertskjöld', default],
                      'CH': ['Christian Hammer', 'http://kirjearkisto.siff.fi/Dealers/CristianHammer/tabid/61/Default.aspx'],
                      'CJT': ['C. J. Timgrén', default],
                      'CMS': ['Carl Magnus Stenbock', default],
                      'CoH': ['Conrad Halberg', default],
                      'CUP': ['Carl Ulrik Palm', 'http://kirjearkisto.siff.fi/Dealers/HBukowskisKonsthandel/tabid/66/Default.aspx'],
                      'EL': ['E. Lindevald', default],
                      'FA': ['Fiskars Aktiebolag', default],
                      'FE': ['Finska Elektrokemiska Aktiebolaget', default],
                      'FS': ['Fredr. Sundgrén', default],
                      'GS': ['G. Sahlholm', default],
                      'GU': ['G. Upmark', default],
                      'GW': ['George Williamson', 'http://kirjearkisto.siff.fi/Dealers/GeorgeWilliamson/tabid/106/Default.aspx'],
                      'HE': ['H. Estlander', default],
                      'HH': ['Hugo Helbing', default],
                      'HT': ['H. Timgrén', default],
                      'HW': ['Hjalmar Wicander', 'http://kirjearkisto.siff.fi/Dealers/HjalmarWicander/tabid/64/Default.aspx'],
                      'JC': ['J. Chaigneau &amp; Co', default],
                      'JJ': ['J. Johansson', default],
                      'JK': ['Johan Koskelo', default],
                      'KB': ['Firma Karl Börjesson', default],
                      'KP': ['Den Kongelige Porcelainsfabriks Udsalg', default],
                      'LM': ['Leo Mellin', default],
                      'MH': ['M. Hallberg', default],
                      'NI': ['Nils Idman', default],
                      'OD': ['O. Donner', default],
                      'OK': ['Oscar Kistner', default],
                      'PF': ['Piehl och Fehling', default],
                      'REW': ['R. E. Westerlund', default],
                      'SC': ['S. Carlsund', default],
                      'ScH': ['Schildt Hallberg', default],
                      'SE': ['Sellberg &amp; Co', default],
                      'SK': ['Svenska Kristallglasbrukens Försäljnings Magasin', default],
                      'SL': ['Sigrid Lindqvist', 'http://kirjearkisto.siff.fi/Dealers/HBukowskisKonsthandel/tabid/66/Default.aspx'],
                      'ST': ['Delegationen för Svenska Teaterns Garantförening', default],
                      'TE': ['Taxeringsnämnden I Esbo socken', default],
                      'TO': ['F. v. Tobiesen', default],
                      'UD': ['Uno Donner', default],
                      'WS': ['Schürer von Waldheim', default],
                      'WB': ['W. Brummer', default],
                      'EÖ': ['Emil Österlind', 'http://kirjearkisto.siff.fi/Dealers/Emil%C3%96sterlind/tabid/65/Default.aspx'],
                      'ABV': ['Aktiebolaget Blekholmens Varf', default],
                      'AD': ['Axel Durling', default],
                      'AH': ['A. F. Hildén', default],
                      'AL': ['Alda Lembke', default],
                      'AM': ['A. Matsson', default],
                      'AN': ['Arvid Nordqvists Handels Aktiebolag', default],
                      'AP': ['A. Pantaenius', default],
                      'AW': ['A. WIllandt', default],
                      'BK': ['Bukowskis konsthandel', default],
                      'CA': ['Carl Armfeldt', default],
                      'CB': ['Carl Blomqvst', default],
                      'CGH': ['C. G Hallberg', default],
                      'CMB': ['C. M. Brofeldt', default],
                      'EN': ['E. Nystrand', default],
                      'FB': ['Fina Blomqvist', default],
                      'FH': ['Fanny Hjelm', default],
                      'HB': ['H. Bukowski', default],
                      'OT': ['Otto Donner', default],
                      'SH': ['Sophie Hammer', default],
                      'SS': ['Sigrid Sundborg', default],
                      'TC': ['Torsten Costiander', default],
                      'WB': ['W. Brummer', default]}
        
    def readfile(self, filename):
        self.filename = filename
        with open(filename, encoding='utf-8') as data:
            self.data = data.readlines()

    def get_meta(self):
        date = re.sub('.*(\d\d\d\d\d\d\d\d).*', r'\1', self.filename)
        fn = re.sub(' ', '', self.filename)
        corrs = fn.strip('.html').split('_')
        sender = re.sub('[a-z]', '', corrs[1])
        receiver = re.sub('[a-z]', '', corrs[2])
        self.fileid = re.sub('_su', '', self.filename.strip('.html'))
        
        if sender not in self.names.keys():
            s = sender
            surli = self.default
        else:
            surli = self.names[sender][1]
            s = self.names[sender][0]

        if receiver not in self.names.keys():
            r = receiver
            rurli = self.default
        else:
            rurli = self.names[receiver][1]
            r = self.names[receiver][0]

        if len(date) != 8:
            date = ''
            ymd = '?'
        else:
            ymd = date[0:4] + '.' + date[4:6] + '.' + date[6:]

          
        if sender == 'PS':
            urli = rurli
        else:
            urli = surli
            
        self.id_ = fn.strip('.html')
        self.text_element = ('<text datefrom="{d}" dateto="{d}" senderinits="{sinits}" receiverinits="{rinits}" sender="{sender}" receiver="{receiver}" date="{date}" id="{id_}" url="{u}">'.format(d=date, date=ymd, receiver=r, sender=s, id_=self.fileid, rinits=receiver, sinits=sender, u=urli))

        print(self.text_element)
        
    def stripline(self, line):
        line = line.strip('\n').lstrip()
        line = re.sub('\t', '', line)
        line = re.sub('&nbsp;', ' ', line)
        line = re.sub(' +', ' ', line)
        line = re.sub('&quot;', '"', line)
        return line

    def preprocess(self):
        self.get_meta()
        """ Collect footnotes from the letter """
        get_note = False
        number = '0'
        temp_note = []
        for line in self.data:
            line = self.stripline(line)
            if '<DIV ID="sdfootnote' in line:
                number = re.sub('.*sdfootnote(\d+?).*', r'\1', line)
                get_note = True
            elif '</DIV>' in line and number != '0':
                self.footnotes[number] = ' '.join(temp_note).lstrip()
                get_note = False
                temp_note = []
                
            if get_note:
                temp_note.append(re.sub('<.+?>', '', line))

        #print(self.footnotes)
        
    def process(self):
        self.preprocess()
        letter = []
        content = False
        for line in self.data:
            line = self.stripline(line)
            if 'BODY' in line:
                content = True
            if self.terminator in line:
                content = False
            if content:
                if re.match('.*<SUP>\d+?<\/SUP>.*', line):
                    line = re.sub('<SUP>(\d+?)<\/SUP>',
                                  r' {footnote@\1} ', line)

                if line.startswith(('<P', '<p')):
                    letter.append('<BREAK>')
                line = re.sub('<BR>', ' ', line)
                line = re.sub('<.+?>', '', line)
                letter.append(line)

         #re.sub('¤+', '¤', '¤'.join(letter)).split('¤')
        a = re.sub('(<BREAK> +)+', '<BREAK> ', ' '.join(letter))

        self.make_sents(a)

    def tokenize(self, l):
        tokenized = []
        l = re.sub('\|+?', ' | ', l)
        l = re.sub(' +', ' ', l)
        l = re.sub('- \| ', '', l)
        tokens = l.split(' ')
        for token in tokens:
            if token.startswith(('(', '„', '[', '"', '”')):
                token = token[0] + ' ' + token[1:]
            if token.endswith((')', ']', '"', '!', '?', '.', ',', ':', '”')):
                token = token[0:-1] + ' ' + token[-1]
            tokenized.append(token)
            
        g = '<sentence> ' + re.sub('([a-zäöå][a-zäöå]) (\.|!|\?) ([A-ZÄÖÅ])',
                r'\1 \2 </sentence> <sentence> \3', ' '.join(tokenized)) + ' </sentence>'

        dogenz = []
        
        for item in g.split(' '):
            note = ''
            if 'footnote' in item:
                number = re.sub('.*?(\d+?).*', r'\1', item)
                #print(number, item)
                note = re.sub('\t', '', self.footnotes[number][2:].strip())
            if item.startswith('<'):
                dogenz.append(item)
            else:
                dogenz.append(item + '\t' + note)
                
        return '\n'.join(dogenz)
                         
    def make_sents(self, text):
        paragraphs = text.split('<BREAK>')
        idnumber = 0
        for x in paragraphs:
            if len(x) > 2:
                print('<paragraph id="{g}">\n'.format(g=self.fileid + '-' + str(idnumber)) + self.tokenize(x.strip()) + '\n</paragraph>')
            idnumber += 1

        print('</text>')
            
def main(argv):
    if len(sys.argv) < 2:
        print("Usage: koff2vrt.py [inputfile]\n")
        sys.exit(1)
    else:
        filename = sys.argv[1]

    o = Sinebrychoff()
    o.readfile(filename)
    o.process()

if __name__ == "__main__":
    main(sys.argv[1:])
