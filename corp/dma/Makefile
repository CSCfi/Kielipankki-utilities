# -*- coding: utf-8 -*-


CORPNAME_BASE = dma

SRC_FILES = tsv/dma6.tsv
# SRC_FILES = dma6-sample2.tsv.gz
# SRC_FILES = dma6-test2.tsv

P_ATTRS = searchword wordtype

CORPUS_DATE = unknown

COMPRESS_TARGETS = gz
S_ATTRS_FEATSET = "sentence_signum sentence_text_words sentence_search_words"

MAKE_VRT_PROG = ./dma-tsv2vrt.py
# First convert Windows CP-1252 punctuation characters left in the
# data to their UTF-8 equivalents and remove control characters.
MAKE_VRT_CMD = \
	perl -CSD -pe 's/\x85/\x{2026}/g; s/\x8A/\x{0160}/g; s/\x91/\x{2018}/g; s/\x92/\x{2019}/g; s/\x93/\x{201D}/g; s/\x94/\x{201E}/g; s/\x96/\x{2013}/g; s/\x9a/\x{0161}/g; s/[\x00-\x08\x0B-\x1F]//g' \
	| /usr/bin/env PYTHONPATH=$(SCRIPTDIR) ./dma-tsv2vrt.py

include ../corp-common.mk
