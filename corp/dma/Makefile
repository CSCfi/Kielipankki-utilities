# -*- coding: utf-8 -*-


CORPNAME_BASE = dma_2016

SRC_SUBDIR = dma
# SRC_FILES = dma6-sample2.tsv
# SRC_FILES = dma6-test2.tsv
SRC_FILES_GENERATED = dma6_fixed.tsv dma_2014-2015.tsv

src_files_old = $(SRC_DIR)/tsv/dma6.tsv
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
# with square brackets, remove SKN page number information (remaining
# after running the original scripts because of a comma), remove
# "<error: loc>" markers (from the PDF field) and replace "Xmlk" with
# "X mlk." and "[Pyhäjä]rvi Ol." with "[Pyhäjä]rvi" in the parish name
# fields (avoid 8-bit characters in the Perl regexp).
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
	tab=$(CORP_BUILDDIR)/tab.tmp; \
	printf "\t" > $$tab; \
	( \
		sort_keys=`echo $$header | awk '{for (i = 1; i <= NF; i++) { if ($$i ~ /^(parish|text)$$/) { printf " -k" i "," i } } }'`; \
		echo "$$header"; \
		tail -n+2 \
		| perl -CSD -ne ' \
			s/\x85/\x{2026}/g; s/\x8A/\x{0160}/g; \
			s/\x91/\x{2018}/g; s/\x92/\x{2019}/g; \
			s/\x93/\x{201D}/g; s/\x94/\x{201E}/g; \
			s/\x96/\x{2013}/g; s/\x9a/\x{0161}/g; \
			s/[\x00-\x08\x0B-\x1F]//g; \
			s/\\\\/\\/g; \
			s/(\s)\}(\s)/$$1]$$2/g; \
			s/(\s)\]\s+\](\s)/$$1]$$2/g; \
			s/(SKN [0-9]+), +s\. +[0-9]+/\1/g; \
			s/ ?<error: loc>//g; \
			@f = /^((?:.*?\t){4})(.*\n)$$/; \
			$$f[0] =~ s/\s?mlk\.?\t/ mlk.\t/g; \
			$$f[0] =~ s/(rvi) Ol\.\t/$$1\t/g; \
			print join("", @f)' \
		| LC_ALL=C sort "-t`cat $$tab`" -s $$sort_keys \
	) $(if $(DEBUG), | tee $(CORP_BUILDDIR)/dma-sorted.tsv) \
	| $(RUN_PYTHON) ./dma-combine-duplicates.py \
		2> $(CORP_BUILDDIR)/dma-combine-duplicates.err \
	$(if $(DEBUG), | tee $(CORP_BUILDDIR)/dma-nodupl.tsv) \
	| ( \
		echo "$$header"; \
		tail -n+2 \
		| LC_ALL=C sort "-t`cat $$tab`" -s -k2 \
	) \
	| $(RUN_PYTHON) ./dma-tsv2vrt.py \
		2> $(CORP_BUILDDIR)/dma-tsv2vrt.err \
	| $(SCRIPTDIR)/vrt-add-placenames.py \
		--source-attribute="text_parish_name"; \
	rm $$tab \
	)

MAKE_VRT_DEPS_EXTRA = dma-combine-duplicates.py dma-tsv2vrt.py


include ../corp-common.mk


