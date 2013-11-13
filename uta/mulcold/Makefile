# -*- coding: utf-8 -*-

# Specify corpora explicitly to ignore old and test corpora
CORPORA = mulcold

LANGUAGES = fi en sv ru de

LINK_ELEM = align
LINK_ATTR = id

COMPRESS_TARGETS = bz2

SRC_FILES = *_$(PARCORP_LANG).vrt

P_ATTRS_other = lemma pos msd amblemma ambpos ambmsd
P_ATTRS_de =

VRT_FIX_ATTRS_OPTS_EXTRA_BASE = \
	--rename-element="s:sentence" --add-element-id="sentence" \
	--replace-xml-character-entities="all" \
	--copy-struct-attribute="align:text/*"
unknown = missing=UNKNOWN
VRT_FIX_ATTRS_OPTS_EXTRA_other = \
	$(VRT_FIX_ATTRS_OPTS_EXTRA_BASE) \
	--input-fields="word lemma pos msd" \
	--output-fields='word lemma:setfirst,$(unknown) pos:setfirst,$(unknown) msd:setfirst,missing="" lemma:setconvert,$(unknown) pos:setconvert,$(unknown) msd:setconvert,missing=""'
VRT_FIX_ATTRS_OPTS_EXTRA_de = \
	$(VRT_FIX_ATTRS_OPTS_EXTRA_BASE)


include ../../corp-common.mk
