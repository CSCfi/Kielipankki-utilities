# -*- coding: utf-8 -*-

# Requires GNU Make

# This makefile is typically included in both the top-level Makefile
# of a corpus directory and the makefiles (*.mk) for the individual
# (sub)corpora in a corpus directory.


eq = $(and $(findstring $(1),$(2)),$(findstring $(2),$(1)))
eqs = $(call eq,$(strip $(1)),$(strip $(2)))
not = $(if $(1),,1)
lower = $(shell echo $(1) | perl -pe 's/(.*)/\L$$1\E/')

showvars = $(if $(DEBUG),$(foreach var,$(1),$(info $(var) = "$($(var))")))
debuginfo = $(if $(DEBUG),$(info *** DEBUG: $(1) ***))


# The corpus has subcorpora if SUBCORPORA has been defined but not
# SUBCORPUS (which would indicate this is a subcorpus).
HAS_SUBCORPORA = $(and $(or $(SUBCORPORA),$(SUBDIRS_AS_SUBCORPORA)),\
			$(call not,$(SUBCORPUS)))

# NOTE: We cannot use the variable name LANGUAGE since that controls
# the language of Make messages, so  we use PARCORP_LANG instead.

# Functions for handling variables with possibly language-specific
# values in parallel corpora or subcorpus-specific values.
# Note: The functions do not work with user-defined functions
# (variables with arguments).

# Prefix values with $(defined_mark) so that also empty defined values
# take precedence over the default value.
defined_mark = !*!DEFINED!*!
defined_val = $(if $(call eq,$(origin $(1)),undefined),,$(defined_mark)$($(1)))

# Return a possibly language-specific value for variable VAR: the
# first one of VAR_$(PARCORP_LANG), VAR_other or VAR.
langvar_val = \
	$(or $(call defined_val,$(1)_$(PARCORP_LANG)),\
	     $(call defined_val,$(1)_other),\
	     $(call defined_val,$(1)))

# An auxiliary function for partvar_defined_or_default
partvar_defined_or_default_aux = \
	$(or $(if $(SUBCORPUS),$(call $(1),$(2)_$(SUBCORPUS))),\
	     $(call $(1),$(2)),\
	     $(3))

# In a subcorpus that is a parallel corpus part, for a variable VAR,
# return the value of the first defined one of
# VAR_$(SUBCORPUS)_$(PARCORP_LANG), VAR_$(SUBCORPUS)_other,
# VAR_$(SUBCORPUS), VAR_$(PARCORP_LANG), VAR_other or VAR, or the
# default argument. If not a subcorpus or a parallel corpus part, skip
# the non-relevant alternatives. The returned value is prefixed
# $(defined_mark) if the value was defined. (TODO: Should we also have
# a default for subcorpora, like _other for languages?)
partvar_defined_or_default = \
	$(if $(PARCORP_LANG),\
	     $(call partvar_defined_or_default_aux,langvar_val,$(1),$(2)),\
	     $(call partvar_defined_or_default_aux,defined_val,$(1),$(2)))

# Return $(defined_mark) if a variant of the argument variable was is
# defined
partvar_defined = \
	$(findstring $(defined_mark),$(call partvar_defined_or_default,$(1)))

# Strip $(defined_mark) and leading and trailing spaces
partvar_or_default = $(strip \
	$(subst $(defined_mark),,$(call partvar_defined_or_default,$(1),$(2))))

# Default to the empty string
partvar = $(call partvar_or_default,$(1))


$(call showvars,MAKEFILE_LIST)

TOPDIR = $(dir $(lastword $(MAKEFILE_LIST)))

SCRIPTDIR = $(TOPDIR)/../scripts

# Run a Python script that may use the modules in $(SCRIPTDIR)
RUN_PYTHON = /usr/bin/env PYTHONPATH=$(SCRIPTDIR) python

CORPROOT_ALTS = \
	/v/corpora /proj/clarin/korp/corpora $(WRKDIR)/corpora \
	/wrk/jyniemi/corpora

# Root directory for various corpus files
CORPROOT ?= $(firstword $(wildcard $(CORPROOT_ALTS)))

# Root directory for default corpus source files
CORPSRCROOT := $(call partvar_or_default,CORPSRCROOT,\
		$(CORPROOT)/src)

ifdef SUBDIRS_AS_SUBCORPORA
SUBCORPORA := $(shell ls -l $(CORPSRCROOT)/$(SRC_SUBDIR) | grep '^d' \
		| awk '{print $$NF}')
endif

FULLTEXTROOT ?= $(CORPROOT)/fulltext
FULLTEXTROOT_SRCDIR ?= $(TOPDIR)/../fulltext

# The following makes assumptions on the location of the Korp backend
# repository; could it be made more flexible?
KORP_BACKEND_DIR := $(TOPDIR)/../../korp-backend/
KORP_CONFIG := \
	$(shell ls $(KORP_BACKEND_DIR)/korp_config.py $(KORP_BACKEND_DIR)/korp.cgi | head -1)

EXTRACT_VALUE = \
	$(or $(shell egrep "^$(2) *= *" $(1) | perl -pe 's/^.*=\s*u?//'),$(3))

SPECIAL_CHARS = $(call EXTRACT_VALUE,$(KORP_CONFIG),SPECIAL_CHARS," /<>|")
ENCODED_SPECIAL_CHAR_OFFSET = \
	$(call EXTRACT_VALUE,$(KORP_CONFIG),ENCODED_SPECIAL_CHAR_OFFSET,0x7F)
ENCODED_SPECIAL_CHAR_PREFIX = \
	$(call EXTRACT_VALUE,$(KORP_CONFIG),ENCODED_SPECIAL_CHAR_PREFIX,"")
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

P_ATTRS := $(call partvar,P_ATTRS)
P_ATTR_FIELDS := word $(P_ATTRS)

