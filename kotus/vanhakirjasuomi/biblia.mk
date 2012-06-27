# -*- coding: utf-8 -*-


include ../../corp-common.mk


FILES = vt4_prof.sen

P_ATTRS = 
S_ATTRS = work:0+code book:0+code chapter:0+code verse:0+code \
		sentence:0+id+code+page


$(CORPNAME).vrt: $(FILES)
	iconv -flatin1 $^ \
	| ./vks2vrt.py > $@
