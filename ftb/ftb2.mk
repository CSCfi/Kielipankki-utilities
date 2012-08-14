# -*- coding: utf-8 -*-


P_ATTRS = lemma pos msd dephead deprel lex
S_ATTRS = sentence:0+id subcorpus:0+name

SRC_FILES = $(wildcard FinnTreeBank_2/*_tab.txt)

MAKE_VRT_CMD = ./ftb2vrt.pl --lemgrams
# ftb2vrt.pl needs file names as arguments; does not read from stdin.
MAKE_VRT_FILENAME_ARGS = 1
MAKE_RELS_CMD = ./ftbvrt2wprel.py


include ftb-common.mk
