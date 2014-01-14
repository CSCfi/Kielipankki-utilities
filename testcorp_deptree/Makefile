# -*- coding: utf-8 -*-


P_ATTRS = lemma pos msd dephead deprel ref spoken lex

SRC_DIR = .
SRC_FILES = testcorp.vrt0

CORPUS_DATE = 2012

MAKE_RELS_PROG = $(SCRIPTDIR)/ftbvrt2wprel.py
MAKE_RELS_CMD = cut -f1-6,8 \
		| $(MAKE_RELS_PROG) --input-type=ftb2 \
			--output-prefix=$(CORPNAME)_rels \
			--compress=$(COMPRESS)

include ../corp-common.mk
