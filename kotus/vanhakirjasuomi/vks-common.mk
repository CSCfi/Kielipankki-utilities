# -*- coding: utf-8 -*-


include ../../corp-common.mk


VKS2VRT = ./vks2vrt.py


$(CORPNAME).vrt: $(FILES) $(VKS2VRT)
	iconv -flatin1 -tutf8 $(FILES) \
	| $(VKS2VRT) --mode=$(MODE) > $@
