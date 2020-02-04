# Kielipankki-utilities

This repository contains software (scripts) and associated data for
importing, converting and other processing of (corpus) data in
[Kielipankki – The Language Bank of
Finland](https://www.kielipankki.fi/language-bank/).

In particular, the repository contains scripts converting data to the
VRT (VeRticalized Text) format used as an input format for the [IMS
Open Corpus Workbench (CWB)](http://cwb.sourceforge.net/) and
[Korp](https://www.kielipankki.fi/support/korp/). Although many
scripts are specific to the Language Bank of Finland, some of them may
be more generally useful, or at least they may be adapted to other
environments.

**Note:** Corpus data itself should *not* be included in this public
repository. Neither should any secret or private information, such as
passwords.


## Directory structure

In general, the top-level directory structure is as follows:

* [`corp/`](corp/): corpus-specific scripts (and associated data),
  containing subdirectories by corpus, group of corpora, corpus origin
  (owner) or corpus type (such as speech)
* [`docs/`](docs/): general documentation on corpus processing
* [`fulltext/`](fulltext/): scripts to be included on corpus full-text
  HTML pages
* [`scripts/`](scripts/): general-purpose scripts
* [`vrt-tools/`](vrt-tools/): FIN-CLARIN VRT Tools: tools for
  processing VeRticalized Text data

For a major subsystems of scripts, such as harvesting or parsing, you
may add a top-level directory of its own, or alternatively, a
subdirectory under `scripts/`.

If you are unsure about where you should put your scripts in
development, you can develop them in a private branch first and merge
it to the master only when they are relatively stable.


## Repository background

This repository is the public successor of the previous
[Kielipankki-konversio](https://github.com/CSCfi/Kielipankki-konversio/)
repository that also contained some private data. The repository was
made public on 2020-02-04. Any further development should be done in
this repository.
