# -*- coding: utf-8 -*-


VNS2VRT_OPTS = --mode=statute --tokenize --para-as-sent \
		--morpho-tag-separator=' '

P_ATTRS = 
S_ATTRS = text:0+distributor+source+title article:0+id paragraph:0+id \
		sentence:0+id+type hi:0+rend dateline:0

include vns-common.mk
