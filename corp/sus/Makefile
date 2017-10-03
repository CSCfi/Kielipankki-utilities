# -*- coding: utf-8 -*-

# SUS Fieldwork corpus (sample)


CORPNAME_BASE = sust

SUBCORPORA = kpv mdf myv

P_ATTRS = ref lemma pos msd phon

SRC_SUBDIR = sus/$(SUBCORPUS)

SRC_FILES = $(shell find $(SRC_DIR) -name \*.xml | sed -e 's,$(SRC_DIR),,')

MAKE_VRT_XSLT = sus-xml2vrt.xslt 
MAKE_VRT_CMD = xsltproc $(MAKE_VRT_XSLT) -
MAKE_VRT_PROG =
MAKE_VRT_SEPARATE_FILES = true
MAKE_VRT_DEPS_EXTRA = $(MAKE_VRT_XSLT)

CORPUS_DATE_PATTERN = "text recdate"

COMPRESS = gz


include ../corp-common.mk
