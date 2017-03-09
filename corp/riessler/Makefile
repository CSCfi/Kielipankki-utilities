# -*- coding: utf-8 -*-


SRC_SUBDIR := riessler/kildin

SRC_FILES := sjd20*[!X].eaf

P_ATTRS =

CORPNAME_BASE = kildin_sample

MAKE_VRT_FILENAME_ARGS = true

MAKE_VRT_CMD = \
	$(SCRIPTDIR)/eaf2vrt.py --metadata-file $(wildcard $(SRC_DIR)/*.txt)

VRT_POSTPROCESS_EXTRA = \
	perl -ne ' \
        BEGIN {$$p = 1} \
        if (/^<sentence .*orth_orig="\#"/) {$$p = 0; next} \
        elsif ($$p == 0 && /^<\/sentence/) {$$p = 1; next} \
	elsif ($$p) {print}' \
	| $(SCRIPTDIR)/vrt-scramble.py

CORPUS_DATE_PATTERN = "text year"
# CORPUS_DATE_FULL_ORDER = ymd

# COMPRESS_TARGETS = gz


include ../corp-common.mk
