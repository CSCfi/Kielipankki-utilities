# -*- coding: utf-8 -*-

# Requires GNU Make

# This makefile is typically included in both the top-level Makefile
# of a corpus directory and the makefiles (*.mk) for the individual
# (sub)corpora in a corpus directory.


TOPDIR = $(dir $(lastword $(MAKEFILE_LIST)))

eq = $(and $(findstring $(1),$(2)),$(findstring $(2),$(1)))
eqs = $(call eq,$(strip $(1)),$(strip $(2)))
lower = $(shell echo $(1) | perl -pe 's/(.*)/\L$$1\E/')

SUBDIRS := \
	$(shell ls \
	| perl -ne 'chomp; print "$$_\n" if -d $$_ && -e "$$_/Makefile"')

CORPORA ?= $(or $(basename $(filter-out %-common.mk,$(wildcard *.mk))),\
		$(CORPNAME_BASE))

DB_TARGETS_ALL = korp_rels korp_lemgrams
DB_HAS_RELS := $(and $(filter dephead,$(P_ATTRS)),$(filter deprel,$(P_ATTRS)))
DB_TARGETS ?= $(if $(DB),$(DB_TARGETS_ALL),\
		$(if $(filter lex,$(P_ATTRS)),\
			korp_lemgrams $(if $(DB_HAS_RELS),korp_rels)))

TARGETS ?= subdirs vrt reg pkg $(if $(strip $(DB_TARGETS)),db)

CORPNAME := $(CORPNAME_PREFIX)$(CORPNAME_BASE)$(CORPNAME_SUFFIX)
CORPNAME_U := $(shell echo $(CORPNAME) | perl -pe 's/(.*)/\U$$1\E/')

DEP_MAKEFILES := $(if $(call eqs,$(call lower,$(MAKEFILE_DEPS)),false),,\
			$(MAKEFILE_LIST))

COMPRESS ?= $(strip $(if $(filter %.gz,$(SRC_FILES)),gz,\
		$(if $(or $(filter %.bz2,$(SRC_FILES)),\
			$(filter %.bz,$(SRC_FILES))),bz2,\
		none)))

COMPR_EXT_none = 
CAT_none = cat
COMPR_none = cat

COMPR_EXT_gz = .gz
CAT_gz = zcat
COMPR_gz = gzip

COMPR_EXT_bz2 = .bz2
CAT_bz2 = bzcat
COMPR_bz2 = bzip2

COMPR_EXT = $(COMPR_EXT_$(COMPRESS))
CAT = $(CAT_$(COMPRESS))
COMPR = $(COMPR_$(COMPRESS))

VRT = .vrt$(COMPR_EXT)
TSV = .tsv$(COMPR_EXT)

MAKE_VRT_PROG ?= $(firstword $(MAKE_VRT_CMD))
MAKE_RELS_PROG ?= $(firstword $(MAKE_RELS_CMD))

TRANSCODE := $(if $(INPUT_ENCODING),iconv -f$(INPUT_ENCODING) -tutf8,cat)

DBUSER = korp
DBNAME = korp
# Unix group for CWB corpus files
CORPGROUP = korp

CWBDIR = /usr/local/cwb/bin
CORPROOT = /v/corpora
CORPDIR = $(CORPROOT)/data
CORPCORPDIR = $(CORPDIR)/$(CORPNAME)
REGDIR = $(CORPROOT)/registry
CORPSQLDIR = $(CORPROOT)/sql

PKGDIR = $(TOPDIR)/export
PKG_FILE = $(PKGDIR)/korpdata_$(CORPNAME).tbz

CWB_ENCODE = $(CWBDIR)/cwb-encode -d $(CORPCORPDIR) -R $(REGDIR)/$(CORPNAME) \
		-xsB -c utf8
CWB_MAKEALL = $(CWBDIR)/cwb-makeall -V -r $(REGDIR) $(CORPNAME_U)
CWB_MAKE = cwb-make -r $(REGDIR) -g $(CORPGROUP) -M 2000 $(CORPNAME_U)

