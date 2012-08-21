# -*- coding: utf-8 -*-


# Do not remake if makefiles are changed (because of the time it takes
# to rebuild the corpus).
MAKEFILE_DEPS = false

P_ATTRS = lemma lemmacomp pos msd dephead deprel lex
S_ATTRS = sentence:0+id+line file:0+name subcorpus:0+name

SRC_FILES = \
	formatted_sentences_all_parsed_07122011.txt.phrm.tag2.conllx.final.bz2

MAKE_VRT_CMD = ./ftbconllx2vrt.py --lemgrams
MAKE_RELS_CMD = ./ftbvrt2wprel.py --input-type=ftb3


include ftb-common.mk