index = $(or $(strip $(foreach wnum,1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16,\
			$(if $(call eqs,$(1),$(word $(wnum),$(2))),\
				$(wnum)))),\
		$(3))

CORPUS_HAS_DEPRELS := \
	$(and $(filter dephead,$(P_ATTRS)),$(filter deprel,$(P_ATTRS)))

LEMGRAM_POSMAP := $(call partvar,LEMGRAM_POSMAP)
VRT_ADD_LEMGRAMS := \
	$(if $(strip $(LEMGRAM_POSMAP)),\
		$(SCRIPTDIR)/vrt-add-lemgrams.py \
			--pos-map-file $(call partvar,LEMGRAM_POSMAP) \
			$(call partvar_or_default,VRT_ADD_LEMGRAMS_OPTS,\
				--lemma-field $(call index,lemma,$(P_ATTR_FIELDS),2) \
				--pos-field $(call index,pos,$(P_ATTR_FIELDS),3)),\
		cat)
VRT_FIX_ATTRS_PROG = $(SCRIPTDIR)/vrt-fix-attrs.py
S_ATTRS_FEATSET := $(call partvar,S_ATTRS_FEATSET)

VRT_FIX_ATTRS_OPTS := \
	$(call partvar_or_default,VRT_FIX_ATTRS_OPTS,\
		--encode-special-chars=all --special-chars=$(SPECIAL_CHARS) \
		--encoded-special-char-offset=$(ENCODED_SPECIAL_CHAR_OFFSET) \
		--encoded-special-char-prefix=$(ENCODED_SPECIAL_CHAR_PREFIX) \
		--replace-xml-character-entities=correct \
		$(if $(S_ATTRS_FEATSET),\
			--set-struct-attributes $(S_ATTRS_FEATSET)) \
		$(call partvar,VRT_FIX_ATTRS_OPTS_EXTRA))
VRT_FIX_ATTRS = $(VRT_FIX_ATTRS_PROG) $(VRT_FIX_ATTRS_OPTS)
XML2VRT = $(SCRIPTDIR)/xml2vrt.py --rule-file $(call partvar,XML2VRT_RULES) \
		--wrapper-element-name= $(call partvar,XML2VRT_OPTS)
# xmlstats.py should _not_ have --decode-special-chars as it does not
# work correctly with UTF-8 encoding.
XMLSTATS = $(SCRIPTDIR)/xmlstats.py --wrapper-element-name= \
		--allow-stray-reserved-characters

$(call showvars,LEMGRAM_POSMAP S_ATTRS_FEATSET VRT_FIX_ATTRS_OPTS)

VRT_EXTRACT_TIMESPANS_PROG = $(SCRIPTDIR)/vrt-extract-timespans.py
CORPUS_DATE := $(call partvar,CORPUS_DATE)
CORPUS_DATE_PATTERN := $(call partvar,CORPUS_DATE_PATTERN)
CORPUS_DATE_RANGES := $(call partvar,CORPUS_DATE_RANGES)
CORPUS_DATE_FULL_ORDER := $(call partvar,CORPUS_DATE_FULL_ORDER)
VRT_EXTRACT_TIMESPANS_OPTS_EXTRA := \
	$(call partvar,VRT_EXTRACT_TIMESPANS_OPTS_EXTRA)
VRT_EXTRACT_TIMESPANS_OPTS := \
	$(call partvar_or_default,VRT_EXTRACT_TIMESPANS_OPTS,\
		$(if $(call eqs,unknown,$(CORPUS_DATE)),--unknown,\
		$(if $(CORPUS_DATE),--fixed=$(CORPUS_DATE),\
		$(if $(CORPUS_DATE_PATTERN),--pattern=$(CORPUS_DATE_PATTERN)))) \
		$(if $(CORPUS_DATE_RANGES),--ranges) \
		$(if $(CORPUS_DATE_FULL_ORDER),\
			--full-dates --full-date-order=$(CORPUS_DATE_FULL_ORDER)) \
			$(VRT_EXTRACT_TIMESPANS_OPTS_EXTRA))
VRT_EXTRACT_TIMESPANS = \
	$(VRT_EXTRACT_TIMESPANS_PROG) \
		--mode=add+extract --timespans-prefix=$(CORPNAME_U) \
		--timespans-output-file=$(CORPNAME_BUILDDIR)_timespans$(TSV) \
		--output-full-dates=always \
		$(VRT_EXTRACT_TIMESPANS_OPTS)

MAKE_CWB_STRUCT_ATTRS = $(XMLSTATS) --cwb-struct-attrs

CWBDATA_EXTRACT_INFO_OPTS := $(call partvar,CWBDATA_EXTRACT_INFO_OPTS)
CWBDATA_EXTRACT_INFO = $(SCRIPTDIR)/cwbdata-extract-info.sh \
			--registry "$(REGDIR)" $(CWBDATA_EXTRACT_INFO_OPTS)

CONVERT_TIMEDATA = \
	$(SCRIPTDIR)/korp-convert-timedata.sh \
		--convert all --tsv-dir $(CORP_BUILDDIR)

PKG_DB_FORMAT ?= tsv

# Load data into the Korp MySQL database only if LOAD_DB is non-empty;
# by default, do not load.
LOAD_DB ?=

MAKE_CORPUS_PKG_OPTS := $(call partvar,MAKE_CORPUS_PKG_OPTS)
MAKE_CORPUS_PKG = $(SCRIPTDIR)/korp-make-corpus-package.sh \
			--corpus-root $(CORPROOT) --registry "$(REGDIR)" \
			--compress $(COMPR_PROG) \
			--database-format $(PKG_DB_FORMAT) \
			--tsv-dir "$(CORPROOT)/vrt/{corpid}" \
			$(MAKE_CORPUS_PKG_OPTS)

SUBDIRS := \
	$(shell find -name Makefile -o -name \*.mk \
	| egrep '/.*/' | cut -d'/' -f2 | sort -u)

