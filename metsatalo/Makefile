# -*- coding: utf-8 -*-


MAKE_VRT_CMD = ./mt2vrt.pl --lemgrams --no-fix-morpho-tags # --morpho-tag-separator=":"
MAKE_RELS_PROG = $(SCRIPTDIR)/ftbvrt2wprel.py
MAKE_RELS_CMD = cut -f1-6,8 \
		| $(MAKE_RELS_PROG) --input-type=ftb2 \
			--output-prefix=$(CORPNAME)_rels \
			--compress=$(COMPRESS)

P_ATTRS = lemma pos msd dephead deprel spoken lex
S_ATTRS = sentence:0+id

SRC_DIR = .
SRC_FILES = reitti_a-siipeen_FTBparse_orig.txt

CORPUS_DATE = 2012


include ../corp-common.mk


reitti_a-siipeen_FTBparse_orig.txt: reitti_a-siipeen_original_tok.txt \
		reitti_a-siipeen_FTBparse.txt
	./align-tokens.pl $^ > $@
