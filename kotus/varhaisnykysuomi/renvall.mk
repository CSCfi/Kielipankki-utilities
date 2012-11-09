# -*- coding: utf-8 -*-


VNS2VRT_OPTS = --mode=dictionary --tokenize --dict-info-as-sent-attrs \
		--morpho-tag-separator=' '

SRC_FILES = renvall.xml

P_ATTRS = 
S_ATTRS = text:0+distributor+source+title \
		sentence:0+etym+etymlang+example+form+pos+xref \
		item:0+itemtype+type+lang

include vns-common.mk
