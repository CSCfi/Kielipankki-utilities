# -*- coding: utf-8 -*-


include ../../corp-common.mk


VNS2VRT = ./vns2vrt.py


$(CORPNAME).vrt: $(FILES) $(VNS2VRT)
	$(VNS2VRT) $(VNS2VRT_OPTS) $(FILES) > $@
