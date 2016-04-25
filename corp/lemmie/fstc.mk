# -*- coding: utf-8 -*-


CORPNAME_MAIN ?= fstc

SUBCORPORA = \
	fisc_lit fisc_myn fisc_sak fisc_tid \
	fnb1999 fnb2000 \
	hbl1998 hbl1999 \
	jt1999 jt2000 \
	soder_a soder_b

SRC_FILE_BASE_soder_a = soderA
SRC_FILE_BASE_soder_b = soderB

# The texts in hbl1999 are not in completely the text id order
SORT_VRT_INPUT_hbl1999 = sort -t'	' -k8,8n -k1,1n |


include lemmie-sv-common.mk
