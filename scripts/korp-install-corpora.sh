#! /bin/sh
# -*- coding: utf-8 -*-

# Install Korp corpora of the latest corpora package

# TODO:
# - Multiple or timestamped backups
# - Backup to a different backup directory
# - Verbosity control
# - Resume a partial installation, e.g., no or only some database
#   files installed
# - Possibly write to the log also partial installations (when CWB
#   files have been installed but database files not)


progname=`basename $0`
progdir=`dirname $0`


usage_header="Usage: $progname [options] corpus|package ...

Install or update the specified corpora from corpus packages to Corpus
Workbench and Korp database.

The arguments may be either corpus package file names, possibly with a full
path name, or corpus names, in which case packages for the corpus are searched
for in the package directory. A full path name may be preceded by a remote
host name and a colon, in which case the package is retrieved from the remote
host without a need to make a local copy of the package file."

optspecs='
c|corpus-root=DIR "$corpus_root"
    use DIR as the root directory of corpus files (CORPUS_ROOT)
p|package-dir=DIR "CORPUS_ROOT/$pkgsubdir" pkgdir
    DIR is the default directory in which to search for corpus
    packages to be installed; may be a remote directory specified as
    HOST:DIR
no-backups !backups
    do not make backup copies of existing corpus files
backup-suffix=SUFFIX ".bak"
    use SUFFIX as the backup file suffix
f|force
    force installing a corpus package that is older than or as old as
    the currently installed package
delay-database-import delay_db
    begin importing database data only after all corpus packages have
    been extracted
n|dry-run
    only report corpus packages that would be installed, but do not
    actually install them
'

usage_footer="Note: The backup copy of a corpus is overwritten by subsequent updates of the
corpus."


pkgsubdir=pkgs


. $progdir/korp-lib.sh

# Process options
eval "$optinfo_opt_handler"


# This is only for compatibility with older corpus packages
pkg_prefix=korpdata_

filelistfile=$tmp_prefix.files
pkglistfile=$tmp_prefix.pkgs

timestamp_format="+%Y-%m-%dT%H:%M:%S"


if [ "x$1" = x ]; then
    error "Please specify the names of corpus packages or corpora to install.
For more information, run '$0 --help'."
fi

if [ "x$pkgdir" = "xCORPUS_ROOT/$pkgsubdir" ]; then
    pkgdir=${CORPUS_PKGDIR:-$corpus_root/$pkgsubdir}
fi

localhost=LOCALHOST
default_pkghost=$localhost
case $pkgdir in
    *:* )
	default_pkghost=${pkgdir%%:*}
	pkgdir=${pkgdir#*:}
	;;
esac

installed_list=$corpus_root/korp_installed_corpora.list

if [ ! -e "$installed_list" ]; then
    touch "$installed_list"
    ensure_perms "$installed_list"
fi


host_is_remote () {
    test "x$1" != x$localhost && test "x$1" != x
}

get_package_corpus_name () {
    local corpname
    corpname=${1##*/}
    corpname=${corpname%.t?z}
    corpname=${corpname%.tar.*}
    case "$1" in
	"$pkgprefix*" )
            corpname=${corpname##$pkgprefix}
            ;;
	* )
	    corpname=${corpname%_korp_20*}
	    ;;
    esac
    echo "$corpname"
}

run_command () {
    if host_is_remote "$1"; then
	# ssh may not read anything from stdin, so that higher-level
	# read works; see https://unix.stackexchange.com/a/107801
	ssh "$1" "$2" < /dev/null
    else
	eval "$2"
    fi
}

find_corpus_packages () {
    local pkgspec pkghost use_find current_pkgdir pkgname_cond ls_cmd cmd \
	  mode links owner group size timestamp pkgname
    pkgspec=$1
    pkghost=$default_pkghost
    use_find=1
    current_pkgdir=$pkgdir
    case $pkgspec in
	*:* )
	    pkghost=${pkgspec%%:*}
	    pkgspec=${pkgspec#*:}
	    ;;
    esac
    # TODO: If $pkgspec is a directory, find packages in it and its
    # subdirectories
    case $pkgspec in
	*/*.* )
	    use_find=
	    ;;
	*/* )
	    current_pkgdir=$pkgspec
	    pkgname_cond="-name \*_korp_20\*.t?z -o -name \*_korp_20\*.tar.\* -o -name $pkg_prefix\*.t?z -o -name $pkg_prefix\*.tar.*"
	    ;;
	*.* )
	    pkgname_cond="-name $pkgspec"
	    ;;
	* )
	    pkgname_cond="-name ${pkgspec}_korp_20\*.t?z -o -name ${pkgspec}_korp_20\*.tar.\* -o -name $pkg_prefix$pkgspec.t?z -o -name $pkg_prefix$pkgspec.tar.*"
	    ;;
    esac
    # Use -v "natural sort of (version) numbers" of GNU ls to use the
    # latest package by the timestamp in the package name, as the
    # timestamp of the file may have changed e.g. in copying.
    ls_cmd="ls -lvr --time-style=$timestamp_format --dereference"
    if [ "x$use_find" = x ]; then
	cmd="$ls_cmd $pkgdir/$pkgspec $pkgspec 2> /dev/null"
    else
	cmd="find $current_pkgdir $maxdepth_opt $pkgname_cond | xargs --no-run-if-empty $ls_cmd"
    fi
    run_command "$pkghost" "$cmd" |
    while read mode links owner group size timestamp pkgname; do
	printf "%s\t%s\t%s\t%s\t%s\n" $(get_package_corpus_name $pkgname) \
	     $pkghost "$pkgname" $timestamp $size
    done
}

