# -*- coding: utf-8 -*-

# Requires GNU Make

# This makefile is typically included in both the top-level Makefile
# of a corpus directory and the makefiles (*.mk) for the individual
# (sub)corpora in a corpus directory.


eq = $(and $(findstring $(1),$(2)),$(findstring $(2),$(1)))
eqs = $(call eq,$(strip $(1)),$(strip $(2)))
lower = $(shell echo $(1) | perl -pe 's/(.*)/\L$$1\E/')

showvars = $(if $(DEBUG),$(foreach var,$(1),$(info $(var) = $($(var)))))

$(call showvars,MAKEFILE_LIST)

TOPDIR = $(dir $(lastword $(MAKEFILE_LIST)))

SCRIPTDIR = $(TOPDIR)/scripts
CORPSRCROOT ?= $(TOPDIR)/../../corp

KORP_SRCDIR = $(TOPDIR)/../src
KORP_CGI = $(KORP_SRCDIR)/backend/korp/korp.cgi

EXTRACT_VALUE = \
	$(or $(shell egrep "^$(2) *= *" $(1) | perl -pe 's/^.*=\s*u?//'),$(3))

SPECIAL_CHARS = $(call EXTRACT_VALUE,$(KORP_CGI),SPECIAL_CHARS," /<>|")
ENCODED_SPECIAL_CHAR_OFFSET = \
	$(call EXTRACT_VALUE,$(KORP_CGI),ENCODED_SPECIAL_CHAR_OFFSET,0x7F)
ENCODED_SPECIAL_CHAR_PREFIX = \
	$(call EXTRACT_VALUE,$(KORP_CGI),ENCODED_SPECIAL_CHAR_PREFIX,"")
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
	$(shell find -name Makefile -o -name \*.mk \
	| egrep '/.*/' | cut -d'/' -f2 | sort -u)

CORPNAME_BASE ?= $(lastword $(subst /, ,$(CURDIR)))
CORPNAME_MAIN ?= $(CORPNAME_BASE)

# CORPORA: The corpora to make with the current makefile. If not
# specified explicitly, all the stems of .mk files in the current
# directory except *-common, *_any and those in IGNORE_CORPORA, or if
# none exists (directory with a single corpus), the name of the
# current directory.
CORPORA ?= $(or $(basename $(filter-out $(addsuffix .mk,\
						%-common %_any \
						$(IGNORE_CORPORA)),\
					$(wildcard *.mk))),\
		$(CORPNAME_BASE))

$(call showvars,SRC_SUBDIR)

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

$(call showvars,\
	WITHIN_CORP_MK CORPNAME_MAIN CORPNAME_BASE \
	SRC_SUBDIR SRC_DIR SRC_FILES \
	CORPORA SRC_FILES_REAL)

DB_TARGETS_ALL = korp_timespans korp_rels korp_lemgrams
DB_HAS_RELS := $(and $(filter dephead,$(P_ATTRS)),$(filter deprel,$(P_ATTRS)))
DB_TARGETS ?= $(if $(DB),$(DB_TARGETS_ALL),\
		korp_timespans \
		$(if $(filter lex,$(P_ATTRS)),\
			korp_lemgrams $(if $(DB_HAS_RELS),korp_rels)))

PARCORP ?= $(LINK_ELEM)

$(call showvars,PARCORP PARCORP_PART)

LANGPAIRS_ALIGN ?= \
	$(foreach lang1,$(LANGUAGES),\
		$(foreach lang2,$(filter-out $(lang1),$(LANGUAGES)),\
			$(lang1)_$(lang2)))

$(call showvars,LANGPAIRS_ALIGN)

EXTRACT_LAST_PART = $(lastword $(subst _, ,$(1)))
EXTRACT_LANG2 = $(call EXTRACT_LAST_PART,$(1))
EXTRACT_LANG1 = \
	$(call EXTRACT_LAST_PART,\
		$(patsubst %_$(call EXTRACT_LAST_PART,$(1)),%,$(1)))
LANGPAIR_LANG1 = $(firstword $(subst _, ,$(1)))
LANGPAIR_LANG2 = $(lastword $(subst _, ,$(1)))

