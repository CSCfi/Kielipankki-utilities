# -*- coding: utf-8 -*-


P_ATTRS = lemma pos msd dephead deprel ref spoken lex

SRC_DIR = .
SRC_FILES = reitti_a-siipeen_FTBparse_orig.txt

CORPUS_DATE = 2012

MAKE_VRT_CMD = ./mt2vrt.pl --no-lemgrams --no-fix-morpho-tags # --morpho-tag-separator=":"
MAKE_RELS_CMD = $(SCRIPTDIR)/ftbvrt2wprel.py \
			--input-fields="word $(P_ATTRS)" \
			--output-prefix=$(CORPNAME)_rels \
			--compress=$(COMPRESS)

LEMGRAM_POSMAP = ../ftb/lemgram_posmap_ftb.tsv


include ../corp-common.mk


reitti_a-siipeen_FTBparse_orig.txt: reitti_a-siipeen_original_tok.txt \
		reitti_a-siipeen_FTBparse.txt
	./align-tokens.pl $^ > $@
