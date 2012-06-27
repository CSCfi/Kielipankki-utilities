# -*- coding: utf-8 -*-


CORPNAME = vks


include ../../corp-common.mk


P_ATTRS = 
S_ATTRS = work:0+code book:0+code chapter:0+code verse:0+code \
		sentence:0+id+code+page


$(CORPNAME).vrt: vt4_prof.sen
	iconv -flatin1 $< \
	| ./vks2vrt.py > $@