# $(error $(call EXTRACT_LANG1,foo_bar_fi_en) :: $(call EXTRACT_LANG2,foo_bar_fi_en) :: $(call LANGPAIR_LANG1,fi_en) :: $(call LANGPAIR_LANG2,fi_en))

TARGETS ?= $(if $(PARCORP),\
		align pkg-parcorp,\
		subdirs vrt reg $(if $(PARCORP_PART),,pkg) \
			$(if $(strip $(DB_TARGETS)),db))

# Separator between corpus name and a subtarget (vrt, reg, db, pkg ...).
# A : needs to be represented as \: and # as \\\#.
SUBTARGET_SEP = \:

CORPNAME := $(CORPNAME_PREFIX)$(CORPNAME_BASE)$(CORPNAME_SUFFIX)
CORPNAME_U := $(shell echo $(CORPNAME) | perl -pe 's/(.*)/\U$$1\E/')

DEP_MAKEFILES := $(if $(call eqs,$(call lower,$(MAKEFILE_DEPS)),false),,\
			$(MAKEFILE_LIST))

COMPRESSED_SRC ?= $(strip $(if $(filter %.gz,$(SRC_FILES_REAL)),gz,\
			$(if $(or $(filter %.bz2,$(SRC_FILES_REAL)),\
				$(filter %.bz,$(SRC_FILES_REAL))),bz2,\
			none)))
COMPRESS ?= $(or $(COMPRESS_TARGETS),$(COMPRESSED_SRC))

COMPR_EXT_none = 
CAT_none = cat
COMPR_none = cat

COMPR_EXT_gz = .gz
CAT_gz = zcat
COMPR_gz = gzip

COMPR_EXT_bz2 = .bz2
CAT_bz2 = bzcat
COMPR_bz2 = bzip2

COMPR_EXT := $(COMPR_EXT_$(COMPRESS))
CAT := $(CAT_$(COMPRESS))
CAT_SRC := $(CAT_$(COMPRESSED_SRC))
COMPR := $(COMPR_$(COMPRESS))

# Use checksums to check if a file has really changed (for selected
# files), unless IGNORE_CHECKSUMS
CHECKSUM_METHOD ?= md5
CKSUM_EXT := .$(CHECKSUM_METHOD)
CKSUM_EXT_COND := $(if $(IGNORE_CHECKSUMS),,$(CKSUM_EXT))
CHECKSUMMER := $(CHECKSUM_METHOD)sum

VRT = .vrt$(COMPR_EXT)
TSV = .tsv$(COMPR_EXT)
ALIGN = .align$(COMPR_EXT)
SQL = .sql$(COMPR_EXT)
VRT_CKSUM = $(VRT)$(CKSUM_EXT_COND)
TSV_CKSUM = $(TSV)$(CKSUM_EXT_COND)
ALIGN_CKSUM = $(ALIGN)$(CKSUM_EXT_COND)

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

$(call showvars,CORPDIR CORPCORPDIR)

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
	($(CAT) $(1:$(CKSUM_EXT)=) > $(2).tsv &); \
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

# Depend on $(CORPNAME).sattrs only if S_ATTRS has not been defined
# previously (in a corpus makefile)
S_ATTRS_DEP := $(if $(S_ATTRS),,$(CORPNAME).sattrs)

S_ATTRS ?= $(shell cat $(CORPNAME).sattrs)

P_OPTS = $(foreach attr,$(P_ATTRS),-P $(attr))
S_OPTS = $(foreach attr,$(S_ATTRS),-S $(attr))

$(call showvars,P_OPTS S_OPTS)

SQLDUMP_NAME = $(CORPSQLDIR)/$(CORPNAME)$(SQL)
SQLDUMP = $(if $(strip $(DB_TARGETS)),$(SQLDUMP_NAME))

DB_TIMESTAMPS = $(patsubst korp_%,$(CORPNAME)_%_load.timestamp,$(DB_TARGETS))
DB_SQLDUMPS = $(patsubst korp_%,$(CORPSQLDIR)/$(CORPNAME)_%$(SQL),$(DB_TARGETS))

RELS_BASES = @ rel head_rel dep_rel sentences
RELS_TSV = $(subst _@,,$(foreach base,$(RELS_BASES),\
				$(CORPNAME)_rels_$(base)$(TSV)))
