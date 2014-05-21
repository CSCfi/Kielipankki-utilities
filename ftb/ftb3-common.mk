# -*- coding: utf-8 -*-


# Do not remake if makefiles are changed (because of the time it takes
# to rebuild the corpus).
MAKEFILE_DEPS ?= false

SRC_DIR ?= $(CORPSRCROOT)/ftb/ftb3

P_ATTRS = lemma lemmacomp pos msd dephead deprel ref lex

LOC_EXTRA_INFO = $(CORPNAME)-loc-extras.txt$(COMPR_EXT)
VRT_EXTRA_DEPS = $(LOC_EXTRA_INFO)
FTB3_AUGMENT_LOC = $(SCRIPTDIR)/ftb3-augment-loc.py

MAKE_VRT_SETUP = (rm -f $(LOC_EXTRA_INFO).fifo; \
		mkfifo $(LOC_EXTRA_INFO).fifo; \
		$(CAT) $(LOC_EXTRA_INFO) > $(LOC_EXTRA_INFO).fifo) &
MAKE_VRT_CMD = $(SCRIPTDIR)/ftbconllx2vrt.py --pos-type=original \
		--no-fix-morpho-tags --no-subcorpora \
		--loc-extra-info-file=$(LOC_EXTRA_INFO).fifo
MAKE_VRT_CLEANUP = rm -f $(LOC_EXTRA_INFO).fifo

MAKE_RELS_CMD = $(SCRIPTDIR)/ftbvrt2wprel.py \
		--input-fields="word $(P_ATTRS)" \
		--output-prefix=$(CORPNAME_BUILDDIR)_rels \
		--compress=$(COMPRESS) --sort

VRT_EXTRACT_TIMESPANS_OPTS = --two-digit-years --full-dates --exclude "* id"

LEMGRAM_POSMAP = lemgram_posmap_ftb.tsv


include ftb-common.mk


$(LOC_EXTRA_INFO): $(SRC_FILES_REAL) $(FTB3_AUGMENT_LOC)
	$(CAT) $(SRC_FILES_REAL) \
	|  $(FTB3_AUGMENT_LOC) --loc-only \
		--source-type=$(FTB3_SOURCE_TYPE) \
		--original-file-directory=$(FTB3_ORIG_SOURCE_DIR) \
	| $(COMPR) > $@
