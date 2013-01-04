# -*- coding: utf-8 -*-


SRC_FILES = *.xml

P_ATTRS = lemma pos msd func lex

CORPNAME_PREFIX = la_

XML2VRT_RULES = la_murre-xml2vrt_rules.py
LEMGRAM_POSMAP = la_murre-lemgram_posmap.tsv

MAKE_VRT_CMD = $(XML2VRT) | $(VRT_ADD_LEMGRAMS)
MAKE_VRT_DEPS_EXTRA = $(firstword $(VRT_ADD_LEMGRAMS))

CORPUS_DATE = unknown

include ../../corp-common.mk