RELS_TSV_CKSUM = $(addsuffix $(CKSUM_EXT_COND),$(RELS_TSV))
MAKE_RELS_TABLE_NAME = $(subst $(CORPNAME)_rels,relations_$(CORPNAME_U),\
			$(subst $(TSV_CKSUM),,$(1)))
RELS_TABLES = $(call MAKE_RELS_TABLE_NAME,$(RELS_TSV_CKSUM))

RELS_TRUNCATE_TABLES = $(foreach tbl,$(RELS_TABLES),truncate table $(tbl);)
RELS_DROP_TABLES = $(foreach tbl,$(RELS_TABLES),drop table if exists $(tbl);)
RELS_CREATE_TABLES_TEMPL = $(TOPDIR)/create-relations-tables-templ.sql
RELS_CREATE_TABLES_SQL = $(call SUBST_CORPNAME,$(RELS_CREATE_TABLES_TEMPL))

.PHONY: all-corp all all-override subdirs parcorp \
	$(CORPORA) $(TARGETS) $(SUBDIRS)

.PRECIOUS: %$(VRT) %$(TSV) %$(ALIGN) %$(CKSUM_EXT)


# The following conditional rules specify the main target, depending
# on where this makefile is included: a makefile in an intermediate
# directory with subdirectories, a makefile for a single corpus, or a
# makefile in a directory with multiple subcorpora (and possibly
# subdirectories).

# If $(CORPORA) == $(CORPNAME_BASE), the current directory does not
# have *.mk for subcorpora
ifeq ($(strip $(CORPORA)),$(strip $(CORPNAME_BASE)))

# If SRC_FILES is not defined, this makefile is in an intermediate
# directory with only subdirectories
ifndef SRC_FILES

# If SUBDIRS is empty and if this is not a parallel corpus, SRC_FILES
# probably has been forgotten
ifeq ($(strip $(SUBDIRS)),)
ifeq ($(strip $(PARCORP)),)
$(error Please specify the source files in SRC_FILES)
endif

else # SUBDIRS non-empty

# Make in subdirectories only
TOP_TARGETS = subdirs

endif # SUBDIRS non-empty

else # SRC_FILES defined

# A single corpus: make actual corpus targets
TOP_TARGETS = all

endif # SRC_FILES defined

else # $(CORPORA) == $(CORPNAME_BASE)

# The directory has *.mk for subcorpora and may contain subdirectories
TOP_TARGETS = subdirs $(CORPORA)

endif

$(call showvars,TOP_TARGETS)


all-top: $(TOP_TARGETS)

all: $(TARGETS)

subdirs: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@

.PHONY: all-top $(TOP_TARGETS) all subdirs $(SUBDIRS)


# Define rules for targets $(CORPORA) and $(CORPORA)$(SUBTARGET_SEP)$(TARGET)

define MAKE_CORPUS_R
$(1)$(if $(subst $(SUBTARGET_SEP),,$(2)),$(SUBTARGET_SEP)$(2)):
	$$(MAKE) -f $(1).mk $(or $(TARGET),$(subst $(SUBTARGET_SEP),all,$(2))) \
		CORPNAME_BASE=$(1) DB=$(DB) WITHIN_CORP_MK=1

.PHONY: $(1)$(if $(subst $(SUBTARGET_SEP),,$(2)),$(SUBTARGET_SEP)$(2))
endef

$(foreach corp,$(CORPORA),\
	$(foreach targ,$(TARGETS) $(SUBTARGET_SEP),\
		$(eval $(call MAKE_CORPUS_R,$(corp),$(targ)))))


# Calculate the checksum of a file, compare it to the previous
# checksum (if any) and use the new checksum file if different,
# otherwise use the old one with the old timestamp.
# For some reason, the construct
#   { $(CHECKSUMMER) $< | tee $@.new | cmp -s $@ - ; } \
#   || mv $@.new $@
# produces empty .md5 files in some cases ($(RELS_TSV)) but not in
# others.

%$(CKSUM_EXT): %
	-$(CHECKSUMMER) $< > $@.new
	cmp -s $@ $@.new || mv $@.new $@
	-rm -f $@.new


reg: vrt
	$(CWB_MAKE)

vrt: $(CORPCORPDIR)/.info

.PHONY: reg vrt