# MySQL statement "load data local infile" gives an error message on
# Daniel: "ERROR 1148 (42000) at line 1: The used command is not
# allowed with this MySQL version". mysqlimport does the same thing.
# mysqlimport only reads named files, so a named pipe created by mknod
# is used to support uncompressing compressed input on the fly.

MYSQL_IMPORT = mknod $(2) p; \
	($(CAT) $(1) > $(2) &); \
	mysqlimport --user $(DBUSER) --local korp $(2); \
	/bin/rm -f $(2)

P_OPTS = $(foreach attr,$(P_ATTRS),-P $(attr))
S_OPTS = $(foreach attr,$(S_ATTRS),-S $(attr))

SQLDUMP_NAME = $(CORPSQLDIR)/$(CORPNAME).mysql
SQLDUMP = $(if $(strip $(DB_TARGETS)),$(SQLDUMP_NAME))

DB_TIMESTAMPS = $(CORPNAME)_lemgrams_load.timestamp \
		$(if $(DB_HAS_RELS),$(CORPNAME)_rels_load.timestamp)


.PHONY: all-corp all all-override subdirs $(CORPORA) $(TARGETS) $(SUBDIRS)


# If $(CORPORA) == $(CORPNAME_BASE), the current directory does not
# have *.mk for subcorpora, so "all" should be the first target.

ifneq ($(strip $(CORPORA)),$(strip $(CORPNAME_BASE)))
all-corp: subdirs $(CORPORA)
endif

all: $(TARGETS)


subdirs: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@


# Define rules for targets $(CORPORA) and $(CORPORA)@$(TARGET)

define MAKE_CORPUS_R
$(1)$(if $(subst @,,$(2)),@$(2)):
	$$(MAKE) -f $(1).mk $(or $(TARGET),$(subst @,all,$(2))) \
		CORPNAME_BASE=$(1) DB=$(DB)
endef

$(foreach corp,$(CORPORA),\
	$(foreach targ,$(TARGETS) @,\
		$(eval $(call MAKE_CORPUS_R,$(corp),$(targ)))))


reg: vrt
	$(CWB_MAKE)

vrt: $(CORPCORPDIR)/.info

# The info file $(CORPCORPDIR)/.info is (ab)used as a timestamp file
# to avoid unnecessarily remaking the corpus data if the .vrt file has
# not changed.

