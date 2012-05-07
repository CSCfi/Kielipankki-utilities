# -*- coding: utf-8 -*-


CORPNAME = metsatalo


include ../corp-common.mk


P_ATTRS = lemma pos msd dephead deprel spoken lex
S_ATTRS = sentence:0+id


reitti_a-siipeen_FTBparse_orig.txt: reitti_a-siipeen_original_tok.txt \
		reitti_a-siipeen_FTBparse.txt
	./align-tokens.pl $^ > $@

$(CORPNAME).vrt: reitti_a-siipeen_FTBparse_orig.txt
	./mt2vrt.pl --lemgrams $^ > $@

$(CORPNAME)_rels.tsv: $(CORPNAME).vrt
	cut -f1-6,8 $< \
	| ../ftb/ftbvrt2wprel.py > $@
