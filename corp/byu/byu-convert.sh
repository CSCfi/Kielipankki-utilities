#! /bin/sh

# A wrapper script for byu-wlp2vrt.py, to avoid specifying PYTHONPATH
# on the command line


progdir=$(dirname $0)

PYTHONPATH=/proj/clarin/korp/git-work/korp-corpimport/scripts $progdir/byu-wlp2vrt.py "$@"