CORPNAME_BASE := $(call partvar_or_default,CORPNAME_BASE,\
			$(lastword $(subst /, ,$(CURDIR))))
CORPNAME_MAIN := $(call partvar_or_default,CORPNAME_MAIN,\
			$(CORPNAME_BASE))
# Corpus base name without prefixes, suffixes or subcorpus name
CORPNAME_BASEBASE := \
	$(call partvar_or_default,CORPNAME_BASEBASE,\
		$(or $(CORPNAME_BASEBASE),$(CORPNAME_BASE)))

CORPNAME := $(call partvar,CORPNAME_PREFIX)$(CORPNAME_BASE)$(call partvar,CORPNAME_SUFFIX)
CORPNAME_U := $(shell echo $(CORPNAME) | perl -pe 's/(.*)/\U$$1\E/')

# CORPORA: The corpora to make with the current makefile. If not
# specified explicitly, all the stems of .mk files in the current
# directory except *-common, *_any and those in IGNORE_CORPORA, or if
# none exists (directory with a single corpus), the name of the
# current directory.
CORPORA ?= $(or $(basename $(filter-out $(addsuffix .mk,\
						%-common %_any \
						$(call partvar,IGNORE_CORPORA)),\
					$(wildcard *.mk))),\
		$(CORPNAME_BASE))

$(call showvars,SRC_SUBDIR)

WITHIN_CORP_MK := $(filter %.mk,$(firstword $(MAKEFILE_LIST)))

CORPDIR = $(CORPROOT)/data
CORPCORPDIR = $(CORPDIR)/$(CORPNAME)
REGDIR = $(CORPROOT)/registry
CORPSQLDIR = $(CORPROOT)/sql
# Directory for various built files: VRT, TSV, timestamps
CORP_BUILDDIR = $(CORPROOT)/vrt/$(CORPNAME)

$(call showvars,CORPNAME CORPNAME_U CORPROOT CORPDIR CORPCORPDIR CORP_BUILDDIR)

# The subdirectory of CORPSRCROOT for the corpus source files; can be
# overridden in individual corpus makefiles. WITHIN_CORP_MK is defined
# if this file is included in a CORPUS.mk makefile (and not Makefile).
SRC_SUBDIR := \
	$(call partvar_or_default,SRC_SUBDIR,\
		$(subst $(abspath $(TOPDIR))/,,$(abspath $(CURDIR)))$(if $(WITHIN_CORP_MK),/$(CORPNAME_BASE)))
# The corpus source directory; overrides CORPSRCROOT if defined in a
# corpus makefile
SRC_DIR := $(call partvar_or_default,SRC_DIR,$(CORPSRCROOT)/$(SRC_SUBDIR))

SRC_FILES := $(call partvar,SRC_FILES)

SRC_FILES_GENERATED := $(call partvar,SRC_FILES_GENERATED)

SRC_FILES_LS_OPTS := $(call partvar_or_default,SRC_FILE_LS_OPTS,-v)

# List all the files sorted together. It might sometimes be desirable
# to list the files of each file specification (possibly with
# wildcards) separately, so maybe we should have a variable to control
# the behaviour.
list_files = \
	$(shell ls $(SRC_FILES_LS_OPTS) $(1) $(if $(DEBUG),,2> /dev/null))

# SRC_FILES (relative to SRC_DIR) must be defined in a corpus-specific
# makefile. Wildcards in SRC_FILES are expanded, and files specified
# in SRC_FILES_EXCLUDE (relative to SRC_DIR) are excluded.
# SRC_FILES_GENERATED is appended, if any. NOTE: SRC_FILES_GENERATED
# does not support wildcards
SRC_FILES_REAL := \
	$(if $(SRC_FILES),\
		$(filter-out \
			$(addprefix $(SRC_DIR)/,\
				$(call partvar,SRC_FILES_EXCLUDE)),\
			$(call list_files,\
				$(addprefix $(SRC_DIR)/,$(SRC_FILES))))) \
	$(addprefix $(CORP_BUILDDIR)/,$(SRC_FILES_GENERATED))


FULLTEXT_SUBDIR := $(call partvar_or_default,FULLTEXT_SUBDIR,$(CORPNAME_MAIN))
FULLTEXT_DIR := $(call partvar_or_default,FULLTEXT_DIR,\
			$(FULLTEXTROOT)/$(FULLTEXT_SUBDIR))

# TODO: Add support for multiple fulltext versions (formats) of the
# same text, probably by using suffixed versions of the appropriate
# variables (FULLTEXT_FILENAME_TEMPLATE, FULLTEXT_XSLT,
# MAKE_FULLTEXT_CMD and maybe others) and a variable like
# FULLTEXT_VERSIONS listing the suffxes.

VRT_MAKE_FULLTEXT_PROG = $(SCRIPTDIR)/vrt-transform.py
VRT_MAKE_FULLTEXT = \
	$(VRT_MAKE_FULLTEXT_PROG) \
		--pos-attrs 'word $(P_ATTRS)' \
		--output-filename-template \
			'$(FULLTEXT_DIR)/$(FULLTEXT_FILENAME_TEMPLATE)' \
		$(if $(FULLTEXT_XSLT),--xslt-stylesheet $(FULLTEXT_XSLT))
MAKE_FULLTEXT_CMD := \
	$(call partvar_or_default,MAKE_FULLTEXT_CMD,\
		$(VRT_MAKE_FULLTEXT))

$(call showvars,\
	CORPORA WITHIN_CORP_MK CORPNAME CORPNAME_MAIN CORPNAME_BASE \
	CORPNAME_BASEBASE SUBDIRS \
	SRC_SUBDIR SRC_DIR SRC_FILES SRC_FILES_GENERATED SRC_FILES_REAL \
	SUBDIRS_AS_SUBCORPORA SUBCORPORA HAS_SUBCORPORA SUBCORPUS \
	FULLTEXTROOT FULLTEXTROOT_SRCDIR FULLTEXT_SUBDIR FULLTEXT_DIR)

