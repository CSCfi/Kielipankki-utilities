# -*- coding: utf-8 -*-


all: $(wildcard *.mk)
	for makefile in $^; do \
		$(MAKE) -f $$makefile CORPNAME=vks_`basename $$makefile .mk`; \
	done
