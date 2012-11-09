# -*- coding: utf-8 -*-


CORPNAME_BASE = kotus_sananparret

TEI2VRT_OPTS = --mode=sayings --tokenize --morpho-tag-separator=' '

MAKE_VRT_CMD = ../../scripts/tei2vrt.py $(TEI2VRT_OPTS)

SRC_FILES = tyrvaa.xml

P_ATTRS = 
S_ATTRS = text:0+distributor+source+title \
		entry:0+location+collector+date+standard+dialect+usage \
		sentence:0+type

include ../../corp-common.mk