DB_TARGETS_ALL = korp_timespans korp_rels korp_lemgrams
DB_TARGETS := \
	$(call partvar_or_default,DB_TARGETS,\
		$(if $(DB),$(DB_TARGETS_ALL),\
			korp_timespans \
			$(if $(filter lex lex/,$(P_ATTRS)),\
				korp_lemgrams \
				$(if $(CORPUS_HAS_DEPRELS),korp_rels))))

$(call showvars,DB DB_TARGETS)

$(call showvars,PARCORP PARCORP_PART PARCORP_LANG LINK_ELEM)

PARCORP := $(call partvar_or_default,PARCORP,\
		$(and $(call partvar,LINK_ELEM),$(call not,$(PARCORP_PART))))

# The full names (including the corpus base name) of all subcorpora,
# including the languages of aligned corpora. If the corpus has no
# subcorpora nor aligned corpora and the corpus is not itself such,
# the value is simply $(CORPNAME_BASE).
# TODO: If possible, take into account that subcorpora may have
# different aligned languages.
SUBCORPORA_ALL := $(strip \
	$(if $(or $(PARCORP_PART),$(SUBCORPUS)),\
		,\
		$(if $(PARCORP),\
			$(if $(SUBCORPORA),\
				$(foreach subcorp,$(SUBCORPORA),\
					$(foreach lang,$(LANGUAGES),\
						$(CORPNAME_BASEBASE)_$(subcorp)_$(lang))),\
				$(addprefix $(CORPNAME_BASEBASE)_,$(LANGUAGES))),\
			$(if $(SUBCORPORA),\
				$(addprefix $(CORPNAME_BASEBASE)_,$(SUBCORPORA)),\
				$(CORPNAME_BASE)))))

$(call showvars,PARCORP PARCORP_PART SUBCORPORA_ALL)

LANGPAIRS_ALIGN := \
	$(call partvar_or_default,LANGPAIRS_ALIGN,\
		$(foreach lang1,$(LANGUAGES),\
			$(foreach lang2,$(filter-out $(lang1),$(LANGUAGES)),\
				$(lang1)_$(lang2))))

$(call showvars,LANGPAIRS_ALIGN)

EXTRACT_LAST_PART = $(lastword $(subst _, ,$(1)))
EXTRACT_LANG2 = $(call EXTRACT_LAST_PART,$(1))
EXTRACT_LANG1 = \
	$(call EXTRACT_LAST_PART,\
		$(patsubst %_$(call EXTRACT_LAST_PART,$(1)),%,$(1)))
LANGPAIR_LANG1 = $(firstword $(subst _, ,$(1)))
LANGPAIR_LANG2 = $(lastword $(subst _, ,$(1)))

# $(error $(call EXTRACT_LANG1,foo_bar_fi_en) :: $(call EXTRACT_LANG2,foo_bar_fi_en) :: $(call LANGPAIR_LANG1,fi_en) :: $(call LANGPAIR_LANG2,fi_en))

TARGETS := \
	$(call partvar_or_default,TARGETS,\
		$(if $(PARCORP),\
			align pkg,\
			subdirs vrt reg timedata \
				$(if $(and $(or $(PARCORP_PART),$(SUBCORPUS)),\
					$(call not,$(MAKE_PKG))),,pkg) \
				$(if $(strip $(DB_TARGETS)),db) \
				$(if $(strip $(FULLTEXT_FILENAME_TEMPLATE)),fulltext)))

# Separator between corpus name and a subtarget (vrt, reg, db, pkg ...).
# A : needs to be represented as \: and # as \\\#.
SUBTARGET_SEP = \:

DEP_MAKEFILES := $(if $(call eqs,$(call lower,$(MAKEFILE_DEPS)),false),,\
			$(MAKEFILE_LIST))

COMPRESSED_SRC ?= $(strip $(if $(filter %.gz,$(SRC_FILES_REAL)),gz,\
			$(if $(or $(filter %.bz2,$(SRC_FILES_REAL)),\
				$(filter %.bz,$(SRC_FILES_REAL))),bz2,\
			none)))
COMPRESS ?= $(or $(COMPRESS_TARGETS),$(COMPRESSED_SRC))

COMPR_EXT_none = 
COMPR_TAR_EXT_none = .tar
CAT_none = cat
COMPR_PROG_none = cat

COMPR_EXT_gz = .gz
COMPR_TAR_EXT_gz = .tgz
CAT_gz = zcat
COMPR_PROG_gz = gzip
COMPR_OPTS_gz = --no-name

COMPR_EXT_bz2 = .bz2
COMPR_TAR_EXT_bz2 = .tbz
CAT_bz2 = bzcat
COMPR_PROG_bz2 = bzip2

COMPR_EXT := $(COMPR_EXT_$(COMPRESS))
COMPR_TAR_EXT = $(COMPR_TAR_EXT_$(COMPRESS))
CAT := $(CAT_$(COMPRESS))
CAT_SRC := $(CAT_$(COMPRESSED_SRC))
COMPR_PROG := $(COMPR_PROG_$(COMPRESS))
COMPR := $(COMPR_PROG_$(COMPRESS)) $(COMPR_OPTS_$(COMPRESS))

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

INPUT_ENCODING := $(call partvar,INPUT_ENCODING)
TRANSCODE := $(if $(INPUT_ENCODING),iconv -f$(INPUT_ENCODING) -tutf8,cat)

DBUSER = korp
DBNAME = korp
# Unix group for CWB corpus files
CORPGROUP = korp

CWBDIR_ALTS = \
	/usr/local/cwb/bin /usr/local/bin /proj/clarin/korp/cwb/bin \
        $(USERAPPL)/bin /v/util/cwb/utils

