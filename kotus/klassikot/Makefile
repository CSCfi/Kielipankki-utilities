# -*- coding: utf-8 -*-


CORPNAME_BASE = kotus_klassikot

MAKE_VRT_CMD = ../../scripts/tei2vrt.py --mode=stories --tokenize --para-as-sent

SRC_FILES = pakkala_lapsia.xml

P_ATTRS = 
S_ATTRS = text:0+distributor+source+title collection:0+id story:0+id \
		sentence:0+id+type


# Override the first target all-corp in corp-common.mk that assumes
# the existence of $(CORPNAME_BASE).mk.
all-override: all


include ../../corp-common.mk
