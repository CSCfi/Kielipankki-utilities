# -*- coding: utf-8 -*-


TEI2VRT_OPTS = --words --morpho-tag-separator=" " \
		--para-elem-name=paragraph --kaino-urls --kotus-metadata \
		--filename="$$filename"
# $$filenamem above refers to the input filename as specified in the
# shell loop calling MAKE_VRT_CMD in corp-common.mk

P_ATTRS = lemma lemmacomp pos msd id lex

CORPUS_DATE_PATTERN = "text date"
CORPUS_DATE_FULL_ORDER = dmy

include ns-common.mk
