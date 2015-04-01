# -*- coding: utf-8 -*-


SRC_SUBDIR := la/murre/xml

EXTRA_ATTRS_FILE = la_murre-extra_text_attrs.tsv

SUBCORPORA := $(shell cut -f2 $(EXTRA_ATTRS_FILE) | tail -n+2 | sort -u)

ADD_EXTRA_ATTRS = ./la_murre-add-extra-text-attrs.pl
ADD_CLAUSE_ELEMS = ./la_murre-add-clause-elems.pl

EXTRAINFO_FILE = $(CORPNAME_BUILDDIR)_extrainfo.tsv

define subcorp_defs
SRC_FILES_$(1) := $$(addsuffix .xml,$$(shell egrep '	$(1)	' $(EXTRA_ATTRS_FILE) | cut -f1))
MAKE_VRT_DEPS_EXTRA_$(1) = \
	$$(EXTRAINFO_FILE) $(ADD_EXTRA_ATTRS) $(ADD_CLAUSE_ELEMS)
endef

$(foreach subcorp,$(SUBCORPORA),\
	$(eval $(call subcorp_defs,$(subcorp))))

P_ATTRS = cleanword lemma pos msd func cow note lex

CORPNAME_PREFIX = la_

XML2VRT_RULES = la_murre.xml2vrt
LEMGRAM_POSMAP = la_murre-lemgram_posmap.tsv

MAKE_VRT_CMD = \
	$(XML2VRT) \
	| $(ADD_EXTRA_ATTRS) $(EXTRAINFO_FILE) \
	| $(ADD_CLAUSE_ELEMS) --remove-cl \
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

CORPUS_DATE = unknown

COMPRESS_TARGETS = gz


include ../../corp-common.mk


$(EXTRAINFO_FILE): $(EXTRA_ATTRS_FILE)
	mkdir -p $(CORP_BUILDDIR)
	head -1 $< > $@
	egrep '	$(SUBCORPUS)	' $< >> $@
