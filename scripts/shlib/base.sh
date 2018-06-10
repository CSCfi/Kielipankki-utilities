# -*- coding: utf-8 -*-

# shlib/base.sh
#
# Generic initialization code for Bourne shell scripts: temporary
# directory and tab character


# The tab character
tab='	'

# Directory for temporary files
tmpdir=${TMPDIR:-${TEMPDIR:-${TMP:-$TEMP}}}
if [ "x$tmpdir" = "x" ]; then
    default_tmpdirs=${default_tmpdirs:-"/tmp /var/tmp"}
    tmpdir_cands=
    # Find the directories that are writable
    for tmpdir_cand in $default_tmpdirs; do
	if [ -w $tmpdir_cand ]; then
	    tmpdir_cands="$tmpdir_cands $tmpdir_cand"
	fi
    done
    # Find the directory with the most free space: first find the
    # number of the dir in $tmpdir_cands, then choose the dir with
    # that number.
    tmpdir_num=$(
	df $tmpdir_cands |
	tail -n+2 |
	cat -n |
	awk '{print $1 "\t" $5}' |
	sort -s -k2,2nr |
	head -1 |
	cut -d"$tab" -f1
    )
    tmpdir=$(echo $tmpdir_cands | cut -d' ' -f$tmpdir_num)
fi
tmp_prefix=$tmpdir/$progname.$$
