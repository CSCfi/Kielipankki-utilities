# -*- coding: utf-8 -*-


MODE = biblia
VKS2VRT_OPTS = --bible-references

SRC_FILES = vt4_prof.sen

P_ATTRS = 
S_ATTRS = work:0+code book:0+code chapter:0+code+bibleref \
		verse:0+code+bibleref sentence:0+id \
		sourcecode:0+work+code+book+chapter+verse+page+bibleref \
		span:0+work+code+book+chapter+verse+page+bibleref

include vks-common.mk
