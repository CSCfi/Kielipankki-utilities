# -*- coding: utf-8 -*-


SRC_SUBDIR := la/murre/xml

EXTRA_ATTRS_FILE = la_murre-extra_text_attrs.tsv

SUBCORPORA := $(shell cut -f2 $(EXTRA_ATTRS_FILE) | tail -n+2 | sort -u)

ADD_EXTRA_ATTRS = ./la_murre-add-extra-text-attrs.pl
ADD_CLAUSE_ELEMS = ./la_murre-add-clause-elems.pl
ADD_LAT_LINKS = ./la_murre-add-lat-links.pl
ADD_METADATA = ./la_murre-add-metadata.py

EXTRAINFO_FILE = $(CORPNAME_BUILDDIR)_extrainfo.tsv
LAT_LINK_DIR = $(SRC_DIR)/../lat-links
IMDI_DIR = $(SRC_DIR)/../imdi

define subcorp_defs
SRC_FILES_$(1) := \
	$$(addsuffix .xml,$$(shell egrep '	$(1)	' $(EXTRA_ATTRS_FILE) | cut -f1))
MAKE_VRT_DEPS_EXTRA_$(1) = \
	$$(EXTRAINFO_FILE) \
	$(ADD_EXTRA_ATTRS) $(ADD_CLAUSE_ELEMS) $(ADD_LAT_LINKS) \
	$(ADD_METADATA) \
	$$(foreach srcfile,$(SRC_FILES_$(1)),\
		$(LAT_LINK_DIR)/$$(basename $$(srcfile)).vrt \
		$(IMDI_DIR)/$$(basename $$(srcfile)).imdi)
endef

$(foreach subcorp,$(SUBCORPORA),\
	$(eval $(call subcorp_defs,$(subcorp))))

P_ATTRS = cleanword lemma pos msd func cow note lex

CORPNAME_BASE = lam
PKGNAME_BASE = la_murre

XML2VRT_RULES = la_murre.xml2vrt
LEMGRAM_POSMAP = la_murre-lemgram_posmap.tsv

MAKE_VRT_CMD = \
	$(XML2VRT) \
	| $(ADD_EXTRA_ATTRS) $(EXTRAINFO_FILE) \
	| $(ADD_CLAUSE_ELEMS) --remove-cl \
	| $(ADD_LAT_LINKS) --link-params-only $(LAT_LINK_DIR) \
	| $(ADD_METADATA) $(IMDI_DIR) \
	| perl -ne '\
	if (/^</) { print } \
	else { \
		@fields = split (/\t/); \
		$$origword = $$fields[0]; \
		if ($$origword !~ /^[[:punct:]]+$$/) { \
			$$fields[0] =~ s/[*+()%\x27]//g; \
			$$fields[0] =~ s/\.{3,}$$//; \
		} \
		print join ("\t", $$origword, @fields) \
	}'

FULLTEXT_SUBDIR = la_murre

FULLTEXT_XSLT = ./la_murre-make-fulltext-html.xslt
FULLTEXT_FILENAME_TEMPLATE = {xpath:/text/@filename}.html

FULLTEXT_EXTRA_FILES = la_murre_fulltext.css
FULLTEXT_ROOT_EXTRA_FILES = highlight_match.js
FULLTEXT_EXTRA_DEPS = $(EXTRA_ATTRS_FILE)

# Add text attributes dialect_region_name and dialect_group_name that
# are not included in the VRT before processing it with XSLT.
MAKE_FULLTEXT_CMD = perl -pe '\
	if (/^<text/) { \
		($$fname) = /\bfilename="(.*?)"/; \
		@lines = qx(egrep "^$$fname\t" "$(EXTRA_ATTRS_FILE)"); \
		@fields = split ("\t", $$lines[0]); \
		s/>/ dialect_region_name="$$fields[4]" dialect_group_name="$$fields[6]">/; \
	}' | \
	$(VRT_MAKE_FULLTEXT)

CORPUS_DATE_PATTERN = "text date"
CORPUS_DATE_FULL_ORDER = ymd

COMPRESS_TARGETS = gz


include ../../corp-common.mk


$(EXTRAINFO_FILE): $(EXTRA_ATTRS_FILE)
	mkdir -p $(CORP_BUILDDIR)
	head -1 $< > $@
	egrep '	$(SUBCORPUS)	' $< >> $@
