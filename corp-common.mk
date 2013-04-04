# -*- coding: utf-8 -*-

# Requires GNU Make

# This makefile is typically included in both the top-level Makefile
# of a corpus directory and the makefiles (*.mk) for the individual
# (sub)corpora in a corpus directory.


eq = $(and $(findstring $(1),$(2)),$(findstring $(2),$(1)))
eqs = $(call eq,$(strip $(1)),$(strip $(2)))
lower = $(shell echo $(1) | perl -pe 's/(.*)/\L$$1\E/')

TOPDIR = $(dir $(lastword $(MAKEFILE_LIST)))

SCRIPTDIR = $(TOPDIR)/scripts
CORPSRCROOT ?= $(TOPDIR)/../../corp

SPECIAL_CHARS = " /<>"
ENCODED_SPECIAL_CHAR_OFFSET = 0x7F
ENCODED_SPECIAL_CHAR_PREFIX = ""
DECODE_SPECIAL_CHARS = perl -C -e '\
	$$sp_chars = $(SPECIAL_CHARS); \
	%sp_char_map = map {($(ENCODED_SPECIAL_CHAR_PREFIX) \
	                     . chr ($(ENCODED_SPECIAL_CHAR_OFFSET) + $$_)) \
			    => substr ($$sp_chars, $$_, 1)} \
			   (0 .. length ($$sp_chars)); \
	while (<>) \
	{ \
		for $$c (keys (%sp_char_map)) \
		{ \
			s/$$c/$$sp_char_map{$$c}/g; \
		} \
		print; \
	}'

VRT_ADD_LEMGRAMS = $(SCRIPTDIR)/vrt-add-lemgrams.py \
			--pos-map-file $(LEMGRAM_POSMAP) \
			$(VRT_ADD_LEMGRAMS_OPTS)
VRT_FIX_ATTRS_PROG = $(SCRIPTDIR)/vrt-fix-attrs.py
VRT_FIX_ATTRS_OPTS ?= \
	--encode-special-chars=all --special-chars=$(SPECIAL_CHARS) \
	--encoded-special-char-offset=$(ENCODED_SPECIAL_CHAR_OFFSET) \
	--encoded-special-char-prefix=$(ENCODED_SPECIAL_CHAR_PREFIX) \
	$(VRT_FIX_ATTRS_OPTS_EXTRA)
VRT_FIX_ATTRS = $(VRT_FIX_ATTRS_PROG) $(VRT_FIX_ATTRS_OPTS)
XML2VRT = $(SCRIPTDIR)/xml2vrt.py --rule-file $(XML2VRT_RULES) \
		--wrapper-element-name= $(XML2VRT_OPTS)
# xmlstats.py should _not_ have --decode-special-chars as it does not
# work correctly with UTF-8 encoding.
XMLSTATS = $(SCRIPTDIR)/xmlstats.py --wrapper-element-name= \
		--allow-stray-reserved-characters

VRT_EXTRACT_TIMESPANS_PROG = $(SCRIPTDIR)/vrt-extract-timespans.py
VRT_EXTRACT_TIMESPANS_OPTS ?= \
	$(if $(call eq,unknown,$(CORPUS_DATE)),--unknown,\
	$(if $(CORPUS_DATE),--fixed=$(CORPUS_DATE),\
	$(if $(CORPUS_DATE_PATTERN),--pattern=$(CORPUS_DATE_PATTERN))))
VRT_EXTRACT_TIMESPANS = \
	$(VRT_EXTRACT_TIMESPANS_PROG) $(VRT_EXTRACT_TIMESPANS_OPTS)

MAKE_CWB_STRUCT_ATTRS = $(XMLSTATS) --cwb-struct-attrs

SUBDIRS := \
	$(shell ls \
	| perl -ne 'chomp; print "$$_\n" if -d $$_ && -e "$$_/Makefile"')

CORPNAME_BASE ?= $(lastword $(subst /, ,$(CURDIR)))

CORPORA ?= $(or $(basename $(filter-out %-common.mk,$(wildcard *.mk))),\
		$(CORPNAME_BASE))

# The subdirectory of CORPSRCROOT for the corpus source files; can be
# overridden in individual corpus makefiles. WITHIN_CORP_MK is defined
# if this file is included in a CORPUS.mk makefile (and not Makefile).
SRC_SUBDIR ?= $(subst $(abspath $(TOPDIR))/,,$(abspath $(CURDIR)))$(if $(WITHIN_CORP_MK),/$(CORPNAME_BASE))
# The corpus source directory; overrides CORPSRCROOT if defined in a
# corpus makefile
SRC_DIR ?= $(CORPSRCROOT)/$(SRC_SUBDIR)

