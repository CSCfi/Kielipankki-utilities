# -*- coding: utf-8 -*-


SRC_FILES = *.xml
SRC_FILES_EXCLUDE = la_murre_Korp_koe.xml vare_muurl_hali1_2.xml
# SRC_FILES = la_murre_Korp_koe.xml vare_muurl_hali1_2.xml

P_ATTRS = lemma pos msd func cow note lex

CORPNAME_PREFIX = la_

XML2VRT_RULES = la_murre.xml2vrt
LEMGRAM_POSMAP = la_murre-lemgram_posmap.tsv

MAKE_VRT_CMD = $(XML2VRT) | $(VRT_ADD_LEMGRAMS)
MAKE_VRT_DEPS_EXTRA = $(firstword $(VRT_ADD_LEMGRAMS))

CORPUS_DATE = unknown

include ../../corp-common.mk
