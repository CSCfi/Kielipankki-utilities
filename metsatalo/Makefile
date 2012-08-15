# -*- coding: utf-8 -*-


CORPNAME_BASE = metsatalo

MAKE_VRT_CMD = ./mt2vrt.pl --lemgrams
MAKE_RELS_PROG = ../ftb/ftbvrt2wprel.py
MAKE_RELS_CMD = cut -f1-6,8 | $(MAKE_RELS_PROG)

DB = 1

P_ATTRS = lemma pos msd dephead deprel spoken lex
S_ATTRS = sentence:0+id

SRC_FILES = reitti_a-siipeen_FTBparse_orig.txt


# Override the first target all-corp in corp-common.mk that assumes
# the existence of $(CORPNAME_BASE).mk.
all-override: all


include ../corp-common.mk


reitti_a-siipeen_FTBparse_orig.txt: reitti_a-siipeen_original_tok.txt \
		reitti_a-siipeen_FTBparse.txt
	./align-tokens.pl $^ > $@
