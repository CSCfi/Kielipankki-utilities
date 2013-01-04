# -*- coding: utf-8 -*-


CORPNAME_PREFIX = ns_

SRC_FILES = *.xml

MAKE_VRT_CMD = ../../scripts/tei2vrt.py $(TEI2VRT_OPTS)

include ../../corp-common.mk
