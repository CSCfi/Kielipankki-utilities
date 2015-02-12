# -*- coding: utf-8 -*-


TEI2VRT_OPTS = --mode=statute-modern --words \
		--morpho-tag-separator=" " --para-elem-name=paragraph

P_ATTRS = lemma lemmacomp pos msd id lex

CORPUS_DATE_PATTERN = 'text title /\s*((?:19|20)[0-9][0-9])'

include ns-common.mk
