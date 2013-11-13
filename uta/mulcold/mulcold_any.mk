# -*- coding: utf-8 -*-


SRC_SUBDIR = uta/mulcold

SRC_FILES = *_$(PARCORP_LANG).vrt

P_ATTRS ?= lemma pos msd

VRT_FIX_ATTRS_OPTS_EXTRA ?= \
	--missing-field-values="3:UNKNOWN" \
	--rename-element="s:sentence" --add-element-id="sentence" \
	--replace-xml-character-entities="all"

include mulcold-common.mk
