#! /bin/sh
# -*- coding: utf-8 -*-

# Extract from a Corpus Workbench corpus the information to be written
# to the info file of the corpus: the total number of sentences and
# the date of the last update.
#
# Usage: cwbdata-extract-info corpus > .info

CWB_BINDIR=/usr/local/cwb/bin
CWB_REGDIR=/v/corpora/registry

sentcount=`
$CWB_BINDIR/cwb-describe-corpus -r $CWB_REGDIR -s $1 |
grep -E 's-ATT sentence +' |
sed -e 's/.* \([0-9][0-9]*\) .*/\1/'`

CORPDIR=`
$CWB_BINDIR/cwb-describe-corpus -r $CWB_REGDIR $1 |
grep '^home directory' |
sed -e 's/.*: //'`

updated=`
ls -lt --time-style=long-iso "$CORPDIR" |
head -2 |
tail -1 |
awk '{print $6}'`

echo Sentences: $sentcount
echo Updated: $updated