# SRC_FILES (relative to SRC_DIR) must be defined in a corpus-specific
# makefile. Wildcards in SRC_FILES are expanded, and files specified
# in SRC_FILES_EXCLUDE (relative to SRC_DIR) are excluded.
SRC_FILES_REAL = $(filter-out $(addprefix $(SRC_DIR)/,$(SRC_FILES_EXCLUDE)),\
			$(wildcard $(addprefix $(SRC_DIR)/,$(SRC_FILES))))

# $(info $(WITHIN_CORP_MK) $(CORPNAME_BASE) $(SRC_SUBDIR) $(SRC_DIR) :: $(SRC_FILES_REAL))

DB_TARGETS_ALL = korp_timespans korp_rels korp_lemgrams
DB_HAS_RELS := $(and $(filter dephead,$(P_ATTRS)),$(filter deprel,$(P_ATTRS)))
DB_TARGETS ?= $(if $(DB),$(DB_TARGETS_ALL),\
		korp_timespans \
		$(if $(filter lex,$(P_ATTRS)),\
			korp_lemgrams $(if $(DB_HAS_RELS),korp_rels)))

PARCORP ?= $(LINK_ELEM)
PARLANG1 = $(firstword $(LANGUAGES))
PARLANG2 = $(lastword $(LANGUAGES))
OTHERLANG = $(subst _@,_$(PARLANG1),$(subst _$(PARLANG1),_$(PARLANG2),$(subst _$(PARLANG2),_@,$(1))))

TARGETS ?= $(if $(PARCORP),\
		align pkg-parcorp,\
		subdirs vrt reg $(if $(PARCORP_PART),,pkg) \
			$(if $(strip $(DB_TARGETS)),db))

CORPNAME := $(CORPNAME_PREFIX)$(CORPNAME_BASE)$(CORPNAME_SUFFIX)
CORPNAME_U := $(shell echo $(CORPNAME) | perl -pe 's/(.*)/\U$$1\E/')

DEP_MAKEFILES := $(if $(call eqs,$(call lower,$(MAKEFILE_DEPS)),false),,\
			$(MAKEFILE_LIST))

