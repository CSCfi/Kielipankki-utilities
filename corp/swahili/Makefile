# -*- coding: utf-8 -*-


CORPNAME_BASE = swahili_sample

SRC_FILES = *.res

P_ATTRS = lemma pos msd gloss syntax verbextra extra1 extra2 extra3

CORPUS_DATE = unknown

# Empty MAKE_VRT_PROG to avoid adding perl as a dependency
MAKE_VRT_PROG =
MAKE_VRT_CMD = \
	tr -d '\015' | \
	perl -ne '\
	if (/^\($$/) { \
		if ($$. > 1) { \
			print "</text>\n"; \
		} \
		print "<text>\n"; \
		next; \
	} elsif (! /^</) { \
		s/&/&amp;/g; \
	} \
	print; \
	END { print "</text>\n"; }'


include ../corp-common.mk
