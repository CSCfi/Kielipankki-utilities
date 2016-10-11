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
P_ATTRS = lemma lemmacomp pos msd dephead deprel ref lex/
# P_ATTRS_ru = $(filter-out lemmacomp,$(P_ATTRS_fi))

# Add a trailing newline if it is missing. (TODO: Handle this in
# corp-common.mk.)
# Add attribute year for the publication year of the text: translation
# year if it exists, otherwise the original year.
# Add attribute "filename" to "text" elements, based on an environment
# variable containing the file name (in corp-common.mk).
FIX_INPUT = perl -pe '\
        if (! /\n$$/) { \
		$$_ .= "\n"; \
        } \
	if (/^<text/) { \
		($$yorig) = /yearorig="(.*?)"/; \
		($$ytr) = /yeartr="(.*?)"/; \
		$$y = $$ytr || $$yorig; \
		s/\s*>\s*\n/ year="$$y" filename="'"`basename $$filename .vrt`"'">\n/; \
	}'
MAKE_VRT_SEPARATE_FILES = true
MAKE_VRT_CMD ?= $(FIX_INPUT)
MAKE_VRT_PROG =

unknown = missing=UNKNOWN
# In contrast to the TDT annotations used in many corpora, the
# annotations in the Finnish sides of ParFin and ParRus use # as the
# compound boundary marker (the default for vrt-fix-attrs.py).
VRT_FIX_ATTRS_OPTS_EXTRA = \
	--rename-element="s:sentence" \
	--rename-element="align:link" \
	--add-element-id="sentence" \
	--replace-xml-character-entities="numeric" \
	--copy-struct-attribute="link:text/*" \
	--copy-struct-attribute="sentence:text/*" \
	--input-fields="word ref lemma pos msd deprel dephead" \
	--compound-boundary-can-replace-hyphen \
	--output-fields='word lemma:noboundaries lemma pos msd dephead deprel ref'

# Combine link attributes filename and id to a new id to be used for
# alignment, and rename id as orig_id.
VRT_POSTPROCESS_EXTRA_FINAL = perl -pe '\
	if (/^<link/) { \
		($$id0, $$fbase) = /\bid="(.*?)".*?\btext_filename="(.*)_..\d"/; \
		$$id = "$$fbase:$$id0"; \
		s/\bid=/id="$$id" orig_id=/ \
	}' \

LEMGRAM_POSMAP ?= ../lemgram_posmap_uta_$(PARCORP_LANG).tsv
WORDPICT_RELMAP_fi ?= ../../wordpict_relmap_ud_fi.tsv
WORDPICT_RELMAP_ru = ../wordpict_relmap_uta_ru.tsv

CORPUS_DATE_PATTERN = "text year"

# This file is included in Makefiles in subdirectories, so we need to
# use ../../ here.
include ../../corp-common.mk