# Choose the first directory (if any) containing cwb-encode
CWBDIR ?= \
	$(dir $(firstword $(wildcard $(addsuffix /cwb-encode,$(CWBDIR_ALTS)))))

$(call showvars,CWBDIR)

PKGNAME_BASE ?= $(CORPNAME_BASE)
PKGDIR ?= $(CORPROOT)/pkgs
PKG_FILE := \
	$(or \
		$(shell ls -t $(PKGDIR)/$(PKGNAME_BASE)/$(PKGNAME_BASE)_korp_* \
			$(if $(DEBUG),,2> /dev/null) | head -1),\
		$(PKGDIR)/$(PKGNAME_BASE)/$(PKGNAME_BASE)_korp_$(shell date '+%Y%m%d')$(COMPR_TAR_EXT))

$(call showvars,PKGNAME_BASE PKGDIR PKG_FILE)

# Corpus name prefixed with the build directory
CORPNAME_BUILDDIR = $(CORP_BUILDDIR)/$(CORPNAME)
# Corpus VRT file
CORP_VRT = $(CORPNAME_BUILDDIR)$(VRT)
# Corpus VRT checksum file
CORP_VRT_CKSUM = $(CORPNAME_BUILDDIR)$(VRT_CKSUM)

CWB_ENCODE = $(CWBDIR)/cwb-encode -d $(CORPCORPDIR) -R $(REGDIR)/$(CORPNAME) \
		-xsB -c utf8
CWB_MAKE = $(SCRIPTDIR)/cwb-make-safe \
		-r $(REGDIR) -g $(CORPGROUP) -M 2000 $(CORPNAME_U)
CWB_ALIGN = $(CWBDIR)/cwb-align
CWB_ALIGN_ENCODE = $(CWBDIR)/cwb-align-encode -v -r $(REGDIR)
CWB_REGEDIT = cwb-regedit -r $(REGDIR)

MAKE_VRT_CMD := $(call partvar_or_default,MAKE_VRT_CMD,cat)

MAKE_VRT_PROG := \
	$(call partvar_or_default,MAKE_VRT_PROG,\
		$(if $(call eq,$(MAKE_VRT_CMD),cat),,\
			$(firstword $(MAKE_VRT_CMD))))
MAKE_VRT_DEPS = $(MAKE_VRT_PROG) $(call partvar,XML2VRT_RULES) \
		$(call partvar,LEMGRAM_POSMAP) \
		$(call partvar,MAKE_VRT_DEPS_EXTRA)

MAKE_VRT_SETUP := $(call partvar,MAKE_VRT_SETUP)
MAKE_VRT_CLEANUP := $(call partvar,MAKE_VRT_CLEANUP)

WORDPICT_RELMAP := $(call partvar,WORDPICT_RELMAP)
MAKE_RELS_OPTS_EXTRA := $(call partvar,MAKE_RELS_OPTS_EXTRA)
MAKE_RELS_OPTS := \
	$(call partvar_or_default,MAKE_RELS_OPTS,\
		--sort --output-type=new-strings \
		--word-form-pair-type=baseform \
		$(MAKE_RELS_OPTS_EXTRA))
MAKE_RELS_CMD := \
	$(call partvar_or_default,MAKE_RELS_CMD,\
		$(if $(CORPUS_HAS_DEPRELS),\
			$(SCRIPTDIR)/vrt-extract-relations.py \
				--input-fields="$(P_ATTR_FIELDS)" \
				--output-prefix=$(CORPNAME_BUILDDIR)_rels \
				--compress=$(COMPRESS) \
				$(if $(WORDPICT_RELMAP),--relation-map $(WORDPICT_RELMAP)) \
				$(MAKE_RELS_OPTS)))
MAKE_RELS_PROG := \
	$(call partvar_or_default,MAKE_RELS_PROG,\
		$(firstword $(MAKE_RELS_CMD)))
MAKE_RELS_DEPS = \
	$(MAKE_RELS_PROG) \
	$(call partvar,MAKE_RELS_DEPS_EXTRA) \
	$(WORDPICT_RELMAP)

# A named pipe created by mkfifo is used to support uncompressing
# compressed input on the fly.

MYSQL_IMPORT = mkfifo $(2).tsv; \
	($(CAT) $(1:$(CKSUM_EXT)=) > $(2).tsv &); \
	mysql --local-infile --user $(DBUSER) --batch --execute " \
		set autocommit = 0; \
		set unique_checks = 0; \
		load data local infile '$(2).tsv' into table $(2) fields escaped by ''; \
		commit; \
		show count(*) warnings; \
		show warnings;" \
		korp; \
	/bin/rm -f $(2).tsv;

SUBST_CORPNAME = $(shell perl -pe 's/\@CORPNAME\@/$(CORPNAME_U)/g' $(1))

# File containing structural attribute declaration in a format
# suitable for cwb-encode
SATTRS_FILE = $(CORPNAME_BUILDDIR).sattrs

# Depend on $(SATTRS_FILE) only if S_ATTRS has not been defined
# previously (in a corpus makefile)
ifeq ($(strip $(call partvar_defined,S_ATTRS)),)
S_ATTRS_DEP := $(if $(call partvar,S_ATTRS),,$(SATTRS_FILE))
# Here S_ATTRS should be a recursively expanded variable as its value
# is defined correctly only after making $(SATTRS_FILE).
S_ATTRS = $(shell cat $(SATTRS_FILE))
else
S_ATTRS_DEP := 
# Here S_ATTRS should be a simply expanded variable in order to avoid
# a recursive reference in partvar.
S_ATTRS := $(call partvar,S_ATTRS)
endif

P_OPTS = $(foreach attr,$(P_ATTRS),-P $(attr))
S_OPTS = $(foreach attr,$(S_ATTRS),-S $(attr))

$(call showvars,P_OPTS S_OPTS)

DB_TIMESTAMPS = $(patsubst korp_%,$(CORPNAME_BUILDDIR)_%_load.timestamp,\
			$(DB_TARGETS))
