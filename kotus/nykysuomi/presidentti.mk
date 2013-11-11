# -*- coding: utf-8 -*-


TEI2VRT_OPTS = --words --lemgrams --morpho-tag-separator=" " \
		--para-elem-name=paragraph

P_ATTRS = lemma lemmacomp pos msd id lex
# S_ATTRS = text:0+distributor+source+title paragraph:0+id+type+topic \
# 		sentence:0+id

include ns-common.mk