find_package_candidates () {
    local listfile
    listfile=$1
    shift
    touch $listfile
    for pkgspec in "$@"; do
	find_corpus_packages "$pkgspec" > $listfile.tmp
	if [ -s $listfile.tmp ]; then
	    grep -Fvx -f$listfile < $listfile.tmp >> $listfile
	else
	    warn "No matching corpus packages found: $pkgspec"
	fi
    done
}

format_package_name_host () {
    if host_is_remote "$2"; then
	printf $2:
    fi
    printf "%s\n" $1
}

get_package_name_date () {
    # Get package date with the possible running number suffix of up
    # to 9999
    local date suffix
    date=$1
    # Remove everything up to and including the last underscore
    date=${date##*_}
    # Remove extension(s)
    date=${date%%.*}
    # Separate suffix
    suffix=${date#*-}
    # If no suffix, default to 0
    if [ $suffix = $date ]; then
        suffix=0
    fi
    # Remove suffix from date
    date=${date%-*}
    printf "%s%04d" "$date" "$suffix"
}

package_is_not_newer () {
    [ "$(get_package_name_date $1)" -le "$(get_package_name_date $2)" ]
}

filter_corpora () {
    local listfile corpname_prev corp_pkgfile \
	  corpname pkghost pkgfile timestamp pkgsize installed_pkg \
	  formatted_pkgname not_newer_msg
    listfile=$1
    corpname_prev=
    corp_pkgfile=
    # global corpora_to_install
    corpora_to_install=
    # The following cannot be a pipeline because the values of the
    # variables would not be retained.
    sort -t"	" -s -k1,1 -k3,3Vr $listfile > $listfile.srt
    while read corpname pkghost pkgfile timestamp pkgsize; do
	if [ "x$corpname" = "x$corpname_prev" ]; then
	    :
	    # TODO: Show this only with --verbose
	    # echo "  $corpname: skipping $pkgfile as older than $corp_pkgfile" >> /dev/stderr
	else
	    installed_pkg=$(grep -E "^[^	]+	$corpname	" $installed_list \
		| cut -d'	' -f3 \
		| sort -Vr \
		| head -1)
	    corpname_prev=$corpname
	    if package_is_not_newer "$pkgfile" "$installed_pkg"; then
		formatted_pkgname="$(format_package_name_host $pkgfile $pkghost)"
		not_newer_msg="not newer than the installed package ($installed_pkg)"
		if [ "x$force" != x ]; then
		    echo "  $corpname: installing $formatted_pkgname because of --force, even though $not_newer_msg" >> /dev/stderr
		else
		    echo "  $corpname: skipping $formatted_pkgname as $not_newer_msg" >> /dev/stderr
		    continue
		fi
	    fi
	    printf "%s\t%s\t%s\t%s\t%s\n" $corpname $pkghost "$pkgfile" \
		$timestamp $pkgsize
	    corpora_to_install="$corpora_to_install $corpname"
	    corp_pkgfile=$pkgfile
	fi
    done < $listfile.srt
}

get_tar_compress_opt () {
    case "$1" in
	*.gz | *.tgz )
	    echo --gzip
	    ;;
	*.tbz | *.bz | *.bz2 )
	    echo --bzip2
	    ;;
	*.xz | *.txz )
	    echo --xz
	    ;;
    esac
}

