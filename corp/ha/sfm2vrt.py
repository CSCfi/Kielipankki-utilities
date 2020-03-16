from __future__ import print_function

# Before:
# Remove carriage returns: sed -i $'s/\r//'
# Remove empty lines: sed -i '/^\s*$/d'

# After: run postprocess-ha-whitespace-and-punctuation.pl on VRTFILE
# and then postprocess-ha-add-lemmas.pl.
# Also add <text filename="" title="" datefrom="YYYYMMDD" dateto="YYYYMMDD">
# ... </text> tags around the file.

# Expected format of input:

# \n [name of the story -> title of a new chapter]

# \t  [ from
# \m  [ 1
# \g  [ to
# \p  [ inf times -> between new sentence ]

# \f  [translation -> en_transl attribute of sentence]
# \rf [ignored -> end of sentence]

# \dt [ignored -> end of chapter]

# All other tag lines are ignored.

import sys

if len(sys.argv) < 3 or sys.argv[1] == '--help':
    print('')
    print('Usage: sfm2vrt.py SFMFILE VRTFILE [EXTRA_PARAMS]')
    print('')
    print('SFMFILE:      The original file in sfm format.')
    print('VRTFILE:      The corresponding file in vrt format.')
    print('EXTRA_PARAMS (mostly designed for debugging):')
    print('  --print-all-words:          Print all words.')
    print('  --print-all-translations:   Print all translated sentences.')
    print('  --dry-run:                  Do not write anything.')
    print('')
    print('This script is mainly designed for converting ha language')
    print('corpora from sfm to vrt format. After running the script, you')
    print('need to postprocess the result with postprocess-ha-whitespace-and-punctuation.pl')
    print('and postprocess-ha-add-lemmas.pl.')
    print('')
    exit(0)

try:
    import toolbox
except ImportError:
    print("Error: module 'toolbox' could not be imported.")
    print("You must first install it (https://github.com/goodmami/toolbox).")
    
data = toolbox.read_toolbox_file(open(sys.argv[1]), 'r')

print_all_words=False
if '--print-all-words' in sys.argv:
    print_all_words=True
print_all_translations=False
if '--print-all-translations' in sys.argv:
    print_all_translations=True
dry_run=False
if '--dry-run' in sys.argv:
    dry_run=True

class FooFile:
    def write(self, s):
        pass

vrtfile_ha = None
if not dry_run:
    vrtfile_ha = open(sys.argv[2], 'w')
else:
    vrtfile_ha = FooFile()
    
line_number=0
chapter_number=0
sentence_number=0

indices=None
text_line=None
morpheme_line=None
gloss_line=None
pos_line=None
processing_sentence=False
mkr_read=None
sentence_start_tag=""
sentence=""

for mkr, text in data:
    line_number=line_number+1
    # lines starting with \t, \m, \g, and \p must be in this order
    if (mkr_read == '\\t' and mkr != '\\m') or (mkr_read == '\\m' and mkr != '\\g') or (mkr_read == '\\g' and mkr != '\\p'):
        print(mkr_read + " " + mkr + " line: " + str(line_number))
        print(text)
        raise RuntimeError('')
    # marks start of chapter
    if mkr == '\\n':
        mkr_read=str(mkr)
        chapter_number=chapter_number+1
        vrtfile_ha.write('<chapter id="' + str(chapter_number) + '" title="' + text + '">\n')
        continue
    # marks end of chapter, value is ignored
    elif mkr == '\\dt':
        mkr_read=str(mkr)
        vrtfile_ha.write('</chapter>\n')
        continue
    # start of { \t, \m, \g, \p } lines
    elif mkr == '\\t':
        mkr_read=str(mkr)
        if not processing_sentence:
            sentence_number=sentence_number+1
            sentence_start_tag = sentence_start_tag + '<sentence id="' + str(sentence_number) + '" '
        processing_sentence=True
        tmgp=True
        indices=[0]
        i=0
        space=False
        for c in text:
            if c == ' ':
                space=True
            else:
                if space == True:
                    indices.append(i)
                    space=False
            i = i+1
        text_line=str(text)
    elif mkr == '\\m':
        mkr_read=str(mkr)
        morpheme_line=str(text)
    elif mkr == '\\g':
        mkr_read=str(mkr)
        gloss_line=str(text)
    elif mkr == '\\p':
        mkr_read=str(mkr)
        pos_line=str(text)

    # Handle the four markers (\t, \m, \g, \p) just read:

        lines=[text_line, morpheme_line, gloss_line, pos_line]
        
        for i in range(0, len(indices)-1):
            for line in lines:
                if print_all_words and line == text_line:
                    print(line[indices[i]:indices[i+1]])
                sentence = sentence + line[indices[i]:indices[i+1]] + '\t'
            sentence = sentence + '\n'
        for line in lines:
            if print_all_words and line == text_line:
                print(line[indices[-1]:])
            sentence = sentence + line[indices[-1]:] + '\t'
        sentence = sentence + '\n'

        for line in lines:
            line=None
    # marks end of sentence, value is ignored
    elif mkr == '\\rf':
        mkr_read=str(mkr)
        sentence = sentence + '</sentence>\n'
        processing_sentence=False
    # English translation
    elif mkr == '\\f':
        mkr_read=str(mkr)
        if text == None:
            sentence_start_tag = sentence_start_tag + 'transl_en="NO_TRANSLATION">\n'
            print('warning: empty translation, replacing it with "NO_TRANSLATION"')
        else:
            line_number = line_number + text.count('\n')
            if print_all_translations:
                print(text)
                print('')
            sentence_start_tag = sentence_start_tag + 'transl_en="' + text.replace('\n', ' ').replace('"', '&quot;') + '">\n'
        vrtfile_ha.write(sentence_start_tag)
        vrtfile_ha.write(sentence)
        sentence_start_tag=""
        sentence=""
    # other tags are skipped
    else:
        mkr_read=str(mkr)