DB_SQLDUMPS = $(patsubst korp_%,$(CORPSQLDIR)/$(CORPNAME)_%$(SQL),$(DB_TARGETS))

ifeq ($(strip $(PARCORP)$(HAS_SUBCORPORA)),)
ifeq ($(strip $(PKG_DB_FORMAT)),sql)
TARGETS := $(TARGETS) sql
endif
endif

$(call showvars,DB_TIMESTAMPS DB_SQLDUMPS)

RELS_BASES = @ rel head_rel dep_rel sentences
RELS_TSV = $(subst _@,,$(foreach base,$(RELS_BASES),\
				$(CORPNAME_BUILDDIR)_rels_$(base)$(TSV)))
RELS_TSV_CKSUM = $(addsuffix $(CKSUM_EXT_COND),$(RELS_TSV))
MAKE_RELS_TABLE_NAME = $(subst $(CORPNAME)_rels,relations_$(CORPNAME_U),\
			$(subst $(TSV_CKSUM),,$(notdir $(1))))
RELS_TABLES = $(call MAKE_RELS_TABLE_NAME,$(RELS_TSV_CKSUM))

$(call showvars,RELS_TSV RELS_TABLES)

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
$(call debuginfo,No *.mk)

# If SRC_FILES_REAL is empty, this makefile is in an intermediate
# directory with only subdirectories
ifeq ($(strip $(SRC_FILES_REAL)),)
$(call debuginfo,Empty SRC_FILES_REAL)

# If SUBDIRS is empty and if this is not a parallel corpus and has no
# subcorpora, SRC_FILES probably has been forgotten or is empty
ifeq ($(strip $(SUBDIRS)),)
$(call debuginfo,Empty SUBDIRS)
ifeq ($(strip $(PARCORP)$(HAS_SUBCORPORA)),)
$(call debuginfo,Not parallel corpus; no subcorpora)
ifeq ($(strip $(SRC_FILES)),)
$(error Please specify the source files in SRC_FILES)
else
ifeq ($(strip $(SRC_FILES_GENERATED)),)
$(error No file(s) $(SRC_FILES) found in $(SRC_DIR))
else
TOP_TARGETS = generate-src all
endif
endif

else ifneq ($(strip $(PARCORP)),)
$(call debuginfo,Parallel corpus)

# Parallel corpus main
TOP_TARGETS = all

endif

else # SUBDIRS non-empty
$(call debuginfo,Non-empty SUBDIRS)

# Make in subdirectories only
TOP_TARGETS = subdirs

endif # SUBDIRS non-empty

else # SRC_FILES defined
$(call debuginfo,Non-empty SRC_FILES)

# A single corpus: make actual corpus targets
TOP_TARGETS = all

endif # SRC_FILES defined

else # $(CORPORA) != $(CORPNAME_BASE)
$(call debuginfo,CORPORA != CORPNAME_BASE ($(CORPORA) != $(CORPNAME_BASE)))

# The directory has *.mk for subcorpora and may contain subdirectories
TOP_TARGETS = subdirs $(CORPORA)

endif

# If subcorpora specified in SUBCORPORA, add them to the main target
# and to TARGETS in case we are processing a subcorpus.mk file
ifneq ($(strip $(HAS_SUBCORPORA)),)
TOP_TARGETS += subcorpora pkg
TARGETS := subcorpora $(if $(MAKE_PKG),pkg)
endif

$(call showvars,TOP_TARGETS TARGETS)


all-top: $(TOP_TARGETS)

all: $(TARGETS)

subdirs: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@

generate-src: $(SRC_FILES_GENERATED)

.PHONY: all-top $(TOP_TARGETS) all subdirs $(SUBDIRS)


# Define rules for targets $(CORPORA) and $(CORPORA)$(SUBTARGET_SEP)$(TARGET)

define MAKE_CORPUS_R
$(1)$(if $(subst $(SUBTARGET_SEP),,$(2)),$(SUBTARGET_SEP)$(2)):
	$$(MAKE) -f $(1).mk $(or $(TARGET),$(subst $(SUBTARGET_SEP),all,$(2))) \
		CORPNAME_BASE=$(1) CORPNAME_BASEBASE=$(1) DB=$(DB)

.PHONY: $(1)$(if $(subst $(SUBTARGET_SEP),,$(2)),$(SUBTARGET_SEP)$(2))
endef

$(foreach corp,$(CORPORA),\
	$(foreach targ,$(TARGETS) $(SUBTARGET_SEP),\
		$(eval $(call MAKE_CORPUS_R,$(corp),$(targ)))))


subcorpora: $(SUBCORPORA)

.PHONY: subcorpora

define MAKE_SUBCORPUS_R
$(1)$(if $(subst $(SUBTARGET_SEP),,$(2)),$(SUBTARGET_SEP)$(2)):
	for makefile in $(1).mk $(CORPNAME_MAIN)_$(1).mk $(CORPNAME_MAIN).mk \
			Makefile; do \
		if test -e $$$$makefile; then \
			$(MAKE) -f $$$$makefile \
				$(or $(TARGET),$(subst $(SUBTARGET_SEP),all,$(2))) \
				CORPNAME_MAIN="$(CORPNAME_MAIN)_$(1)" \
				CORPNAME_BASE="$(CORPNAME_BASE)_$(1)" \
				CORPNAME_BASEBASE="$(CORPNAME_BASEBASE)" \
				SUBCORPUS="$(1)" DB=$(DB); \
			break; \
		fi; \
	done; \

.PHONY: $(1)$(if $(subst $(SUBTARGET_SEP),,$(2)),$(SUBTARGET_SEP)$(2))
endef

$(foreach subcorp,$(SUBCORPORA),\
	$(foreach targ,$(TARGETS) $(SUBTARGET_SEP),\
		$(eval $(call MAKE_SUBCORPUS_R,$(subcorp),$(targ)))))


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

