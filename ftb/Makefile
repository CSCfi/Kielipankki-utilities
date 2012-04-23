# -*- coding: utf-8 -*-


CORPNAME = ftb2

CWBDIR = /usr/local/cwb/bin
CORPDIR = /corpora/data
REGDIR = /corpora/registry

CWB_ENCODE = $(CWBDIR)/cwb-encode -d $(CORPDIR)/$(CORPNAME) -f $(CORPNAME).vrt -R $(REGDIR)/$(CORPNAME) -xsB -c utf8
CWB_MAKEALL = $(CWBDIR)/cwb-makeall -V -r $(REGDIR) $(shell echo $(CORPNAME) | perl -pe 's/(.*)/\U$$1\E/')

P_ATTRS = lemma pos msd dephead deprel
S_ATTRS = sentence:0+id subcorpus:0+name
P_OPTS = $(foreach attr,$(P_ATTRS),-P $(attr))
S_OPTS = $(foreach attr,$(S_ATTRS),-S $(attr))

reg: vrt
	$(CWB_MAKEALL)

vrt: ftb2.vrt
	-mkdir $(CORPDIR)/$(CORPNAME)
	$(CWB_ENCODE) $(P_OPTS) $(S_OPTS)

ftb2.vrt: $(wildcard FinnTreeBank_2/*_tab.txt)
	./ftb2vrt.pl $^ > $@
