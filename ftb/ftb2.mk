# -*- coding: utf-8 -*-


P_ATTRS = lemma pos msd dephead deprel lex
S_ATTRS = sentence:0+id subcorpus:0+name

SRC_FILES = *_tab.txt
SRC_FILES_EXCLUDE = news-samples%

MAKE_VRT_CMD = ./ftb2vrt.pl --lemgrams --no-fix-morpho-tags # --morpho-tag-separator=":"
# ftb2vrt.pl needs file names as arguments; does not read from stdin.
MAKE_VRT_FILENAME_ARGS = 1
MAKE_RELS_CMD = ./ftbvrt2wprel.py --output-prefix=$(value CORPNAME)_rels \
		--compress=$(value COMPRESS) --sort

CORPUS_DATE = unknown


include ftb-common.mk
