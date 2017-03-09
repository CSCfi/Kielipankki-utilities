# -*- coding: utf-8 -*-


CORPNAME_PREFIX = vks_

INPUT_ENCODING = latin1

VKS2VRT_COMMON_OPTS = --clean-code --embed-source-code --span-elements

MAKE_VRT_CMD = ./vks2vrt.py --mode=$(MODE) $(VKS2VRT_COMMON_OPTS) \
		$(VKS2VRT_OPTS)

SRC_FILES = *.sen

include ../../corp-common.mk
