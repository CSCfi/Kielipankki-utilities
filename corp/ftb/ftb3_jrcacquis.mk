# -*- coding: utf-8 -*-

SRC_FILES ?= ftb3.1-jrc_acquis.conllx.bz2 
# SRC_FILES ?= ftb3.1-jrc_acquis-10000.conllx.bz2 

FTB3_SOURCE_TYPE = jrc
FTB3_ORIG_SOURCE_DIR = $(CORPSRCROOT)/jrc_acquis_30/fi

include ftb3-common.mk
