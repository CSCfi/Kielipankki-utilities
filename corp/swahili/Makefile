# -*- coding: utf-8 -*-


CORPNAME_BASE = hcs

SUBCORPORA = old_books old_news new_bunge new_news
# SUBCORPORA = new_bunge new_news

SRC_SUBDIR = hcs/hcs-valmis-anl-fixed
# SRC_SUBDIR = hcs/anl-fixed
SRC_FILES = $(subst _,-mat/,$(SUBCORPUS))/*.anl

P_ATTRS = lemma pos msd gloss syntax verbextra extra1 extra2 extra3 rest

COMPRESS_TARGETS = gz

# Empty MAKE_VRT_PROG to avoid adding perl as a dependency
MAKE_VRT_PROG =
# Add datefrom and dateto to text start tags based on the attributes
# year, month and day. Collect the positional attributes after the
# 10th one to a single attribute, the values of fields separated by
# double spaces.
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
	print;'


include ../corp-common.mk
