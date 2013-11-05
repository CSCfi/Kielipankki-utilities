# -*- coding: utf-8 -*-

# Specify corpora explicitly to ignore old and test corpora
CORPORA = mulcold

LANGUAGES = fi en sv ru de

LINK_ELEM = align
LINK_ATTR = id

COMPRESS_TARGETS = bz2

SRC_FILES = *_$(PARCORP_LANG).vrt

P_ATTRS_other = lemma pos msd
P_ATTRS_de =

VRT_FIX_ATTRS_OPTS_EXTRA_BASE = \
	--rename-element="s:sentence" --add-element-id="sentence" \
	--replace-xml-character-entities="all"
VRT_FIX_ATTRS_OPTS_EXTRA_other = \
	$(VRT_FIX_ATTRS_OPTS_EXTRA_BASE) \
	--missing-field-values="3:UNKNOWN"
VRT_FIX_ATTRS_OPTS_EXTRA_de = \
	$(VRT_FIX_ATTRS_OPTS_EXTRA_BASE)


include ../../corp-common.mk
