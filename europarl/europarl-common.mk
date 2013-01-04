# -*- coding: utf-8 -*-


# Do not remake if makefiles are changed (because of the time it takes
# to rebuild the corpus).
MAKEFILE_DEPS ?= false

SRC_SUBDIR = europarl

MAKE_VRT_CMD = ../scripts/europarl2vrt.py --tokenize --add-link-elements

CORPUS_DATE = unknown

P_ATTRS = 
S_ATTRS = sentence:0+id

include ../corp-common.mk
