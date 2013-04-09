# -*- coding: utf-8 -*-


# Do not remake if makefiles are changed (because of the time it takes
# to rebuild the corpus).
MAKEFILE_DEPS ?= false

P_ATTRS = lemma lemmacomp pos posorig msd dephead deprel lex
S_ATTRS = sentence:0+id+line file:0+name subcorpus:0+name

# SRC_FILES = ftb3-100000.txt.bz2
SRC_FILES ?= ftb3.conllx.bz2 
# SRC_FILES ?= formatted_sentences_all_parsed_07122011.txt.phrm.tag2.conllx.final.bz2

MAKE_VRT_CMD = $(SCRIPTDIR)/ftbconllx2vrt.py --lemgrams \
			--pos-type=clean+original \
			--no-fix-morpho-tags # --morpho-tag-separator=":"
MAKE_RELS_CMD = $(SCRIPTDIR)/ftbvrt2wprel.py --input-type=ftb3-extrapos \
		--output-prefix=$(CORPNAME)_rels \
		--compress=$(COMPRESS) --sort

VRT_EXTRACT_TIMESPANS_OPTS = --two-digit-years --full-dates --exclude "* id"

include ftb-common.mk
