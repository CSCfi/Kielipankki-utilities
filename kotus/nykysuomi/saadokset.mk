# -*- coding: utf-8 -*-


TEI2VRT_OPTS = --mode=statute-modern --words --lemgrams \
		--morpho-tag-separator=" " --para-elem-name=paragraph

SRC_FILES = laki10.xml

P_ATTRS = lemma lemmacomp pos msd id lex
S_ATTRS = text:0+distributor+source+title div:1+id+type \
		paragraph:0+id+type+topic sentence:0+id+type

CORPUS_DATE_PATTERN = 'text title /\s*((?:19|20)[0-9][0-9])'

include ns-common.mk
