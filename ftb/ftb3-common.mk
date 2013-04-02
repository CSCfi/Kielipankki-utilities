# -*- coding: utf-8 -*-


# Do not remake if makefiles are changed (because of the time it takes
# to rebuild the corpus).
MAKEFILE_DEPS ?= false

SRC_DIR ?= $(CORPSRCROOT)/ftb/ftb3

P_ATTRS = lemma lemmacomp pos msd dephead deprel lex

MAKE_VRT_CMD = ./ftbconllx2vrt.py --lemgrams --pos-type=original \
			--no-fix-morpho-tags --no-subcorpora
MAKE_RELS_CMD = ./ftbvrt2wprel.py --input-type=ftb3 \
		--output-prefix=$(value CORPNAME)_rels \
		--compress=$(value COMPRESS) --sort

VRT_EXTRACT_TIMESPANS_OPTS = --two-digit-years --full-dates --exclude "* id"

include ftb-common.mk
