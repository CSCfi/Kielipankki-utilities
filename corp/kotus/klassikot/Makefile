# -*- coding: utf-8 -*-


CORPNAME_BASE = kotus_klassikot

SRC_SUBDIR = kotus/klassikot/teksti
SRC_FILES = */*.xml

MAKE_VRT_CMD = ../../scripts/tei2vrt.py --mode=stories --tokenize \
		--para-as-sent --morpho-tag-separator=' '

MAKE_VRT_SEPARATE_FILES = true

P_ATTRS = 

CORPUS_DATE_PATTERN = 'text title \(((?:1[0-9]|20)[0-9][0-9])'

COMPRESS_TARGETS = bz2

include ../../corp-common.mk