# The info file $(CORPCORPDIR)/.info is (ab)used as a timestamp file
# to avoid unnecessarily remaking the corpus data if the .vrt file has
# not changed.

$(CORPCORPDIR)/.info: $(CORPNAME)$(VRT_CKSUM) $(CORPNAME).info $(S_ATTRS_DEP)
	-mkdir $(CORPCORPDIR) || /bin/rm $(CORPCORPDIR)/*
	$(CAT) $(<:$(CKSUM_EXT)=) | $(CWB_ENCODE) $(P_OPTS) $(S_OPTS) \
	&& cp $(CORPNAME).info $(CORPCORPDIR)/.info

%.info: %$(VRT_CKSUM)
	echo "Sentences: "`$(CAT) $(<:$(CKSUM_EXT)=) | egrep -c '^<sentence[> ]'` > $@
	ls -l --time-style=long-iso $(<:$(CKSUM_EXT)=) \
	| perl -ne '/(\d{4}-\d{2}-\d{2})/; print "Updated: $$1\n"' >> $@

%.sattrs: %$(VRT_CKSUM)
	$(CAT) $(<:$(CKSUM_EXT)=) \
	| $(MAKE_CWB_STRUCT_ATTRS) > $@

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
	$(CAT_SRC) $(SRC_FILES_REAL) \
	| $(TRANSCODE) \
	| $(MAKE_VRT_CMD) \
	| $(VRT_FIX_ATTRS) \
	| $(COMPR) > $@
endif
	$(MAKE_VRT_CLEANUP)

db: korp_db

korp_db: $(DB_TARGETS)

korp_rels: $(CORPNAME)_rels_load.timestamp

.PHONY: db korp_db korp_rels


$(CORPNAME)_rels_load.timestamp: $(RELS_TSV_CKSUM) $(RELS_CREATE_TABLES_TEMPL)
	mysql --user $(DBUSER) \
		--execute '$(RELS_DROP_TABLES) $(RELS_CREATE_TABLES_SQL)' \
		$(DBNAME)
	$(foreach rel,$(RELS_TSV_CKSUM),\
		$(call MYSQL_IMPORT,$(rel),$(strip \
			$(call MAKE_RELS_TABLE_NAME,$(rel)))))
	touch $@

$(CORPSQLDIR)/$(CORPNAME)_rels$(SQL): $(CORPNAME)_rels_load.timestamp
	mysqldump --no-autocommit --user $(DBUSER) $(DBNAME) $(RELS_TABLES) \
	| $(COMPR) > $@

$(RELS_TSV): $(CORPNAME)$(VRT_CKSUM) $(MAKE_RELS_DEPS)
	$(CAT) $(<:$(CKSUM_EXT)=) \
	| $(MAKE_RELS_CMD)

define KORP_LOAD_DB_R
korp_$(1): $(CORPNAME)_$(1)_load.timestamp

.PHONY: korp_$(1)

CREATE_SQL_$(1) = '\
	CREATE TABLE IF NOT EXISTS `$$(TABLENAME_$(1))` ( \
		$$(COLUMNS_$(1)) \
	) ENGINE=InnoDB DEFAULT CHARSET=utf8;'

$(CORPNAME)_$(1)_load.timestamp: $(CORPNAME)_$(1)$(TSV_CKSUM)
	mysql --user $(DBUSER) --execute $$(CREATE_SQL_$(1)) $(DBNAME)
	mysql --user $(DBUSER) \
		--execute "delete from $$(TABLENAME_$(1)) where corpus='$(CORPNAME_U)';" \
		$(DBNAME)
	$$(call MYSQL_IMPORT,$$<,$$(TABLENAME_$(1)))
	touch $$@

$(CORPSQLDIR)/$(CORPNAME)_$(1)$(SQL): $(CORPNAME)_$(1)_load.timestamp
	-mkfifo $$@.fifo; \
	{ \
	echo $$(CREATE_SQL_$(1)); \
	echo 'DELETE FROM `$$(TABLENAME_$(1))` where '"corpus='$(CORPNAME_U)';"; \
	mysqldump --no-autocommit --user $(DBUSER) --no-create-info \
		--where "corpus='$(CORPNAME_U)'" $(DBNAME) $$(TABLENAME_$(1)); \
	} > $$@.fifo & \
	$(COMPR) < $$@.fifo > $$@
	-rm $$@.fifo
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

$(CORPNAME)_lemgrams$(TSV): $(CORPNAME)$(VRT_CKSUM)
	$(CAT) $(<:$(CKSUM_EXT)=) \
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

$(CORPNAME)_timespans$(TSV): \
		$(CORPNAME)$(VRT_CKSUM) $(VRT_EXTRACT_TIMESPANS_PROG)
	$(CAT) $(<:$(CKSUM_EXT)=) \
	| $(DECODE_SPECIAL_CHARS) \
	| $(VRT_EXTRACT_TIMESPANS) \
	| gawk -F'	' '{print "$(CORPNAME_U)\t" $$0}' \
	| $(COMPR) > $@

$(eval $(call KORP_LOAD_DB_R,timespans))

pkg: $(PKG_FILE)

$(PKG_FILE): $(CORPCORPDIR)/.info $(DB_SQLDUMPS)
	-mkdir $(dir $@)
	tar cvjpf $@ $(CORPCORPDIR) $(REGDIR)/$(CORPNAME) $(DB_SQLDUMPS)

.PHONY: pkg

# $(SQLDUMP_NAME): $(DB_SQLDUMPS)
# 	-mkdir $(dir $@)
# 	cat $^ > $@


# Align parallel corpora

ALIGN_CORP = \
	$(CWB_REGEDIT) $(CORPNAME)_$(1) :add :a "$(CORPNAME)_$(2)"; \
	align=$(CORPNAME)_$(1)_$(2)$(ALIGN); \
	fifo=$$align.fifo; \
	mkfifo $$fifo; \
	($(CAT) $$align > $$fifo &); \
	$(CWB_ALIGN_ENCODE) -D $$fifo; \
	rm $$fifo

# CHECK: Does this always work correctly when running more than one
# simultaneous job?

# FIXME: When changing some parts of a parallel corpus, the alignments
# do not seem to get encoded.

align: parcorp $(CORPNAME)_aligned.timestamp

.PHONY: align

$(CORPNAME)_aligned.timestamp: \
		$(foreach langpair,$(LANGPAIRS_ALIGN),\
			$(CORPNAME)_$(langpair)$(ALIGN_CKSUM))
	for langpair in $(LANGPAIRS_ALIGN); do \
		lang1=`echo $$langpair | sed -e 's/_.*//'`; \
		lang2=`echo $$langpair | sed -e 's/.*_//'`; \
		$(call ALIGN_CORP,$${lang1},$${lang2}); \
	done
	touch $@

