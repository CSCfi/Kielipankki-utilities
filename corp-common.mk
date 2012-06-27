# -*- coding: utf-8 -*-


CORPNAME_U := $(shell echo $(CORPNAME) | perl -pe 's/(.*)/\U$$1\E/')

DBUSER = korp
DBNAME = korp

CWBDIR = /usr/local/cwb/bin
CORPDIR = /corpora/data
REGDIR = /corpora/registry

CWB_ENCODE = $(CWBDIR)/cwb-encode -d $(CORPDIR)/$(CORPNAME) -f $(CORPNAME).vrt -R $(REGDIR)/$(CORPNAME) -xsB -c utf8
CWB_MAKEALL = $(CWBDIR)/cwb-makeall -V -r $(REGDIR) $(CORPNAME_U)

P_OPTS = $(foreach attr,$(P_ATTRS),-P $(attr))
S_OPTS = $(foreach attr,$(S_ATTRS),-S $(attr))


reg: vrt info
	$(CWB_MAKEALL)
	cp -p info $(CORPDIR)/$(CORPNAME)/.info

vrt: $(CORPNAME).vrt
	-mkdir $(CORPDIR)/$(CORPNAME)
	$(CWB_ENCODE) $(P_OPTS) $(S_OPTS)

info: $(CORPNAME).vrt
	egrep '<sentence' $< | tail -1 \
	| perl -ne '/"(.*?)"/; print "Sentences: $$1\n"' > $@
	ls -l --time-style=long-iso $< \
	| perl -ne '/(\d{4}-\d{2}-\d{2})/; print "Updated: $$1\n"' >> $@

korp_db: korp_rels korp_lemgrams

korp_rels: $(CORPNAME)_rels.tsv
	mysql --user $(DBUSER) --execute "truncate table relations_$(CORPNAME_U); load data local infile '$<' into table relations_$(CORPNAME_U);" $(DBNAME)

korp_lemgrams: $(CORPNAME)_lemgrams.tsv
	mysql --user $(DBUSER) --execute "delete from lemgram_index where corpus='$(CORPNAME_U)'; load data local infile '$<' into table lemgram_index;" $(DBNAME)

$(CORPNAME)_lemgrams.tsv: $(CORPNAME).vrt
	egrep -v '<' $< \
	| gawk -F'	' '{print $$NF}' \
	| tr -d '|' \
	| sort \
	| uniq -c \
	| perl -pe 's/^\s*(\d+)\s*(.*)/$$2\t$$1\t0\t0\t$(CORPNAME_U)/' > $@
