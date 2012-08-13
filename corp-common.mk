# -*- coding: utf-8 -*-


CORPORA ?= $(basename $(filter-out %-common.mk,$(wildcard *.mk)))

TARGETS ?= vrt reg $(if $(DB),db)

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


.PHONY: all-corp all $(CORPORA) $(TARGETS)


all-corp: $(CORPORA)

all: $(TARGETS)


# Define rules for targets $(CORPORA) and $(CORPORA)@$(TARGET)

define MAKE_CORPUS_R
$(1)$(if $(subst @,,$(2)),@$(2)):
	$$(MAKE) -f $(1).mk $(subst @,all,$(2)) CORPNAME=$(1)
endef

$(foreach corp,$(CORPORA),\
	$(foreach targ,$(TARGETS) @,\
		$(eval $(call MAKE_CORPUS_R,$(corp),$(targ)))))


reg: vrt $(CORPNAME).info
	$(CWB_MAKEALL)
	cp -p $(CORPNAME).info $(CORPDIR)/$(CORPNAME)/.info

vrt: $(CORPNAME).vrt
	-mkdir $(CORPDIR)/$(CORPNAME)
	-rm $(CORPDIR)/$(CORPNAME)/*
	$(CWB_ENCODE) $(P_OPTS) $(S_OPTS)

%.info: %.vrt
	echo "Sentences: "`egrep -c '^<sentence[> ]' $<` > $@
	ls -l --time-style=long-iso $< \
	| perl -ne '/(\d{4}-\d{2}-\d{2})/; print "Updated: $$1\n"' >> $@

db: korp_db

korp_db: korp_rels korp_lemgrams

# MySQL statement "load data local infile" gives an error message on
# Daniel: "ERROR 1148 (42000) at line 1: The used command is not
# allowed with this MySQL version". mysqlimport does the same thing.

korp_rels: $(CORPNAME)_rels.tsv
	mysql --user $(DBUSER) --execute 'CREATE TABLE IF NOT EXISTS `relations_$(CORPNAME_U)` (`head` varchar(1024) NOT NULL, `rel` char(3) NOT NULL, `dep` varchar(1024) NOT NULL, `depextra` varchar(1024) DEFAULT NULL, `freq` int(11) NOT NULL, `freq_rel` int(11) NOT NULL, `freq_head_rel` int(11) NOT NULL, `freq_rel_dep` int(11) NOT NULL, `wf` tinyint(4) NOT NULL, `sentences` text, KEY `head` (`head`(255)), KEY `dep` (`dep`(255))) ENGINE=InnoDB DEFAULT CHARSET=utf8;' $(DBNAME)
	mysql --user $(DBUSER) --execute "truncate table relations_$(CORPNAME_U);" $(DBNAME)
	-ln -sf $(CORPNAME)_rels.tsv relations_$(CORPNAME_U).tsv
	mysqlimport --user $(DBUSER) --local korp relations_$(CORPNAME_U)

korp_lemgrams: $(CORPNAME)_lemgrams.tsv
	ln -s $< lemgram_index.tsv
	mysql --user $(DBUSER) --execute "delete from lemgram_index where corpus='$(CORPNAME_U)';" $(DBNAME)
	mysqlimport --user $(DBUSER) --local korp lemgram_index.tsv
	rm lemgram_index.tsv

$(CORPNAME)_lemgrams.tsv: $(CORPNAME).vrt
	egrep -v '<' $< \
	| gawk -F'	' '{print $$NF}' \
	| tr -d '|' \
	| sort \
	| uniq -c \
	| perl -pe 's/^\s*(\d+)\s*(.*)/$$2\t$$1\t0\t0\t$(CORPNAME_U)/' > $@
