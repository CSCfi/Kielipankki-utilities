'''Hopefully this extracts usable CoNLL-U from the parallel CEAL VRT,
stdin to stdout. All ampersands are in &amp; so only that is handled.
Start tags are preserved as is, end tags are dropped.

'''

import sys

for line in sys.stdin:
    if line.startswith('<!'): continue
    if line.startswith('</'):
        line.startswith('</sentence>') and print()
        continue
    if line.startswith('<'):
        print('#', line, end = '')
        continue

    # dropping \n in LEX (dropping LEX anyway)
    [
        WORD, REF, LEMMA, LEMMACOMP, POS, XPOS,
        MSD, DEPHEAD, DEPREL, DEPS, MISC, LEX
    ] = line.split('\t')
    print(REF,
          WORD.replace('&amp;', '&'),
          LEMMA.replace('&amp;', '&'),
          POS,
          XPOS,
          MSD.replace(' ', '|'),
          DEPREL,
          DEPHEAD,
          DEPS,
          MISC,
          sep = '\t')
