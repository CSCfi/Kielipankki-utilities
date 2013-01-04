# -*- coding: utf-8 -*-


CORPNAME_BASE = kotus_klassikot

MAKE_VRT_CMD = ../../scripts/tei2vrt.py --mode=stories --tokenize \
		--para-as-sent --morpho-tag-separator=' '

SRC_FILES = *.xml

P_ATTRS = 
S_ATTRS = text:0+distributor+source+title collection:0+id+title \
		story:0+id+title sentence:0+id+type


include ../../corp-common.mk
