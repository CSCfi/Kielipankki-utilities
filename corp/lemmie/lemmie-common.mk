# -*- coding: utf-8 -*-


SRC_SUBDIR := lemmie/tsv

SRC_FILE_BASE = $(or $(SRC_FILE_BASE_$(SUBCORPUS)),$(SUBCORPUS))

SRC_FILES = main_$(SRC_FILE_BASE).tsv
MAKE_VRT_DEPS_EXTRA = \
	$(CORP_BUILDDIR)/elements_$(SUBCORPUS).srt.tsv \
	$(CORP_BUILDDIR)/documents_$(SUBCORPUS).tsv

MAKE_VRT_SEPARATE_FILES = true
MAKE_VRT_PROG = ./lemmie-tsv2vrt.py
MAKE_VRT_CMD = \
	$(MAKE_VRT_PREPROCESS) \
	/usr/bin/env PYTHONPATH=$(SCRIPTDIR) $(MAKE_VRT_PROG) \
		--elem-file $(CORP_BUILDDIR)/elements_$(SUBCORPUS).srt.tsv \
		--doc-info-file $(CORP_BUILDDIR)/documents_$(SUBCORPUS).tsv

ifeq ($(LANG),sv)
HAS_LEMMACOMP = 1
VRT_FIX_ATTRS_OPTS_EXTRA = \
	--input-fields='word lemma pos msd' \
	--output-fields='word lemma:noboundaries lemma pos msd' \
	--compound-boundary-marker='_'
endif

P_ATTRS = lemma $(if $(HAS_LEMMACOMP),lemmacomp) pos msd lex/

LEMGRAM_POSMAP = lemmie_$(LANG)-lemgram_posmap.tsv

CORPUS_DATE_PATTERN = "text date"
CORPUS_DATE_FULL_ORDER = ymd

COMPRESS_TARGETS = gz

MAKE_PKG = $(and $(WITHIN_CORP_MK),$(HAS_SUBCORPORA))


include ../corp-common.mk


$(call showvars,SRC_FILE_BASE MAKE_VRT_DEPS_EXTRA MAKE_PKG)

$(CORP_BUILDDIR)/documents_$(SUBCORPUS).tsv: $(SRC_DIR)/documents.tsv
	mkdir -p $(dir $@)
	awk -F'	' 'NR == 1 || $$13 == "$(SRC_FILE_BASE)"' $< \
	| sort -t'	' -k1,1n > $@

$(CORP_BUILDDIR)/elements_$(SUBCORPUS).srt.tsv: \
		$(SRC_DIR)/elements_$(SRC_FILE_BASE).tsv
	mkdir -p $(dir $@)
	sort -t'	' -k2,2n -k4,4n -k6,6n -k1,1n $< > $@
