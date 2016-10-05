# -*- coding: utf-8 -*-


CORPNAME_BASE = dma_2016

SRC_SUBDIR = dma
SRC_FILES = tsv/dma6.tsv
# SRC_FILES = dma6-sample2.tsv
# SRC_FILES = dma6-test2.tsv
SRC_FILES_GENERATED = dma_2014-2015.tsv

src_files_new = $(SRC_DIR)/uudet/*.txt

# lemma, pos and msd are only used to convey place name information to
# Korp's map facility.
P_ATTRS = searchword wordtype lemma pos msd

CORPUS_DATE = unknown

COMPRESS_TARGETS = gz
S_ATTRS_FEATSET = "sentence_signum sentence_text_words sentence_search_words"

MAKE_VRT_PROG = ./dma-tsv2vrt.py

# First convert Windows CP-1252 punctuation characters left in the
# data to their UTF-8 equivalents, remove control characters, convert
# double backslashes to single ones, replace lone right curly brackets
# with square brackets and remove SKN page number information
# (remaining after running the original scripts because of a comma).
#
# Sort the result (except the heading line) by parish and text, so
# that duplicates can be removed. It seems that a literal tab cannot
# be passed to commands here, perhaps because the value of the
# variable is used as an argument to the macro partvar_or_default, so
# we use a temporary file as a workaround.
#
# Then convert to VRT and add place name information.
MAKE_VRT_CMD = \
	( \
	header=`cat $(SRC_FILES_REAL) | head -1`; \
	printf "\t" > tab.tmp; \
	( \
		sort_keys=`echo $$header | awk '{for (i = 1; i <= NF; i++) { if ($$i ~ /^(parish|text)$$/) { printf " -k" i "," i } } }'`; \
		echo "$$header"; \
		tail -n+2 \
		| perl -CSD -pe ' \
			s/\x85/\x{2026}/g; s/\x8A/\x{0160}/g; \
			s/\x91/\x{2018}/g; s/\x92/\x{2019}/g; \
			s/\x93/\x{201D}/g; s/\x94/\x{201E}/g; \
			s/\x96/\x{2013}/g; s/\x9a/\x{0161}/g; \
			s/[\x00-\x08\x0B-\x1F]//g; \
			s/\\\\/\\/g; \
			s/(\s)\}(\s)/$$1]$$2/g; \
			s/(\s)\]\s+\](\s)/$$1]$$2/g; \
			s/(SKN [0-9]+), +s\. +[0-9]+/\1/g;' \
		| LC_ALL=C sort "-t`cat tab.tmp`" -s $$sort_keys \
	) $(if $(DEBUG), | tee $(CORP_BUILDDIR)/dma-sorted.tsv) \
	| $(RUN_PYTHON) ./dma-combine-duplicates.py \
		2> $(CORP_BUILDDIR)/dma-combine-duplicates.err \
	$(if $(DEBUG), | tee $(CORP_BUILDDIR)/dma-nodupl.tsv) \
	| ( \
		echo "$$header"; \
		tail -n+2 \
		| LC_ALL=C sort "-t`cat tab.tmp`" -s -k2 \
	) \
	| $(RUN_PYTHON) ./dma-tsv2vrt.py \
		2> $(CORP_BUILDDIR)/dma-tsv2vrt.err \
	| $(SCRIPTDIR)/vrt-add-placenames.py \
		--source-attribute="text_parish_name"; \
	rm tab.tmp \
	)

MAKE_VRT_DEPS_EXTRA = dma-combine-duplicates.py dma-tsv2vrt.py


include ../corp-common.mk


# Convert the new original files to roughly the same format as the SUI
# DMA MySQL database dump (dma6.tsv), by using the old scripts. Add
# ids beginning from the end of the old ones.
$(CORP_BUILDDIR)/dma_2014-2015.tsv: $(src_files_new)
	mkdir -p $(CORP_BUILDDIR)
	cat $^ \
	| tr -d '\015' \
	| grep -viah '^Area' \
	| grep -va '^	' \
	| perl -pe 's/\s+\n/\n/; s/(\s)\}(\s)/$$1]$$2/g' \
	| awk -F'	' 'BEGIN {OFS = FS} {$$8 = $$4; print}' \
	| scripts-old/muuta_korvausmerkit.pl \
	| scripts-old/muuta_rakenne.pl \
	| scripts-old/lisaa_pdf_linkit.pl \
	| perl -pe 'BEGIN {$$id = 403965} \
		    s/^(.*?)\t(.*?)(\t.+)$$/$$id\t$$1\t$$1 $$2\t$$2$$3\t/; \
		    $$id++;' \
	| iconv -fcp1252 > $@
