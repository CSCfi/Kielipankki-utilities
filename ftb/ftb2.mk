# -*- coding: utf-8 -*-


P_ATTRS = lemma pos msd dephead deprel lex
# S_ATTRS = sentence:0+id subcorpus:0+name

SRC_FILES = *_tab.txt
SRC_FILES_EXCLUDE = news-samples% sofie%

MAKE_VRT_CMD = $(SCRIPTDIR)/ftb2vrt.pl --lemgrams --no-fix-morpho-tags # --morpho-tag-separator=":"
# ftb2vrt.pl needs file names as arguments; does not read from stdin.
MAKE_VRT_FILENAME_ARGS = 1
MAKE_RELS_CMD = $(SCRIPTDIR)/ftbvrt2wprel.py \
		--output-prefix=$(CORPNAME)_rels \
		--compress=$(COMPRESS) --sort

CORPUS_DATE = unknown

COMPRESS_TARGETS = bz2

include ftb-common.mk
