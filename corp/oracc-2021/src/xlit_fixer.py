import re
import os
from collections import Counter
from collections import defaultdict

""" Generate a fix list for some broken transliterations. At first
try to find correct transliterations from the corpus, e.g. KUR.KUR for
KURKUR. If this fails, try segmenting signs by using regex, e.g. by
finding impossible consonant and vowel clusters and split them.

The script writes a replace list that can be used to re-generate
the vrt files. """

INDEX = r'[₁₂₃₄₅₆₇₈₉₀]'
logo_cons = 'BDGHKLMNPQRSŠTW'
C = r'[%s]' % logo_cons
INVALID_C_CLUSTERS = [a+b for a in logo_cons for b in logo_cons]
VALID_C_CLUSTERS = []

def writefile(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        for d in data:
            f.write(d + '\n')

def fix(xlit):
    """ Fix series of transliteration issues in CAMS """
    xlit = re.sub(f'({INDEX})([a-zšṭṣ])', r'\1-\2', xlit)
    xlit = re.sub(f'({INDEX})([A-ZŠ])', r'\1.\2', xlit)
    xlit = re.sub('([aue])([aue])', r'\1-\2', xlit)
    xlit = re.sub('(i)([uie])', r'\1-\2', xlit)
    xlit = re.sub('(aeu)(i)', r'\1-\2', xlit)
    xlit = re.sub('([AIUE])([AUIE])', r'\1.\2', xlit)
    xlit = re.sub('([A-ZŠa-zšṭṣ])(MEŠ)', r'\1-\2', xlit)
    xlit = xlit.replace('{d}NIN', '{d}NIN.')

    for c in INVALID_C_CLUSTERS:
        xlit = xlit.replace(c, f'{c[0]}.{c[1]}')
    return xlit

def read_vrt(files):
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            for l in f.read().splitlines():
                if not l.startswith('<'):
                    yield l.split('\t')[0]

def make_error_list(data):
    """ Generate a set of words that are likely erroneous """
    errs=set()
    for xlit in data:
        if not xlit.islower():
            xlit_stripped = re.sub('[\.-]', '', xlit)
            errs.add((xlit_stripped, xlit))
    return errs

def make_fix_list(data):
    """ Generate error : fix dictionary based on VRT without
    errors; also get a list of all consonant clusters """
    fixes = defaultdict(list)
    for xlit in data:
        if not xlit.islower():
            clusters = re.findall(f'({C})({C})', xlit)
            for c in clusters:
                VALID_C_CLUSTERS.append(c[0]+c[1])
            xlit_stripped = re.sub('[\.-]', '', xlit)
            fixes[xlit_stripped].append(xlit)

    """ Update the list of consonant clusters and remove valid
    ones from the list """
    for k, v in Counter(VALID_C_CLUSTERS).items():
        if v > 10:
            INVALID_C_CLUSTERS.remove(k)

    return {k: Counter(v).most_common()[0][0] for k, v in fixes.items()}

def make_replacer(errors, gold):
    """ make error : fix based on broken file and files without
    errors """
    f = 0
    n = 0
    for e_stripped, e_orig in errors:
        xlit = gold.get(e_stripped, None)
        if xlit is not None:
            if e_orig != xlit:
                f += 1
                yield f'{e_orig}\t{xlit}'
        else:
            e_fixed = fix(e_orig)
            if e_orig != e_fixed:
                n += 1
                yield f'{e_orig}\t{fix(e_fixed)}'
    print(f, n)

data = read_vrt(['../broken_vrt/cams-gkab.vrt'])
gkab_broken = make_error_list(data)

filelist = ('../vrt/'+f for f in os.listdir('../vrt')\
            if f.startswith(('saao', 'atae', 'rinap', 'adsd', 'ribo',
                             'cams', 'aemw', 'blms', 'riao', 'hbtin',
                             'rimanum', 'obmc')) and f != 'cams-gkab.vrt')
data = read_vrt(filelist)
fixes = make_fix_list(data)

replace_data = make_replacer(gkab_broken, fixes)

writefile('../norm/cams-gkab.txt', replace_data)
