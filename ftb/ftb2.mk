# -*- coding: utf-8 -*-


P_ATTRS = lemma pos msd dephead deprel ref lex

SRC_FILES = *_tab.txt
SRC_FILES_EXCLUDE = news-samples% sofie%

MAKE_VRT_CMD = $(SCRIPTDIR)/ftb2vrt.pl --no-lemgrams --no-fix-morpho-tags # --lemgrams --morpho-tag-separator=":"
# ftb2vrt.pl needs file names as arguments; does not read from stdin.
MAKE_VRT_FILENAME_ARGS = 1
MAKE_RELS_CMD = $(SCRIPTDIR)/ftbvrt2wprel.py \
		--input-fields="word $(P_ATTRS)" \
		--output-prefix=$(CORPNAME_BUILDDIR)_rels \
		--compress=$(COMPRESS) --sort

LEMGRAM_POSMAP = lemgram_posmap_ftb.tsv

CORPUS_DATE = unknown

COMPRESS_TARGETS = bz2

include ftb-common.mk
