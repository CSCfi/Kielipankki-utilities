# -*- coding: utf-8 -*-


CORPNAME_BASE = dma

SRC_FILES = tsv/dma6.tsv
# SRC_FILES = dma6-sample2.tsv.gz
# SRC_FILES = dma6-test2.tsv
SRC_FILES_GENERATED = dma_2014-2015.tsv

src_files_new = $(SRC_DIR)/uudet/*.txt

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


# Convert the new original files to roughly the same format as the SUI
# DMA MySQL database dump (dma6.tsv)
$(CORP_BUILDDIR)/dma_2014-2015.tsv: $(src_files_new)
	cat $^ \
	| tr -d '\015' \
	| grep -vih '^Area' \
	| grep -v '^	' \
	| perl -pe 's/\s+\n/\n/; s/(\s)\}(\s)/$$1]$$2/g' \
	| awk -F'	' 'BEGIN {OFS = FS} {$$8 = $$4; print}' \
	| scripts-old/muuta_korvausmerkit.pl \
	| scripts-old/muuta_rakenne.pl \
	| scripts-old/lisaa_pdf_linkit.pl \
	| perl -pe 's/^(.*?)\t(.*?)(\t.+)$$/\t$$1\t$$1 $$2\t$$2$$3\t/' \
	| iconv -fcp1252 > $@
