# -*- coding: utf-8 -*-


SRC_FILES = *.xml
SRC_FILES_EXCLUDE = la_murre_Korp_koe.xml vare_muurl_hali1_2.xml
# SRC_FILES = la_murre_Korp_koe.xml vare_muurl_hali1_2.xml

P_ATTRS = cleanword lemma pos msd func cow note lex

CORPNAME_PREFIX = la_

XML2VRT_RULES = la_murre.xml2vrt
LEMGRAM_POSMAP = la_murre-lemgram_posmap.tsv

MAKE_VRT_CMD = \
	$(XML2VRT) \
	| perl -ne '\
	if (/^</) { print } \
	else { \
		@fields = split (/\t/); \
		$$origword = $$fields[0]; \
		if ($$origword !~ /^[[:punct:]]+$$/) { \
			$$fields[0] =~ s/[*+()%\x27]//g; \
			$$fields[0] =~ s/\.{3,}$$//; \
		} \
		print join ("\t", $$origword, @fields) \
	}'

CORPUS_DATE = unknown

COMPRESS_TARGETS = gz

include ../../corp-common.mk
