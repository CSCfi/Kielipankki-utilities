# -*- coding: utf-8 -*-


P_ATTRS = lemma lemmacomp pos msd dephead deprel ref spoken lex

# SRC_DIR = .
SRC_FILES_GENERATED = reitti_a-siipeen_normalized.conll09

UTTERANCE_FILE = $(SRC_DIR)/reitti_a-siipeen_utterances.csv

CORPUS_DATE = 20120217
TEXT_AUTHOR = Tero Aalto, Mietta Lennes
TEXT_TITLE = Reitti A-siipeen
TEXT_YEAR = $(shell echo $(CORPUS_DATE) | sed -e 's/\(....\).*/\1/')

VRT_ADD_UTTERANCES_OPTS = \
	--word-field-number=2 --pos-field-number=5 --skip-pos-regexp=Punct \
	--nodeid='MPI2817%23' --multi-word-alignment='2:niinku' \
	--attributes='id,participant,begintime,endtime,duration,annexlink'
MAKE_VRT_CMD = \
	$(SCRIPTDIR)/conll2vrt.py \
		--top-attribute "author=$(TEXT_AUTHOR)" \
		--top-attribute "title=$(TEXT_TITLE)" \
		--top-attribute "year=$(TEXT_YEAR)" \
	| $(SCRIPTDIR)/vrt-add-utterances.py \
		--utterance-file $(UTTERANCE_FILE) $(VRT_ADD_UTTERANCES_OPTS)
MAKE_VRT_DEPS_EXTRA = \
	$(SCRIPTDIR)/vrt-add-utterances.py $(UTTERANCE_FILE)

VRT_FIX_ATTRS_OPTS_EXTRA = \
	--input-fields='ref word lemma lemma2 pos pos2 msd msd2 dephead dephead2 deprel deprel2 dummy1 dummy2 spoken' \
	--output-fields='word lemma:noboundaries lemma pos msd dephead deprel ref spoken' \
	--compound-boundary-marker='|' --compound-boundary-can-replace-hyphen \
	--add-element-id='sentence paragraph'

LEMGRAM_POSMAP = ../lemgram_posmap_tdt.tsv
WORDPICT_RELMAP = ../wordpict_relmap_tdt.tsv

PARSER_DIR = $(HOME)/finclarin/fidepparser
PARSER = (cd $(PARSER_DIR); ./parser_wrapper.sh)


include ../corp-common.mk


$(CORP_BUILDDIR)/reitti_a-siipeen_normalized.conll09: \
		$(SRC_DIR)/reitti_a-siipeen_normalized_sents.txt
	cat $^ \
	| awk -F'	' '$$1 != "" {print "\t<p>"; print} $$1 == "" {print}' \
	| cut -d'	' -f2 \
	| $(PARSER) > $@
