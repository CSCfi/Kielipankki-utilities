# -*- coding: utf-8 -*-


CORPNAME_MAIN = parole_sv
SUBCORPUS = parole_sv

# Make a package even if SUBCORPUS is defined, as lemmie-common.mk
# uses the value of SUBCORPUS in various places
MAKE_PKG = true


include lemmie-sv-common.mk
