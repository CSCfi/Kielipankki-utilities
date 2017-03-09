# -*- coding: utf-8 -*-


CORPNAME_BASE = kotus_sananparret

SRC_SUBDIR = kotus/sp/teksti
SRC_FILES = */*.xml

TEI2VRT_OPTS = --mode=sayings --tokenize --morpho-tag-separator=' '

MAKE_VRT_CMD = ../../scripts/tei2vrt.py $(TEI2VRT_OPTS)

MAKE_VRT_SEPARATE_FILES = true

P_ATTRS = 

COMPRESS_TARGETS = bz2

include ../../corp-common.mk
