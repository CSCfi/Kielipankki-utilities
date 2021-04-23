# -*- coding: utf-8 -*-

# shlib/base.sh
#
# Generic initialization code for Bourne shell scripts: temporary
# directory and tab character


# The tab character
tab='	'

# Directory for temporary files
tmpdir=

# First try the values of environment variables; use the first whose
# value is set and the directory is writable, regardless of the free
# space.
tmpdir_vars="
    $LOCAL_SCRATCH
    $TMPDIR
    $TEMPDIR
    $TMP
    $TEMP
"
for tmpdir_cand in $tmpdir_vars; do
    if [ "$tmpdir_cand" != "" ] && [ -w $tmpdir_cand ]; then
        tmpdir=$tmpdir_cand
        break
    fi
done

# If none of the above was available, choose the one of those listed
# below with most free space.
# FIXME: This does not always work well, as e.g. $TMPDIR is chosen if
# it is defined even if it is very small (as by default in Puhti
# compute nodes). We now rely on the user to set TMPDIR appropriately
# in such cases. But would we be able to do any better as a filesystem
# with more space might be much slower?
if [ "x$tmpdir" = "x" ]; then
    default_tmpdirs=${default_tmpdirs:-"
			 /tmp
			 /var/tmp
			 .
			 $HOME/tmp
			 $HOME
		      "}
    tmpdir_cands=
    # Find the directories that are writable
    for tmpdir_cand in $default_tmpdirs; do
	if [ -w $tmpdir_cand ]; then
	    tmpdir_cands="$tmpdir_cands $tmpdir_cand"
	fi
    done
    # Find the directory with the most free space: first find the
    # number of the dir in $tmpdir_cands, then choose the dir with
    # that number. Note that this does not take any quotas into
    # account; could it?
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
