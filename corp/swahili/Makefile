# -*- coding: utf-8 -*-


CORPNAME_BASE = hcs2

SUBCORPORA = old_books old_news new_bunge new_news
# SUBCORPORA = new_bunge new_news

SRC_SUBDIR = hcs/hcs-valmis-anl-fixed-jussi
# SRC_SUBDIR = hcs/anl-fixed
SRC_FILES = $(subst _,-mat/,$(SUBCORPUS))/*.anl

P_ATTRS = lemma pos msd gloss syntax msdextra

COMPRESS_TARGETS = gz

# Empty MAKE_VRT_PROG to avoid adding perl as a dependency
MAKE_VRT_PROG =
# Add datefrom and dateto to text start tags based on the attributes
# year, month and day. Collect the positional attributes after the
# 7th one to a single attribute, the values of fields separated by
# double spaces. Finally, remove inappropriate control characters.
MAKE_VRT_CMD = \
	perl -ne '\
        if (/^<text/) { \
		($$year) = / year="(\d{4})/; \
		($$mon) = / month="(\d\d)"/; \
		($$day) = / day="(\d\d)"/; \
		$$date = "$$year$$mon$$day"; \
		s/>/ datefrom="$$date" dateto="$$date">/; \
	} elsif (/^((?:.*\t){10})(\t.*)$$/) { \
		$$base = $$1; \
		$$rest = $$2; \
		$$rest =~ s/\t/  /g; \
		$$_ = "$$base$$rest"; \
	} \
        s/((?:.*\t){4})\{\s*(.*?)\s*\}\t/$$1$$2\t/; \
	print;' \
	| tr -d '\000-\010\013-\037'


include ../corp-common.mk
