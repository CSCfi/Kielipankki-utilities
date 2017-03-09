# Kielipankki-konversio

This repository contains software (scripts) and associated data for
importing, converting and other processing of (corpus) data in
Kielipankki.

Corpus data itself should *not* be included in this repository.


## Directory structure

In general, the top-level directory structure is as follows:

* `corp/`: corpus-specific scripts (and associated data), containing
  subdirectories by corpus, group of corpora, corpus origin (owner) or
  corpus type (such as speech)
* `fulltext/`: scripts to be included on corpus full-text HTML pages
* `scripts/`: general-purpose scripts

For a major subsystems of scripts, such as harvesting or parsing, you
may add a top-level directory of its own, or alternatively, a
subdirectory under `scripts/`.

If you are unsure about where you should put your scripts in
development, you can develop them in a private branch first and merge
it to the master only when they are relatively stable.