timedata: reg
	$(CONVERT_TIMEDATA) $(CORPNAME)

.PHONY: reg vrt timedata

# The info file $(CORPCORPDIR)/.info is (ab)used as a timestamp file
# to avoid unnecessarily remaking the corpus data if the .vrt file has
# not changed.

$(CORPCORPDIR)/.info: \
		$(CORP_VRT_CKSUM) \
		$(CORPNAME_BUILDDIR).info \
		$(S_ATTRS_DEP)
	-mkdir $(CORPCORPDIR) || /bin/rm $(CORPCORPDIR)/*
	$(CAT) $(<:$(CKSUM_EXT)=) | $(CWB_ENCODE) $(P_OPTS) $(S_OPTS) \
	&& cp $(CORPNAME_BUILDDIR).info $(CORPCORPDIR)/.info

%.info: %$(VRT_CKSUM)
	$(CWBDATA_EXTRACT_INFO) $(CORPNAME) > $@

%.sattrs: %$(VRT_CKSUM)
	$(CAT) $(<:$(CKSUM_EXT)=) \
	| $(MAKE_CWB_STRUCT_ATTRS) > $@

VRT_POSTPROCESS = \
	$(if $(VRT_POSTPROCESS_EXTRA),$(VRT_POSTPROCESS_EXTRA) |) \
	$(VRT_EXTRACT_TIMESPANS) \
	| $(VRT_FIX_ATTRS) \
	| $(VRT_ADD_LEMGRAMS) \
	$(if $(VRT_POSTPROCESS_EXTRA_FINAL),| $(VRT_POSTPROCESS_EXTRA_FINAL)) \
	| $(COMPR)

# This does not support passing compressed files or files requiring
# transcoding to a program requiring filename arguments. That might be
# achieved by using named pipes as for mysqlimport.
$(CORP_VRT) $(CORPNAME_BUILDDIR)_timespans$(TSV): \
		$(SRC_FILES_REAL) $(MAKE_VRT_DEPS) $(VRT_FIX_ATTRS_PROG) \
		$(VRT_EXTRACT_TIMESPANS_PROG) $(DEP_MAKEFILES) $(VRT_EXTRA_DEPS)
	$(MAKE_VRT_SETUP)
	-mkdir -p $(CORP_BUILDDIR)
ifdef MAKE_VRT_FILENAME_ARGS
	$(MAKE_VRT_CMD) $(SRC_FILES_REAL) \
	| $(VRT_POSTPROCESS) > $@
else
	$(if $(MAKE_VRT_SEPARATE_FILES),\
		for filename in $(SRC_FILES_REAL); do \
			$(CAT_SRC) "$$filename" \
			| $(TRANSCODE) \
			| $(MAKE_VRT_CMD); \
		done, \
		$(CAT_SRC) $(SRC_FILES_REAL) \
		| $(TRANSCODE) \
		| $(MAKE_VRT_CMD)) \
	| $(VRT_POSTPROCESS) > $@
endif
	$(MAKE_VRT_CLEANUP)

db: korp_db

korp_db: $(DB_TARGETS)

sql: $(DB_SQLDUMPS)

DB_TARGET_RELS = $(if $(LOAD_DB),\
			$(CORPNAME_BUILDDIR)_rels_load.timestamp,\
			$(RELS_TSV_CKSUM))

korp_rels: $(DB_TARGET_RELS)

.PHONY: db korp_db sql korp_rels


$(CORPNAME_BUILDDIR)_rels_load.timestamp: \
		$(RELS_TSV_CKSUM) $(RELS_CREATE_TABLES_TEMPL)
	mysql --user $(DBUSER) \
		--execute '$(RELS_DROP_TABLES) $(RELS_CREATE_TABLES_SQL)' \
		$(DBNAME)
	$(foreach rel,$(RELS_TSV_CKSUM),\
		$(call MYSQL_IMPORT,$(rel),$(strip \
			$(call MAKE_RELS_TABLE_NAME,$(rel)))))
	touch $@

$(CORPSQLDIR)/$(CORPNAME)_rels$(SQL): \
		$(CORPNAME_BUILDDIR)_rels_load.timestamp
	mysqldump --no-autocommit --user $(DBUSER) $(DBNAME) $(RELS_TABLES) \
	| $(COMPR) > $@

$(RELS_TSV): $(CORP_VRT_CKSUM) $(MAKE_RELS_DEPS)
	$(CAT) $(<:$(CKSUM_EXT)=) \
	| $(MAKE_RELS_CMD)

define KORP_LOAD_DB_R
korp_$(1): $(CORPNAME_BUILDDIR)_$(1)$(if $(LOAD_DB),_load.timestamp,$(TSV_CKSUM))

.PHONY: korp_$(1)

CREATE_SQL_$(1) = '\
	CREATE TABLE IF NOT EXISTS `$$(TABLENAME_$(1))` ( \
		$$(COLUMNS_$(1)) \
	) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8 DEFAULT COLLATE=utf8_bin;'

$(CORPNAME_BUILDDIR)_$(1)_load.timestamp: $(CORPNAME_BUILDDIR)_$(1)$(TSV_CKSUM)
	mysql --user $(DBUSER) --execute $$(CREATE_SQL_$(1)) $(DBNAME)
	mysql --user $(DBUSER) \
		--execute "delete from $$(TABLENAME_$(1)) where corpus='$(CORPNAME_U)';" \
		$(DBNAME)
	$$(call MYSQL_IMPORT,$$<,$$(TABLENAME_$(1)))
	touch $$@

$(CORPSQLDIR)/$(CORPNAME)_$(1)$(SQL): $(CORPNAME_BUILDDIR)_$(1)_load.timestamp
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
	`freq_prefix` int(11) DEFAULT NULL, \
	`freq_suffix` int(11) DEFAULT NULL, \
	`corpus` varchar(64) NOT NULL, \
	UNIQUE KEY `lemgram_corpus` (`lemgram`, `corpus`), \
	KEY `lemgram` (`lemgram`), \
	KEY `corpus` (`corpus`)

$(eval $(call KORP_LOAD_DB_R,lemgrams))

$(CORPNAME_BUILDDIR)_lemgrams$(TSV): $(CORP_VRT_CKSUM)
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

$(eval $(call KORP_LOAD_DB_R,timespans))


# Make full-text files from VRT and copy possible extra files into the
# full-text directory.
fulltext: vrt $(FULLTEXT_EXTRA_FILES) \
		$(FULLTEXTROOT_SRCDIR)/$(FULLTEXT_ROOT_EXTRA_FILES) \
		$(FULLTEXT_EXTRA_DEPS)
	-mkdir -p $(FULLTEXT_DIR)
	$(CAT) $(CORP_VRT) \
	| $(DECODE_SPECIAL_CHARS) \
	| $(MAKE_FULLTEXT_CMD)
ifneq ($(strip $(FULLTEXT_EXTRA_FILES)),)
	cp -p $(FULLTEXT_EXTRA_FILES) $(FULLTEXT_DIR)
endif
ifneq ($(strip $(FULLTEXT_ROOT_EXTRA_FILES)),)
	cp -p $(FULLTEXTROOT_SRCDIR)/$(FULLTEXT_ROOT_EXTRA_FILES) \
		$(FULLTEXTROOT)
endif


pkg: $(PKG_FILE)

# TODO: Make this rule depend on database TSV/SQL files
$(PKG_FILE): $(foreach subcorp,$(SUBCORPORA_ALL),$(CORPDIR)/$(subcorp)/.info) \
		$(if $(PARCORP),align)
	-mkdir -p $(dir $@)
	$(MAKE_CORPUS_PKG) $(PKGNAME_BASE) $(SUBCORPORA_ALL)

.PHONY: pkg


# Align parallel corpora

ALIGN_CORP = \
	$(CWB_REGEDIT) $(CORPNAME)_$(1) :add :a "$(CORPNAME)_$(2)"; \
	align=$(CORP_BUILDDIR)_$(1)/$(CORPNAME)_$(1)_$(2)$(ALIGN); \
	fifo=$$align.fifo; \
	mkfifo $$fifo; \
	($(CAT) $$align > $$fifo &); \
	$(CWB_ALIGN_ENCODE) -D $$fifo; \
	rm $$fifo

# Store the alignment timestamp file in the corpus directory of the
# first language
PARCORP_MAINDIR = $(CORP_BUILDDIR)_$(firstword $(LANGUAGES))
ALIGN_TIMESTAMP = $(PARCORP_MAINDIR)/$(CORPNAME)_aligned.timestamp

# Basenames (without suffix) for alignment files
ALIGN_BASENAMES = \
	$(foreach langpair,$(LANGPAIRS_ALIGN),\
		$(CORP_BUILDDIR)_$(call LANGPAIR_LANG1,$(langpair))/$(CORPNAME)_$(langpair))

# CHECK: Does this always work correctly when running more than one
# simultaneous job?

# FIXME: When changing some parts of a parallel corpus, the alignments
# do not seem to get encoded.

align: parcorp $(ALIGN_TIMESTAMP)

.PHONY: align

$(ALIGN_TIMESTAMP): $(addsuffix $(ALIGN_CKSUM),$(ALIGN_BASENAMES))
	for langpair in $(LANGPAIRS_ALIGN); do \
		lang1=`echo $$langpair | sed -e 's/_.*//'`; \
		lang2=`echo $$langpair | sed -e 's/.*_//'`; \
		$(call ALIGN_CORP,$${lang1},$${lang2}); \
	done
	touch $@

