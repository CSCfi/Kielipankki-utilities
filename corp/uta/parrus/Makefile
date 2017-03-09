# -*- coding: utf-8 -*-

CORPNAME_BASE = parrus_2016

# fi contains all the Finnish translations, fiN contain only a single
# translation for each Russian text (fi1 contains files marked with fi
# and fi1).
LANGUAGES = fi fi1 fi2 fi3 fi4 ru
num_variants_fi = 1 2 3 4

SRC_FILES_fi = *_fi[1-4].vrt
$(foreach num,$(num_variants_fi),\
	$(eval SRC_FILES_fi$(num) = *_fi$(num).vrt))
SRC_FILES_ru = *_ru1.vrt

LANGPAIRS_ALIGN := \
	$(filter-out fi_fi% fi%_fi,\
		$(foreach lang1,$(LANGUAGES),\
			$(foreach lang2,$(filter-out $(lang1),$(LANGUAGES)),\
				$(lang1)_$(lang2))))

$(foreach num,$(num_variants_fi),\
	$(eval LEMGRAM_POSMAP_fi$(num) = ../lemgram_posmap_uta_fi.tsv) \
	$(eval WORDPICT_RELMAP_fi$(num) = ../../wordpict_relmap_ud_fi.tsv))

# Replace two characters in the Windows 1252 code points found in the
# source files with their Unicode equivalents. ftfy is not used, since
# it seems to remove the characters in the Cyrillic text instead of
# converting them.
MAKE_VRT_CMD = \
	$(FIX_INPUT) \
	| perl -CSD -pe 's/\x85/\x{2026}/g; s/\x95/\x{2022}/g'

include ../parfinrus-common.mk
