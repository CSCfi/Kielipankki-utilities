# -*- coding: utf-8 -*-


TEI2VRT_OPTS = --mode=statute-modern --words --lemgrams \
		--morpho-tag-separator=":"

SRC_FILES = laki10.xml

P_ATTRS = lemma lemmacomp pos msd id lex
S_ATTRS = text:0+distributor+source+title div:1+id+type para:0+id+type+topic \
		sentence:0+id+type

include ns-common.mk
