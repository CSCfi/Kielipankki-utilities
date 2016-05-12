# -*- coding: utf-8 -*-

LANGUAGES ?= fi ru

LINK_ELEM = link
LINK_ATTR = id

COMPRESS_TARGETS = gz

# Even though the Russian words have no compound boundaries marked and
# thus would not need a separate lemmacomp attribute, both aligned
# corpora need the same attributes in the CWB data because korp.cgi
# decodes both using the same set of attributes. The dummy lemmacomp
# in Russian might not be needed if it were the last attribute in
# Finnish.
P_ATTRS = lemma lemmacomp pos msd amblemma/ amblemmacomp/ ambpos/ ambmsd/ lex/
# P_ATTRS_ru = $(filter-out lemmacomp,$(P_ATTRS_fi))

ADD_TEXT_FILENAME = perl -pe '\
	if (/^<text/) { \
		s/>\s*\n/ filename="'"`basename $$filename .vrt`"'">\n/ \
	}'
MAKE_VRT_SEPARATE_FILES = true
MAKE_VRT_CMD ?= $(ADD_TEXT_FILENAME)
MAKE_VRT_PROG =

unknown = missing=UNKNOWN
VRT_FIX_ATTRS_OPTS_EXTRA = \
	--rename-element="s:sentence" \
	--rename-element="align:link" \
	--add-element-id="sentence" \
	--replace-xml-character-entities="numeric" \
	--copy-struct-attribute="link:text/*" \
	--copy-struct-attribute="sentence:text/*" \
	--input-fields="word lemma pos msd" \
	--output-fields='word lemma:setfirst,noboundaries,$(unknown) lemma:setfirst,$(unknown) pos:setfirst,$(unknown) msd:setfirst,missing="" lemma:set,unique,noboundaries,$(unknown) lemma:set,unique,$(unknown) pos:set,unique,$(unknown) msd:set,unique,missing=""'

# Combine link attributes txtnumber and id to a new id to be used for
# alignment, and rename id as orig_id.
VRT_POSTPROCESS_EXTRA_FINAL = perl -pe '\
	if (/^<link/) { \
		($$id0, $$fname) = /\bid="(.*?)".*?\btext_filename="(.*?)"/; \
		($$fnum) = ($$fname =~ /(\d+)/); \
		$$id = "$$fnum:$$id0"; \
		s/\bid=/id="$$id" orig_id=/ \
	}' \

LEMGRAM_POSMAP ?= ../lemgram_posmap_uta_$(PARCORP_LANG).tsv
# Use the ambiguous lemma and pos
VRT_ADD_LEMGRAMS_OPTS = --lemma-field=6 --pos-field=8

CORPUS_DATE_PATTERN = "text period"

# This file is included in Makefiles in subdirectories, so we need to
# use ../../ here.
include ../../corp-common.mk