backup_corpus () {
    local pkgname pkghost tar_cmd backup_msg_shown
    pkgname=$1
    pkghost=$2
    echo "  Checking for existing corpus files"
    tar_cmd="tar tf $pkgname $(get_tar_compress_opt $pkgname) \
            --wildcards --wildcards-match-slash \
	    --transform 's,.*/\(data\|registry\|sql\)/,\1/,' \
	    --show-transformed-names '*/data' '*/registry' '*/sql'"
    backup_msg_shown=
    run_command "$pkghost" "$tar_cmd" |
    cut -d/ -f1,2 |
    sort -u |
    while read fname; do
	if [ -e $corpus_root/$fname ]; then
	    if [ "x$backup_msg_shown" = x ]; then
		echo "  Backing up existing corpus files"
		backup_msg_shown=1
	    fi
	    cp -dpr $corpus_root/$fname $corpus_root/$fname$backup_suffix
	    ensure_perms $corpus_root/$fname$backup_suffix
	fi
    done
}

human_readable_size () {
    local kb
    kb=$(($1 / 1024))
    if [ "$kb" -lt 10240 ]; then
	echo "$kb KiB"
    else
	echo "$(($kb / 1024)) MiB"
    fi
}

# Return the size of a file in a human-readable format
filesize () {
    human_readable_size $(du -bs $1 | cut -f1)
}

adjust_registry () {
    local filelistfile regfile corpus_id datadir
    # This assumes that the target datadir is
    # $corpus_root/data/$corpus_id
    filelistfile=$1
    grep registry/ $filelistfile |
    while read regfile_base; do
	regfile=$corpus_root/$regfile_base
	corpus_id=${regfile_base##*/}
	datadir=$(echo "$regfile" | sed -e 's,/registry/,/data/,')
	if ! grep -E -ql $corpus_root $regfile 2> /dev/null; then
	    mv $regfile $regfile.orig
	    sed -e "s,^HOME .*,HOME $datadir," \
                -e "s,^INFO .*/\.info,INFO $datadir/.info," \
		$regfile.orig > $regfile
	    touch --reference=$regfile.orig $regfile
	    ensure_perms $regfile
	    rm $regfile.orig
	fi
    done
}

install_file_sql () {
    local sqlfile db
    sqlfile=$1
    db=$korpdb
    case $sqlfile in
	*_auth_* )
	    db=$korpdb_auth
	    ;;
    esac
    comprcat $sqlfile \
	| mysql $mysql_opts $db
    return $?
}

install_file_tsv () {
    local tsvfile
    tsvfile=$1
    $progdir/korp-mysql-import.sh --prepare-tables $tsvfile
    return $?
}

install_dbfiles () {
    local type filelistfile msg files
    type=$1
    filelistfile=$2
    msg=$3
    files=`grep -E '\.'$type'(\.(bz2|gz|xz))?$' $filelistfile`
    if [ "x$files" != "x" ]; then
	echo "  $msg data into MySQL database"
	for file in $files; do
	    echo "    $file (size `filesize $corpus_root/$file`)"
	    install_file_$type "$corpus_root/$file"
	    if [ $? -ne 0 ]; then
		error "Errors in loading $file"
	    fi
	done
    fi
}

