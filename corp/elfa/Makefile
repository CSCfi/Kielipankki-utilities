# -*- coding: utf-8 -*-


P_ATTRS = \
	type subtype mode voice elemstack synch overlap_speaker overlap_content

S_ATTRS_FEATSET = sentence_speaker_l1

SRC_FILES = ELFA_xml/[CU]*.xml

COMPRESS_TARGETS = gz

CORPUS_DATE_PATTERN = 'text date'
CORPUS_DATE_FULL_ORDER = ymd

MAKE_VRT_SEPARATE_FILES = true
MAKE_VRT_PROG = elfa-tei2vrt.py
MAKE_VRT_CMD = $(RUN_PYTHON) $(MAKE_VRT_PROG)


include ../corp-common.mk
