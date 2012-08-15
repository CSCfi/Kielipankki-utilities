# -*- coding: utf-8 -*-


CORPNAME_PREFIX = vns_

# Even though the encoding of the input XML files is ISO Latin-1, they
# should not converted to UTF-8, since the encoding is specified in
# the XML declaration and the script works correctly with it.

MAKE_VRT_CMD = ./vns2vrt.py $(VNS2VRT_OPTS)

include ../../corp-common.mk
