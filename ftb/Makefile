# -*- coding: utf-8 -*-


CORPORA = $(basename $(filter-out %-common.mk,$(wildcard *.mk)))

TARGETS = vrt reg korp_db


.PHONY: all $(CORPORA)


all: $(CORPORA)

# Define rules for targets $(CORPORA) and $(CORPORA)@$(TARGET)

define MAKE_CORPUS_R
$(1)$(if $(subst @,,$(2)),@$(2)):
	$$(MAKE) -f $(1).mk $(subst @,,$(2)) CORPNAME=$(1)
endef

$(foreach corp,$(CORPORA),\
	$(foreach targ,$(TARGETS) @,\
		$(eval $(call MAKE_CORPUS_R,$(corp),$(targ)))))
