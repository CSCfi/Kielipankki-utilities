# -*- coding: utf-8 -*-


P_ATTRS = lemma lemmacomp pos msd dephead deprel lex
S_ATTRS = sentence:0+id+line file:0+name subcorpus:0+name

SRC_FILES = formatted_sentences_all_parsed_07122011.txt.phrm.tag2.conllx.final.bz2
# INPUT_FILE = ftb3-s5pc.txt

MAKE_VRT_CMD = ./ftbconllx2vrt.py --lemgrams
MAKE_RELS_CMD = ./ftbvrt2wprel.py --input-type=ftb3


include ftb-common.mk


# $(CORPNAME).vrt: $(INPUT_FILE)
# 	./ftbconllx2vrt.py --lemgrams < $^ > $@

# $(CORPNAME)_rels.tsv: $(CORPNAME).vrt
# 	./ftbvrt2wprel.py --input-type=ftb3 < $< > $@
