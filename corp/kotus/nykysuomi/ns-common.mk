# -*- coding: utf-8 -*-


CORPNAME_PREFIX = kotus_ns_

SRC_SUBDIR = kotus/teko/teksti/$(CORPNAME_BASEBASE)/$(SUBCORPUS)

SUBDIRS_AS_SUBCORPORA = true

SRC_FILES ?= *.xml

MAKE_VRT_CMD = ../../scripts/tei2vrt.py $(TEI2VRT_OPTS)

MAKE_VRT_SEPARATE_FILES = true

LEMGRAM_POSMAP = lemgram_posmap_kotus_ns.tsv

COMPRESS_TARGETS = bz2

include ../../corp-common.mk
