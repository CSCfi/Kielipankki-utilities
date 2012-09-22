# -*- coding: utf-8 -*-


# Do not remake if makefiles are changed (because of the time it takes
# to rebuild the corpus).
MAKEFILE_DEPS ?= false

P_ATTRS = lemma lemmacomp pos posorig msd dephead deprel lex
S_ATTRS = sentence:0+id+line file:0+name subcorpus:0+name

# SRC_FILES = ftb3-100000.txt.bz2
SRC_FILES ?= \
	formatted_sentences_all_parsed_07122011.txt.phrm.tag2.conllx.final.bz2

MAKE_VRT_CMD = ./ftbconllx2vrt.py --lemgrams --pos-type=clean+original \
			--morpho-tag-separator=":"
MAKE_RELS_CMD = ./ftbvrt2wprel.py --input-type=ftb3-extrapos \
		--output-prefix=$(value CORPNAME)_rels \
		--compress=$(value COMPRESS)


include ftb-common.mk
