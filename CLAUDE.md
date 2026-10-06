# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Scripts and data for converting and processing corpora into VRT (VeRticalized Text) for CWB and Korp at Kielipankki (the Language Bank of Finland). The repository is public: never commit corpus data, passwords or keys.

## Layout

- `scripts/`: general scripts, grouped by prefix (`korp-*`, `cwbdata-*`, `vrt-*`). `korp-make` is the main end-to-end corpus build script. Bash libraries are in `scripts/shlib/`, loaded via `scripts/korp-lib.sh`.
- `vrt-tools/`: FIN-CLARIN VRT Tools, the actively developed tool set. Library in `libvrt/`, one module per tool in `libvrt/tools/`. Older modules (`vrtargslib.py`, `vrtnamelib.py`, `vrtargsoolib.py`) are still in use.
- `scripttestlib/`: pytest library for testing command-line scripts (not the PyPI `scripttest`). Shared with `vrt-tools` and `rel-tools` via symlinked `conftest.py` and `test_scripts.py`.
- `corp/`: per-corpus scripts, data and docs. The Makefiles there (`corp-common.mk`, `corp/Makefile`) are obsolete; ignore them.
- `docs/`: corpus publishing how-tos (workflow docs, not code conventions).
- `rel-tools/`: `rel-*` relational TSV tools (not a current focus).
- Scripts find each other via relative paths such as `$progdir/../vrt-tools` and `$progdir/../corp`, so keep the directory layout stable.

## Tests

No Makefile or CI; run pytest manually:

- `cd vrt-tools && pytest tests/`
- `pytest -k test_scripts` (all scripttestlib tests); `pytest -k <script-name>` (one script)
- `pytest tests/libvrt/test_x.py::Class::test`

For new script tests prefer scripttestlib (`scripttest_*.yaml` or `.py`; cases have `input.cmdline`, `input.stdin`, `output.stdout/stderr/returncode`). `scripttestlib/make-scripttest -- cmd args < input` generates a scaffold. `rel-tools/check/` uses `libtest.sh`.

## Code style

- Bash, sh and Python 3 (target 3.10; much code is older). Shebangs: `#! /bin/bash`, `#! /bin/sh`, or `#! /usr/bin/env python3` followed by `# -*- mode: Python; -*-`.
- Lines at most 80 characters; spaces only in new code (older files use tabs); no trailing whitespace.
- Python: single quotes for ordinary strings, `"""` for docstrings; type annotations and Google-style docstrings in new code.
- British English spelling with -ize (not -ise).
- Executables are kebab-case with no extension (`vrt-drop-attrs`, `korp-make`).
- vrt-tools pattern: a thin entry script (`from libvrt.tools.vrt_x import Cls; Cls().run()`) plus module `libvrt/tools/vrt_x.py` (underscores). The class subclasses `vrtargsoolib.InputProcessor` and defines `DESCRIPTION`, `ARGSPECS` (e.g. `('--verbose|v', 'help')`), `check_args` and `main(self, args, inf, ouf)`. Some tools use `libvrt.args` (`parsearguments`/`main`/`transput`) instead. Raise `BadData` for data errors and `BadCode` for internal errors (`libvrt.bad`).
- Shell option parsing: a multi-line `optspecs='...'` variable (`@ Section` headers, `name=METAVAR default`, indented help), processed via `shlib/opts.sh` and `scripts/shutil-make-optionhandler.py`; usage text is built from `usage_header` plus `optspecs`. Follow `scripts/korp-make`. Load libraries with `shlib_required_libs="..."` then `. $_shlibdir/loadlibs.sh`.

## Environment

`scripts/shlib/site.sh` maps `$HOSTNAME` to a site (roihu, puhti, taito, korp, nyklait-09-01) and sets default corpus roots, CWB bin dirs and file groups. Most scripts assume the CSC/Korp server layout and external tools (CWB, MySQL), and will not run in a generic environment.

## Git

- Default branch is `master`. Small changes may go directly to master; larger ones use branches (e.g. `dev-*`) and PRs.
- Commit messages for tools: `path-or-tool: Area: Imperative summary` (e.g. `shlib/site.sh: Add support for CSC Roihu HPC environment`).
- The working tree usually holds many untracked scratch files (data, backups, session transcripts). Stage files explicitly; never `git add -A` or `git add .`. Use `git ls-files` to see what is really in the repo, and do not treat untracked files as conventions.