define MAKE_ALIGN_R
$(CORPNAME)_$$(strip $(1))_$$(strip $(2))$(ALIGN): \
		$(CORPDIR)/$(CORPNAME)_$$(strip $(1))/.info
	-mkfifo $$@.fifo
	($(CWB_ALIGN) -o $$@.fifo -r $(REGDIR) -V $(LINK_ELEM)_$(LINK_ATTR) \
		$(CORPNAME)_$$(strip $(1)) $(CORPNAME)_$$(strip $(2)) \
		$(LINK_ELEM) > /dev/null &); \
	$(COMPR) < $$@.fifo > $$@
	-rm $$@.fifo
endef

$(foreach langpair,$(LANGPAIRS_ALIGN),\
	$(eval $(call MAKE_ALIGN_R,$(call LANGPAIR_LANG1,$(langpair)),\
					$(call LANGPAIR_LANG2,$(langpair)))))

MAKE_PARCORP_PARTS = \
	for lang in $(LANGUAGES); do \
		for suffix in _$$lang _any ""; do \
			makefile=$(CORPNAME_MAIN)$$suffix.mk; \
			if test -e $$makefile; then \
				$(MAKE) -f $$makefile $(1) \
					CORPNAME_MAIN="$(CORPNAME)" \
					CORPNAME_BASE="$(CORPNAME)_$$lang" \
					LANGUAGES="$(LANGUAGES)" \
					PARCORP_LANG=$$lang; \
				break; \
			fi; \
		done; \
	done

parcorp:
	$(call MAKE_PARCORP_PARTS,all WITHIN_CORP_MK=1 PARCORP_PART=1)

pkg-parcorp: align
	$(call MAKE_PARCORP_PARTS,pkg)

.PHONY: parcorp pkg-parcorp
