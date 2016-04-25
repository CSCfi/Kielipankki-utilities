# -*- coding: utf-8 -*-


LANG = sv

MAKE_VRT_PREPROCESS = \
	perl -pe 's/\x0D/\\r/g; s/\x08/\\b/g; s/\xC2\x85//g' | \
	$(SORT_VRT_INPUT_$(SUBCORPUS))


include lemmie-common.mk
