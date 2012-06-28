# -*- coding: utf-8 -*-


all: $(filter-out %-common.mk,$(wildcard *.mk))
	for makefile in $^; do \
		$(MAKE) -f $$makefile CORPNAME=vks_`basename $$makefile .mk`; \
	done
