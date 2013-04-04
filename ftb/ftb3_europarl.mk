# -*- coding: utf-8 -*-

SRC_FILES ?= ftb3.1-europarl.conllx.bz2 
# SRC_FILES ?= ftb3.1-europarl-10000.conllx.bz2

FTB3_SOURCE_TYPE = europarl
FTB3_ORIG_SOURCE_DIR = $(CORPSRCROOT)/europarl/v5/fi-en/fi

include ftb3-common.mk
