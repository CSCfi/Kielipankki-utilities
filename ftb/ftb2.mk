# -*- coding: utf-8 -*-


P_ATTRS = lemma pos msd dephead deprel lex
S_ATTRS = sentence:0+id subcorpus:0+name


include ftb-common.mk


$(CORPNAME).vrt: $(wildcard FinnTreeBank_2/*_tab.txt)
	./ftb2vrt.pl --lemgrams $^ > $@

$(CORPNAME)_rels.tsv: $(CORPNAME).vrt
	./ftbvrt2wprel.py < $< > $@