install_db () {
    local filelistfile
    filelistfile=$1
    install_dbfiles sql $filelistfile Loading
    install_dbfiles tsv $filelistfile Importing
}

install_corpus () {
    local corp corpus_pkg pkgtime pkgsize pkghost install_base_msg
    corp=$1
    corpus_pkg=$2
    pkgtime=$3
    pkgsize=$4
    pkghost=$5
    install_base_msg="$corp from $(format_package_name_host $corpus_pkg $pkghost) (compressed size $(human_readable_size $pkgsize))"
    echo
    if [ "x$dry_run" != x ]; then
	echo "Would install $install_base_msg (dry run)"
	return
    fi
    echo "Installing $install_base_msg"
    if [ "x$backups" != x ]; then
	backup_corpus $corpus_pkg $pkghost
    fi
    echo "  Copying CWB files"
    run_command "$pkghost" "cat '$corpus_pkg'" |
    tar xvp -C $corpus_root -f- $(get_tar_compress_opt $corpus_pkg) \
	--wildcards --wildcards-match-slash \
	--transform 's,.*/\(data\|registry\|sql\)/,\1/,' \
	--show-transformed-names '*/data' '*/registry' '*/sql' 2>&1 \
	| tee $filelistfile \
	| sed -e 's/^/    /'
    # Allow missing directory sql
    if grep '^tar:' $filelistfile > $tmp_prefix.tar_errors; then
	if grep -E -q -v \
	    '(\*/sql: Not found|Cannot (utime|change mode)|Exiting with failure)' \
	    $tmp_prefix.tar_errors;
	then
	    error "Errors in extracting $corpus_pkg"
	else
	    warn "Ignoring non-fatal extraction errors"
	fi
    fi
    (
	cd $corpus_root
	ensure_perms $(cat $filelistfile)
    )
    adjust_registry $filelistfile
    if [ "x$delay_db" != x ]; then
	echo "  (Delaying installing database files)"
	cp -p $filelistfile $filelistfile.$corp
    else
	install_corpus_step2 $filelistfile $corp "$corpus_pkg" $pkgtime
    fi
}

install_corpus_step2 () {
    local filelistfile corp corpus_pkg pkgtime
    filelistfile=$1
    corp=$2
    corpus_pkg=$3
    pkgtime=$4
    install_db $filelistfile
    # Log to the list of installed corpora: current time, corpus name,
    # package file name, package file modification time, installing
    # user
    printf "%s\t%s\t%s\t%s\t%s\n" \
	$(date "$timestamp_format") $corp $(basename "$corpus_pkg") \
	$pkgtime $(whoami) >> $installed_list
}

install_corpora () {
    local pkglistfile dry_run_msg corpname pkghost pkgfile pkgtime pkgsize
    pkglistfile=$1
    dry_run_msg=
    if [ "x$dry_run" != x ]; then
	dry_run_msg=" (dry run)"
    fi
    echo
    echo "Installing Korp corpora$dry_run_msg:"
    for corp in $corpora_to_install; do
	echo "  $corp"
    done
    while read corpname pkghost pkgfile pkgtime pkgsize; do
	install_corpus $corpname "$pkgfile" $pkgtime $pkgsize $pkghost
    done < $pkglistfile
    if [ "x$delay_db" != x ] && [ "x$dry_run" = x ]; then
	echo
	echo Installing database files
	while read corpname pkghost pkgfile pkgtime pkgsize; do
	    install_corpus_step2 \
		$filelistfile.$corpname $corpname "$pkgfile" $pkgtime
	done < $pkglistfile
    fi
    echo
    echo "Installation complete$dry_run_msg"
}


echo Searching for corpus packages to install
find_package_candidates $pkglistfile.base "$@"
if [ ! -s $pkglistfile.base ]; then
    error "No matching corpus packages found"
fi

# The following two cannot be in a pipeline, because the former
# constructs the value of the variable corpora_to_install that the
# latter uses
filter_corpora $pkglistfile.base > $pkglistfile
if [ "x$corpora_to_install" = x ]; then
    error "No corpora to install"
fi
install_corpora $pkglistfile