$(CORPCORPDIR)/.info: $(CORPNAME)$(VRT) $(CORPNAME).info
	-mkdir $(CORPCORPDIR) || /bin/rm $(CORPCORPDIR)/*
	$(CAT) $< | $(CWB_ENCODE) $(P_OPTS) $(S_OPTS) \
	&& cp $(CORPNAME).info $(CORPCORPDIR)/.info

%.info: %$(VRT)
	echo "Sentences: "`$(CAT) $< | egrep -c '^<sentence[> ]'` > $@
	ls -l --time-style=long-iso $< \
	| perl -ne '/(\d{4}-\d{2}-\d{2})/; print "Updated: $$1\n"' >> $@

# This does not support passing compressed files or files requiring
# transcoding to a program requiring filename arguments. That might be
# achieved by using named pipes as for mysqlimport.
$(CORPNAME)$(VRT): $(SRC_FILES) $(MAKE_VRT_PROG) $(DEP_MAKEFILES)
ifdef MAKE_VRT_FILENAME_ARGS
	$(MAKE_VRT_CMD) $(SRC_FILES) \
	| $(COMPR) > $@
else
	$(CAT) $(SRC_FILES) \
	| $(TRANSCODE) \
	| $(MAKE_VRT_CMD) \
	| $(COMPR) > $@
endif

db: korp_db

korp_db: $(DB_TARGETS)

korp_rels: $(CORPNAME)_rels_load.timestamp

CREATE_RELS_SQL = '\
	CREATE TABLE IF NOT EXISTS `relations_$(CORPNAME_U)` ( \
		`head` varchar(1024) NOT NULL, \
		`rel` char(3) NOT NULL, \
		`dep` varchar(1024) NOT NULL, \
		`depextra` varchar(1024) DEFAULT NULL, \
		`freq` int(11) NOT NULL, \
		`freq_rel` int(11) NOT NULL, \
		`freq_head_rel` int(11) NOT NULL, \
		`freq_rel_dep` int(11) NOT NULL, \
		`wf` tinyint(4) NOT NULL, \
		`sentences` text, \
		KEY `head` (`head`(255)), \
		KEY `dep` (`dep`(255)) \
	) ENGINE=InnoDB DEFAULT CHARSET=utf8;'

$(CORPNAME)_rels_load.timestamp: $(CORPNAME)_rels$(TSV)
	mysql --user $(DBUSER) --execute $(CREATE_RELS_SQL) $(DBNAME)
	mysql --user $(DBUSER) \
		--execute "truncate table relations_$(CORPNAME_U);" $(DBNAME)
	$(call MYSQL_IMPORT,$<,relations_$(CORPNAME_U).tsv)
	touch $@

$(CORPNAME)_rels$(TSV): $(CORPNAME)$(VRT) $(MAKE_RELS_PROG)
	$(CAT) $< \
	| $(MAKE_RELS_CMD) \
	| $(COMPR) > $@

korp_lemgrams: $(CORPNAME)_lemgrams_load.timestamp

CREATE_LEMGRAMS_SQL = '\
	CREATE TABLE IF NOT EXISTS `lemgram_index` ( \
		`lemgram` varchar(64) NOT NULL, \
		`freq` int(11) DEFAULT NULL, \
		`freqprefix` int(11) DEFAULT NULL, \
		`freqsuffix` int(11) DEFAULT NULL, \
		`corpus` varchar(64) NOT NULL, \
		UNIQUE KEY `lemgram_corpus` (`lemgram`, `corpus`), \
		KEY `lemgram` (`lemgram`), \
		KEY `corpus` (`corpus`) \
	) ENGINE=InnoDB DEFAULT CHARSET=utf8;'

$(CORPNAME)_lemgrams_load.timestamp: $(CORPNAME)_lemgrams$(TSV)
	mysql --user $(DBUSER) --execute $(CREATE_LEMGRAMS_SQL) $(DBNAME)
	mysql --user $(DBUSER) \
		--execute "delete from lemgram_index where corpus='$(CORPNAME_U)';" \
		$(DBNAME)
	$(call MYSQL_IMPORT,$<,lemgram_index.tsv)
	touch $@

$(CORPNAME)_lemgrams$(TSV): $(CORPNAME)$(VRT)
	$(CAT) $< \
	| egrep -v '<' \
	| gawk -F'	' '{print $$NF}' \
	| tr -d '|' \
	| sort \
	| uniq -c \
	| perl -pe 's/^\s*(\d+)\s*(.*)/$$2\t$$1\t0\t0\t$(CORPNAME_U)/' \
	| $(COMPR) > $@

pkg: $(PKG_FILE)

$(PKG_FILE): $(CORPCORPDIR)/.info $(SQLDUMP)
	-mkdir $(dir $@)
	tar cvjpf $@ $(CORPCORPDIR) $(REGDIR)/$(CORPNAME) $(SQLDUMP)

$(SQLDUMP_NAME): $(DB_TIMESTAMPS)
	-mkdir $(dir $@)
	echo $(CREATE_LEMGRAMS_SQL) > $@
	echo 'DELETE FROM `lemgram_index` where '"corpus='$(CORPNAME_U)';" >> $@
	mysqldump --user $(DBUSER) --no-create-info \
		--where "corpus='$(CORPNAME_U)'" $(DBNAME) lemgram_index >> $@
ifdef DB_HAS_RELS
	mysqldump --user $(DBUSER) $(DBNAME) relations_$(CORPNAME_U) >> $@
endif
