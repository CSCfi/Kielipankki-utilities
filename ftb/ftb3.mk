# -*- coding: utf-8 -*-


P_ATTRS = lemma lemma2 pos msd dephead deprel lex
S_ATTRS = sentence:0+id+line file:0+name subcorpus:0+name


include ftb-common.mk


INPUT_FILE = formatted_sentences_all_parsed_07122011.txt.phrm.tag2.conllx.final
# INPUT_FILE = ftb3-100000.txt


$(CORPNAME).vrt: $(INPUT_FILE)
	./ftbconllx2vrt.py --lemgrams < $^ > $@

$(CORPNAME)_rels.tsv: $(CORPNAME).vrt
	./ftbvrt2wprel.py --input-type=ftb3 < $< > $@
