# -*- coding: utf-8 -*-

CORPNAME_BASE = parrus

# fi contains all the Finnish translations, fiN contain only a single
# translation for each Russian text (fi1 contains files marked with fi
# and fi1).
LANGUAGES = fi fi1 fi2 fi3 ru

SRC_FILES_fi = *_fi.vrt *_fi[1-3].vrt
SRC_FILES_fi1 = *_fi.vrt *_fi1.vrt
SRC_FILES_fi2 = *_fi2.vrt
SRC_FILES_fi3 = *_fi3.vrt
SRC_FILES_ru = *_ru.vrt

LANGPAIRS_ALIGN := \
	$(filter-out fi_fi% fi%_fi,\
		$(foreach lang1,$(LANGUAGES),\
			$(foreach lang2,$(filter-out $(lang1),$(LANGUAGES)),\
				$(lang1)_$(lang2))))

LEMGRAM_POSMAP_fi1 = ../lemgram_posmap_uta_fi.tsv
LEMGRAM_POSMAP_fi2 = ../lemgram_posmap_uta_fi.tsv
LEMGRAM_POSMAP_fi3 = ../lemgram_posmap_uta_fi.tsv

# Replace two characters in the Windows 1252 code points found in the
# source files with their Unicode equivalents. ftfy is not used, since
# it seems to remove the characters in the Cyrillic text instead of
# converting them.
MAKE_VRT_CMD = \
	$(ADD_TEXT_FILENAME) \
	| perl -CSD -pe 's/\x85/\x{2026}/g; s/\x95/\x{2022}/g'

include ../parfinrus-common.mk
