# -*- coding: utf-8 -*-


CORPNAME_MAIN ?= ftc

LANG = fi

SUBCORPORA = \
	aamu1995 aamu1999 \
	demari1995 demari1997 demari1998 demari1999 demari2000 \
	hasa1999 hasa2000 \
	hs1995ae hs1995ak hs1995et hs1995hu hs1995ka hs1995kn hs1995ku \
		hs1995ma_mn hs1995misc hs1995mp hs1995nh hs1995po hs1995ro \
		hs1995rt hs1995sp hs1995st hs1995ta_te hs1995tr hs1995ul \
		hs1995vk hs1995vs hs1995yo \
	hysa1994 hysa1997 \
	ilta1996 \
	kaleva1998_1999 \
	kangasa \
	karj1991 karj1992 karj1993 karj1994 karj1995 karj1997 karj1998 \
		karj1999 karj_unspec \
	kesu1999 \
	otava1993 \
	tm1995_1997 \
	tusa1998 tusa1999

SRC_FILE_BASE_karj_unspec = karjUnspec


include lemmie-common.mk