MAKE_ALIGN_CMD ?= \
	mkfifo $(3).fifo; \
	($(CWB_ALIGN) -o $(3).fifo -r $(REGDIR) \
		-V $(LINK_ELEM)_$(LINK_ATTR) \
		$(CORPNAME)_$(strip $(1)) $(CORPNAME)_$(strip $(2)) \
		$(LINK_ELEM) > /dev/null &); \
	$(COMPR) < $(3).fifo > $(3); \
	rm -f $(3).fifo

define MAKE_ALIGN_R
$(CORP_BUILDDIR)_$$(strip $(1))/$(CORPNAME)_$$(strip $(1))_$$(strip $(2))$(ALIGN): \
		$(CORPDIR)/$(CORPNAME)_$$(strip $(1))/.info
	$(call MAKE_ALIGN_CMD,$$(strip $(1)),$$(strip $(2)),$$@)
endef

$(call showvars,ALIGN_FILES ALIGN_LANGS LANGPAIRS_ALIGN)

$(foreach langpair,$(LANGPAIRS_ALIGN),\
	$(eval $(call MAKE_ALIGN_R,$(call LANGPAIR_LANG1,$(langpair)),\
					$(call LANGPAIR_LANG2,$(langpair)))))

MAKE_PARCORP_PARTS = \
	for lang in $(LANGUAGES); do \
		for makefile in $(CORPNAME_MAIN)_$$lang.mk \
				$(CORPNAME_MAIN)_any.mk $(CORPNAME_MAIN).mk \
				Makefile; do \
			if test -e $$makefile; then \
				$(MAKE) -f $$makefile $(1) \
					CORPNAME_MAIN="$(CORPNAME_MAIN)" \
					CORPNAME_BASE="$(CORPNAME_BASE)_$$lang" \
					CORPNAME_BASEBASE="$(CORPNAME_BASEBASE)" \
					LANGUAGES="$(LANGUAGES)" \
					PARCORP_LANG=$$lang; \
				break; \
			fi; \
		done; \
	done

parcorp:
	$(call MAKE_PARCORP_PARTS,all PARCORP_PART=1)

.PHONY: parcorp
