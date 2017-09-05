"""
corpusname = input('corpusname:')
langpair = input('language pair (enfi, fiar): ')
dirname = corpusname.lower()
year = input('year: ')
"""

""" =======================================

This script makes a batch file for converting Opus MOSES format
into VRT and add it into Korp.

User must first download the corresponding corpora (eg. with wget)

======================================= """

# lpair = language pair
# printjs = print javascript for config.js
# printbatch = print batch template for coprus conversion

lpair = 'dafi'
makefolder = True
printjs = True
printbatch = True

# List of available corpora for the language pair
# 1 = true, 0 = false

lista = """
0,OpenSubtitles2011,2011
0,OpenSubtitles2012,2012
0,OpenSubtitles2013,2013
0,OpenSubtitles2015,2015
1,OpenSubtitles,2014
0,DGT,2014
0,EUbookshop,2014
0,EMEA,2009
0,ECB,2009
0,KDE4,2009
1,GNOME,2014
1,EUconst,2009
0,PHP,2014
1,Ubuntu,2014
1,Tatoeba,2014
0,Books,2014,
1,Europarl,2014
1,JRC-Acquis,2014"""

def gen(corpusname, langpair, dirname, year):

    lang1 = langpair[0:2]
    lang2 = langpair[2:]

    infilename1 = corpusname + '.' + lang1 + '-' + lang2 + '.' + lang1
    infilename2 = corpusname + '.' + lang1 + '-' + lang2 + '.' + lang2

    dirname1 = 'opus_' + dirname + '_' + langpair + '_' + lang1
    dirname2 = 'opus_' + dirname + '_' + langpair + '_' + lang2

    dirname1 = dirname1.lower().replace('-', '_')
    dirname2 = dirname2.lower().replace('-', '_')

    corpnames = {'OpenSubtitles2011': 'OpenSubtitles 2011',
                 'OpenSubtitles2012': 'OpenSubtitles 2012',
                 'OpenSubtitles2013': 'OpenSubtitles 2013',
                 'OpenSubtitles2014': 'OpenSubtitles 2014',
                 'OpenSubtitles2015': 'OpenSubtitles 2015',
                 'OpenSubtitles': 'OpenSubtitles',
                 'DGT': 'DGT - A collection of EU Translation Memories provided by the JRC',
                 'EMEA': 'EMEA - European Medicines Agency documents',
                 'ECB': 'ECB - European Central Bank corpus',
                 'KDE4': 'KDE4 - KDE4 localization files (v.2)',
                 'EUbookshop' : 'The EU bookshop corpus',
                 'GNOME': 'GNOME localization files',
                 'EUconst': 'The European constitution',
                 'PHP': 'The PHP manual corpus',
                 'Books': 'A collection of translated literature',
                 'Ubuntu': 'Ubuntu localization files',
                 'Tatoeba': 'A DB of translated sentences',
                 'Europarl': 'Europarl',
                 'JRC-Acquis': 'JRC-Acquis'}

    if printbatch:
        print('wget -O {corpname}.zip http://opus.lingfil.uu.se/download.php?f={corpname}%2F{lpair}.txt.zip &&'.format(corpname=corpusname,
                                                                                             lpair=lang1 + '-' + lang2))
        print('unzip {corpname}.zip &&'.format(corpname=corpusname))
        print('rm {corpname}.zip &&'.format(corpname=corpusname))
        print('python3 ~asahala/scripts/mosestovrt.py %s %s > %s.vrt &&' % (infilename1, year, infilename1))
        print('python3 ~asahala/scripts/mosestovrt.py %s %s > %s.vrt &&' % (infilename2, year, infilename2))
        print('python /v/korp/scripts/vrt-fix-attrs.py --encode-special-chars=all < %s.vrt > %s.fix &&' % (infilename1, infilename1))
        print('python /v/korp/scripts/vrt-fix-attrs.py --encode-special-chars=all < %s.vrt > %s.fix &&' % (infilename2, infilename2))
        print('mkdir /corp/corpora/data/%s &&' % dirname1)
        print('mkdir /corp/corpora/data/%s &&' % dirname2)
        print('/usr/local/cwb/bin/cwb-encode -xsB -c utf8 -d /v/corpora/data/%s -R /v/corpora/registry/%s -S text:0+title+datefrom+dateto -S paragraph:0+id -S sentence:0+id -f %s.fix &&' % (dirname1, dirname1, infilename1))
        print('/usr/local/cwb/bin/cwb-encode -xsB -c utf8 -d /v/corpora/data/%s -R /v/corpora/registry/%s -S text:0+title+datefrom+dateto -S paragraph:0+id -S sentence:0+id -f %s.fix &&' % (dirname2, dirname2, infilename2))
        print('/usr/local/bin/cwb-make -r /v/corpora/registry -g korp -M 2000 %s &&' % (dirname1.upper()))
        print('/usr/local/bin/cwb-make -r /v/corpora/registry -g korp -M 2000 %s &&' % (dirname2.upper()))
        print('cwb-align -v -r /v/corpora/registry -o %s.align -V paragraph_id %s %s paragraph &&' % (corpusname + lang1 + '-' + lang2, dirname1, dirname2))
        print('cwb-align -v -r /v/corpora/registry -o %s.align -V paragraph_id %s %s paragraph &&' % (corpusname + lang2 + '-' + lang1, dirname2, dirname1))
        print('cwb-regedit -r /v/corpora/registry %s :add :a %s &&' % (dirname1, dirname2))
        print('cwb-regedit -r /v/corpora/registry %s :add :a %s &&' % (dirname2, dirname1))
        print('cwb-align-encode -v -r /v/corpora/registry -D %s.align &&' % (corpusname + lang1 + '-' + lang2))
        print('cwb-align-encode -v -r /v/corpora/registry -D %s.align &&' % (corpusname + lang2 + '-' + lang1))
        print('python /v/korp/scripts/vrt-extract-timespans.py --timespans-prefix=%s %s.vrt > %s-timespans.tsv &&' % (dirname1.upper(), infilename1, infilename1))
        print('python /v/korp/scripts/vrt-extract-timespans.py --timespans-prefix=%s %s.vrt > %s-timespans.tsv &&' % (dirname2.upper(), infilename2, infilename2))
        print("""mysql --local-infile --user korp --execute "LOAD DATA LOCAL INFILE '%s-timespans.tsv' INTO TABLE timespans;" korp &&""" % infilename1)
        print("""mysql --local-infile --user korp --execute "LOAD DATA LOCAL INFILE '%s-timespans.tsv' INTO TABLE timespans;" korp &&""" % infilename2)
        print('\n\n\n\n')

    if printjs:
        print('''settings.corpora.%s = {
            title : "%s",
            description : "%s",
            id : "%s",
            urn : "opus_urn",
            metadata_urn : "opus_meta",
            lang : "fin",
            linked_to : ["%s"],
            context: context.alignAligned,
            within: {
                "sentence": "sentence"
            },
            within : settings.spWithin,
            context : settings.spContext,
            attributes : {
            },
            struct_attributes : sattrlist.opus
        };
        ''' % (dirname2, corpusname, corpnames[corpusname], dirname2, dirname1))
        print('''settings.corpora.%s = {
            title : "%s",
            description : "%s",
            id : "%s",
            urn : "opus_urn",
            metadata_urn : "opus_meta",
            lang : "dan",
            linked_to : ["%s"],
            context: context.alignAligned,
            within: {
                "sentence": "sentence"
            },
            within : settings.spWithin,
            context : settings.spContext,
            attributes : {
            },
            struct_attributes : sattrlist.opus,
            hide : true
        };
        ''' % (dirname1, corpusname, corpnames[corpusname], dirname1, dirname2))

    
for line in lista.split('\n'):
    if line.startswith('1'):
        line = line.split(',')
        gen(line[1], lpair, line[1].lower(), line[2])