# Fix truncated location fields by taking the locations from the PDF
# field if the value of the location field is a prefix of the
# locations in the PDF field.
fix_truncated_locations = \
	perl -F'\t' -ane ' \
		$$loc = $$F[6]; \
		$$pdfloc = $$F[8]; \
		$$pdfloc =~ s/\S+_([0-9]{1,3}[a-z]?)\.pdf/$$1/g; \
		$$pdfloc =~ s/\S+\.pdf//g; \
		$$pdfloc =~ s/<error: loc>//g; \
		$$pdfloc =~ s/^\s*(.*?)\s*$$/$$1/; \
		if ($$pdfloc && $$pdfloc ne "-") { \
			($$loc0, $$loc1, $$loc2) = ($$loc =~ /^(.*?)((?:[0-9]{1,3}[a-z]?)(?: (?:[0-9]{1,3}[a-z]?))*)(.*?)$$/); \
			if ($$loc1 ne $$pdfloc) { \
				$$locinfo = "$$. ($$F[0] $$F[1])"; \
				if (substr ($$pdfloc, 0, length ($$loc1)) eq $$loc1) { \
					print STDERR "$$locinfo: Fixing location based on pdf location: $$loc1 => $$pdfloc\n"; \
					$$loc1 = $$pdfloc; \
				} else { \
					print STDERR "Warning: $$locinfo: location and PDF differ: $$loc1 <> $$pdfloc\n"; \
				} \
			} \
		} \
		$$F[6] = "$$loc0$$loc1$$loc2"; \
		print join ("\t", @F);'

# Fix the location field: move signums before SKNA location; replace
# truncated prefixes of "Suomen kielen nauhoitearkisto" with "SKNA";
# and move two apparent comments to the comment field.
fix_location = \
	perl -F'\t' -ane ' \
		$$F[6] =~ s/^((?:mahdollisesti |luultavasti )?SKNA:\S+(?: tai SKNA:\S+)?)\s+((?:[0-9]+[a-z]? ?)+)/$$2 $$1/; \
		$$F[6] =~ s/ Suomen kielen.*$$/ SKNA/; \
		if ($$F[6] =~ /^(tark\. kaupungissa|paikosta-sanan s:n)/) { \
			$$F[5] = $$F[6]; \
			$$F[6] = "-"; \
		} \
		print join ("\t", @F);'

# Fix the location data in some records of the older dma6 data from
# SUI DMA database and re-add PDF links based on the fixed data. From
# the input to lisaa_pdf_linkit.pl, we need to cut out fields added
# only at later stages and paste them back afterwards.
$(CORP_BUILDDIR)/dma6_fixed.tsv: $(src_files_old) Makefile
	f1_4=$(CORP_BUILDDIR)/dma6_f1-4.tsv; \
	f12=$(CORP_BUILDDIR)/dma6_f12.tsv; \
	cut -d'$(t)' -f1-4 $(src_files_old) \
	| tail -n+2 > $$f1_4; \
	cut -d'$(t)' -f12 $(src_files_old) \
	| tail -n+2 > $$f12; \
	header=`cat $(src_files_old) | head -1`; \
	( \
		echo "$$header"; \
		cut -d'$(t)' -f2,4-11 $(src_files_old) \
		| tail -n+2 \
		| $(fix_truncated_locations) \
		| iconv -tlatin1 \
		| cut -d'$(t)' -f1-8 \
		| $(fix_location) \
		| scripts-old/lisaa_pdf_linkit.pl \
		| cut -d'$(t)' -f3- \
		| iconv -flatin1 \
		| paste $$f1_4 - $$f12 \
	) > $@; \
	rm $$f1_4 $$f12

# Convert the new original files to roughly the same format as the SUI
# DMA MySQL database dump (dma6.tsv), by using the old scripts. Add
# ids beginning from the end of the old ones.
$(CORP_BUILDDIR)/dma_2014-2015.tsv: $(src_files_new) Makefile
	mkdir -p $(CORP_BUILDDIR)
	cat $(src_files_new) \
	| tr -d '\015' \
	| grep -viah '^Area' \
	| grep -va '^	' \
	| perl -pe 's/\s+\n/\n/; s/(\s)\}(\s)/$$1]$$2/g' \
	| awk -F'$(t)' 'BEGIN {OFS = FS} {$$8 = $$4; print}' \
	| scripts-old/muuta_korvausmerkit.pl \
	| scripts-old/muuta_rakenne.pl \
	| $(fix_location) \
	| scripts-old/lisaa_pdf_linkit.pl \
	| perl -pe 'BEGIN {$$id = 403965} \
		    s/^(.*?)\t(.*?)(\t.+)$$/$$id\t$$1\t$$1 $$2\t$$2$$3\t/; \
		    $$id++;' \
	| iconv -fcp1252 > $@
