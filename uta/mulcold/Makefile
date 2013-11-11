# -*- coding: utf-8 -*-

# Specify corpora explicitly to ignore old and test corpora
CORPORA = mulcold

LANGUAGES = fi en sv ru de

LINK_ELEM = align
LINK_ATTR = id

COMPRESS_TARGETS = bz2

SRC_FILES = *_$(PARCORP_LANG).vrt

P_ATTRS_fi = lemma lemmacomp pos msd amblemma ambpos ambmsd lex
P_ATTRS_sv = $(P_ATTRS_fi)
P_ATTRS_en = $(filter-out lemmacomp,$(P_ATTRS_fi))
P_ATTRS_ru = $(P_ATTRS_en)
P_ATTRS_de =

VRT_FIX_ATTRS_OPTS_EXTRA_BASE = \
	--rename-element="s:sentence" --add-element-id="sentence" \
	--replace-xml-character-entities="all" \
	--copy-struct-attribute="align:text/*"
unknown = missing=UNKNOWN
VRT_FIX_ATTRS_OPTS_EXTRA_other = \
	$(VRT_FIX_ATTRS_OPTS_EXTRA_BASE) \
	--input-fields="word lemma pos msd" \
	--output-fields='word lemma:setfirst,noboundaries,$(unknown) lemma:setfirst,$(unknown) pos:setfirst,$(unknown) msd:setfirst,missing="" lemma:setconvert,$(unknown) pos:setconvert,$(unknown) msd:setconvert,missing=""'
VRT_FIX_ATTRS_OPTS_EXTRA_de = \
	$(VRT_FIX_ATTRS_OPTS_EXTRA_BASE)

LEMGRAM_POSMAP = ../lemgram_posmap_uta_$(PARCORP_LANG).tsv

include ../../corp-common.mk