COMPRESS := $(strip $(if $(filter %.gz,$(SRC_FILES_REAL)),gz,\
		$(if $(or $(filter %.bz2,$(SRC_FILES_REAL)),\
			$(filter %.bz,$(SRC_FILES_REAL))),bz2,\
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

MAKE_VRT_CMD ?= cat

MAKE_VRT_PROG ?= $(if $(call eq,$(MAKE_VRT_CMD),cat),,\
			$(firstword $(MAKE_VRT_CMD)))
MAKE_VRT_DEPS = $(MAKE_VRT_PROG) $(XML2VRT_RULES) $(LEMGRAM_POSMAP) \
		$(MAKE_VRT_DEPS_EXTRA)
MAKE_RELS_PROG ?= $(firstword $(MAKE_RELS_CMD))
MAKE_RELS_DEPS = $(MAKE_RELS_PROG) $(MAKE_RELS_DEPS_EXTRA)

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
CWB_ALIGN = $(CWBDIR)/cwb-align
CWB_ALIGN_ENCODE = $(CWBDIR)/cwb-align-encode -v -r $(REGDIR)
CWB_REGEDIT = cwb-regedit -r $(REGDIR)

# A named pipe created by mkfifo is used to support uncompressing
# compressed input on the fly.

MYSQL_IMPORT = mkfifo $(2).tsv; \
	($(CAT) $(1) > $(2).tsv &); \
	mysql --local-infile --user $(DBUSER) --batch --execute " \
		set autocommit = 0; \
		set unique_checks = 0; \
		load data local infile '$(2).tsv' into table $(2); \
		commit; \
		show count(*) warnings; \
		show warnings;" \
		korp; \
	/bin/rm -f $(2).tsv;

SUBST_CORPNAME = $(shell perl -pe 's/\@CORPNAME\@/$(CORPNAME_U)/g' $(1))

S_ATTRS ?= $(shell $(CAT) $(CORPNAME)$(VRT) | $(MAKE_CWB_STRUCT_ATTRS))

P_OPTS = $(foreach attr,$(P_ATTRS),-P $(attr))
S_OPTS = $(foreach attr,$(S_ATTRS),-S $(attr))

SQLDUMP_NAME = $(CORPSQLDIR)/$(CORPNAME).sql
SQLDUMP = $(if $(strip $(DB_TARGETS)),$(SQLDUMP_NAME))

DB_TIMESTAMPS = $(patsubst korp_%,$(CORPNAME)_%_load.timestamp,$(DB_TARGETS))
DB_SQLDUMPS = $(patsubst korp_%,$(CORPSQLDIR)/$(CORPNAME)_%.sql,$(DB_TARGETS))

RELS_BASES = @ rel head_rel dep_rel sentences
RELS_TSV = $(subst _@,,$(foreach base,$(RELS_BASES),\
				$(CORPNAME)_rels_$(base)$(TSV)))
MAKE_RELS_TABLE_NAME = $(subst $(CORPNAME)_rels,relations_$(CORPNAME_U),\
			$(subst $(TSV),,$(1)))
RELS_TABLES = $(call MAKE_RELS_TABLE_NAME,$(RELS_TSV))

RELS_TRUNCATE_TABLES = $(foreach tbl,$(RELS_TABLES),truncate table $(tbl);)
RELS_DROP_TABLES = $(foreach tbl,$(RELS_TABLES),drop table if exists $(tbl);)
RELS_CREATE_TABLES_TEMPL = $(TOPDIR)/create-relations-tables-templ.sql
RELS_CREATE_TABLES_SQL = $(call SUBST_CORPNAME,$(RELS_CREATE_TABLES_TEMPL))

.PHONY: all-corp all all-override subdirs parcorp \
	$(CORPORA) $(TARGETS) $(SUBDIRS)


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
		CORPNAME_BASE=$(1) DB=$(DB) WITHIN_CORP_MK=1
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
$(CORPNAME)$(VRT): $(SRC_FILES_REAL) $(MAKE_VRT_DEPS) $(VRT_FIX_ATTRS_PROG) \
		$(DEP_MAKEFILES) $(VRT_EXTRA_DEPS)
	$(MAKE_VRT_SETUP)
ifdef MAKE_VRT_FILENAME_ARGS
	$(MAKE_VRT_CMD) $(SRC_FILES_REAL) \
	| $(VRT_FIX_ATTRS) \
	| $(COMPR) > $@
else
	$(CAT) $(SRC_FILES_REAL) \
	| $(TRANSCODE) \
	| $(MAKE_VRT_CMD) \
	| $(VRT_FIX_ATTRS) \
	| $(COMPR) > $@
endif
	$(MAKE_VRT_CLEANUP)

db: korp_db

korp_db: $(DB_TARGETS)

korp_rels: $(CORPNAME)_rels_load.timestamp


$(CORPNAME)_rels_load.timestamp: $(RELS_TSV) $(RELS_CREATE_TABLES_TEMPL)
	mysql --user $(DBUSER) \
		--execute '$(RELS_DROP_TABLES) $(RELS_CREATE_TABLES_SQL)' \
		$(DBNAME)
	$(foreach rel,$(RELS_TSV),\
		$(call MYSQL_IMPORT,$(rel),$(strip \
			$(call MAKE_RELS_TABLE_NAME,$(rel)))))
	touch $@

$(CORPSQLDIR)/$(CORPNAME)_rels.sql: $(CORPNAME)_rels_load.timestamp
	mysqldump --no-autocommit --user $(DBUSER) $(DBNAME) $(RELS_TABLES) > $@

$(RELS_TSV): $(CORPNAME)$(VRT) $(MAKE_RELS_DEPS)
	$(CAT) $< \
	| $(MAKE_RELS_CMD)

define KORP_LOAD_DB_R
korp_$(1): $(CORPNAME)_$(1)_load.timestamp

CREATE_SQL_$(1) = '\
	CREATE TABLE IF NOT EXISTS `$$(TABLENAME_$(1))` ( \
		$$(COLUMNS_$(1)) \
	) ENGINE=InnoDB DEFAULT CHARSET=utf8;'

$(CORPNAME)_$(1)_load.timestamp: $(CORPNAME)_$(1)$(TSV)
	mysql --user $(DBUSER) --execute $$(CREATE_SQL_$(1)) $(DBNAME)
	mysql --user $(DBUSER) \
		--execute "delete from $$(TABLENAME_$(1)) where corpus='$(CORPNAME_U)';" \
		$(DBNAME)
	$$(call MYSQL_IMPORT,$$<,$$(TABLENAME_$(1)))
	touch $$@

$(CORPSQLDIR)/$(CORPNAME)_$(1).sql: $(CORPNAME)_$(1)_load.timestamp
	echo $$(CREATE_SQL_$(1)) > $$@
	echo 'DELETE FROM `$$(TABLENAME_$(1))` where '"corpus='$(CORPNAME_U)';" >> $$@
	mysqldump --no-autocommit --user $(DBUSER) --no-create-info \
		--where "corpus='$(CORPNAME_U)'" $(DBNAME) $$(TABLENAME_$(1)) \
		>> $$@
endef

TABLENAME_lemgrams = lemgram_index
COLUMNS_lemgrams = \
	`lemgram` varchar(64) NOT NULL, \
	`freq` int(11) DEFAULT NULL, \
	`freqprefix` int(11) DEFAULT NULL, \
	`freqsuffix` int(11) DEFAULT NULL, \
	`corpus` varchar(64) NOT NULL, \
	UNIQUE KEY `lemgram_corpus` (`lemgram`, `corpus`), \
	KEY `lemgram` (`lemgram`), \
	KEY `corpus` (`corpus`)

$(eval $(call KORP_LOAD_DB_R,lemgrams))

$(CORPNAME)_lemgrams$(TSV): $(CORPNAME)$(VRT)
	$(CAT) $< \
	| egrep -v '<' \
	| gawk -F'	' '{print $$NF}' \
	| tr '|' '\n' \
	| egrep -v '^$$' \
	| $(DECODE_SPECIAL_CHARS) \
	| sort \
	| uniq -c \
	| perl -pe 's/^\s*(\d+)\s*(.*)/$$2\t$$1\t0\t0\t$(CORPNAME_U)/' \
	| $(COMPR) > $@

TABLENAME_timespans = timespans
COLUMNS_timespans = \
	`corpus` varchar(64) NOT NULL, \
	`datefrom` varchar(14) DEFAULT '"''"', \
	`dateto` varchar(14) DEFAULT '"''"', \
	`tokens` int(11) DEFAULT 0, \
	KEY `corpus` (`corpus`)

$(CORPNAME)_timespans$(TSV): $(CORPNAME)$(VRT) $(VRT_EXTRACT_TIMESPANS_PROG)
	$(CAT) $< \
	| $(DECODE_SPECIAL_CHARS) \
	| $(VRT_EXTRACT_TIMESPANS) \
	| gawk -F'	' '{print "$(CORPNAME_U)\t" $$0}' \
	| $(COMPR) > $@

$(eval $(call KORP_LOAD_DB_R,timespans))

pkg: $(PKG_FILE)

$(PKG_FILE): $(CORPCORPDIR)/.info $(DB_SQLDUMPS)
	-mkdir $(dir $@)
	tar cvjpf $@ $(CORPCORPDIR) $(REGDIR)/$(CORPNAME) $(DB_SQLDUMPS)

# $(SQLDUMP_NAME): $(DB_SQLDUMPS)
# 	-mkdir $(dir $@)
# 	cat $^ > $@


# Align parallel corpora

ALIGN_CORP = \
		$(CWB_REGEDIT) $(1) :add :a "$(call OTHERLANG,$(1))"; \
		$(CWB_ALIGN_ENCODE) -D $(1).align

align: parcorp $(CORPNAME)_$(PARLANG1).align $(CORPNAME)_$(PARLANG2).align
	$(call ALIGN_CORP,$(CORPNAME)_$(PARLANG1))
	$(call ALIGN_CORP,$(CORPNAME)_$(PARLANG2))

%.align: $(CORPDIR)/%/.info
	$(CWB_ALIGN) -o $@ -r $(REGDIR) -V $(LINK_ELEM)_$(LINK_ATTR) \
		$(basename $@) $(basename $(call OTHERLANG,$@)) $(LINK_ELEM)

parcorp:
	for lang in $(LANGUAGES); do \
		$(MAKE) -f $(CORPNAME)_$$lang.mk all \
			CORPNAME_BASE=$(CORPNAME)_$$lang WITHIN_CORP_MK=1; \
	done

pkg-parcorp:
	for lang in $(LANGUAGES); do \
		$(MAKE) -f $(CORPNAME)_$$lang.mk pkg \
			CORPNAME_BASE=$(CORPNAME)_$$lang; \
	done
