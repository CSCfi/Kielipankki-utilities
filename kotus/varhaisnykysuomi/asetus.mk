# -*- coding: utf-8 -*-


VNS2VRT_OPTS = --tokenize --para-as-sent --mode=statute

SRC_FILES = 1840heik.xml

P_ATTRS = 
S_ATTRS = text:0+distributor+source+title article:0+id paragraph:0+id \
		sentence:0+id+type hi:0+rend dateline:0

include vns-common.mk
