#! /bin/sh
# -*- coding: utf-8 -*-

# Install Korp corpora of the latest corpora package

# TODO:
# - Multiple or timestamped backups
# - Backup to a different backup directory
# - Option to force installing a package file older than the currently
#   installed version
# - Verbosity control
# - Ignore tar errors of missing sql directory
# - Convert to using korp-lib.sh


progname=`basename $0`
progdir=`dirname $0`


# TODO: Replace much of the following initialization code with
# sourcing korp-lib.sh

# Korp MySQL database
korpdb=korp
korpdb_auth=korp_auth
# Unless specified via environment variables, assume that the Korp
# MySQL database user and password are specified in a MySQL option
# file
mysql_opts=
if [ "x$KORP_MYSQL_USER" != "x" ]; then
    mysql_opts=--user=$KORP_MYSQL_USER
fi
if [ "x$KORP_MYSQL_PASSWORD" != "x" ]; then
    mysql_opts="$mysql_opts --password=$KORP_MYSQL_PASSWORD"
fi
if [ "x$KORP_MYSQL_BIN" != "x" ]; then
    mysql_bin=$KORP_MYSQL_BIN
elif [ -x /opt/mariadb/bin/mysql ]; then
    # MariaDB on the Korp server
    mysql_bin="/opt/mariadb/bin/mysql --defaults-extra-file=/var/lib/mariadb/my.cnf"
else
    mysql_bin=mysql
fi

default_corpus_roots="/v/corpora /proj/clarin/korp/corpora $WRKDIR/corpora /wrk/jyniemi/corpora"

find_existing_dir () {
    _test=$1
    _file=$2
    shift 2
    for dir in "$@"; do
	if [ $_test $dir/$_file ]; then
	    echo $dir
	    break
	fi
    done
}

# Root directory, relative to which the corpus directory resides
corpus_root=${CORPUS_ROOT:-$(find_existing_dir -d "" $default_corpus_roots)}

pkgsubdir=pkgs

# This will be set later based on $corpus_root, which may be modified
# by options
pkgdir=$CORPUS_PKGDIR

backups=1
backup_suffix=.bak

# This is only for compatibility with older corpus packages
pkg_prefix=korpdata_

tmpdir=${TMPDIR:-${TEMPDIR:-${TMP:-${TEMP:-/tmp}}}}
tmp_prefix=$tmpdir/$progname

filelistfile=$tmp_prefix.files.$$
pkglistfile=$tmp_prefix.pkgs.$$

timestamp_format="+%Y-%m-%dT%H:%M:%S"

filegroup=
for grp in korp clarin; do
    if groups | grep -qw $grp; then
	filegroup=$grp
	break
    fi
done
if [ "x$filegroup" = x ]; then
    filegroup=`groups | cut -d' ' -f1`
fi


ensure_perms () {
    chgrp -R $filegroup "$@" 2> /dev/null
    chmod -R g=u "$@" 2> /dev/null
}

warn () {
    echo "$progname: Warning: $1" >&2
}

error () {
    echo "$progname: $1" >&2
    exit 1
}

cleanup () {
    if [ "x$tmp_prefix" != "x" ]; then
	rm -rf $tmp_prefix.*
    fi
}

cleanup_abort () {
    cleanup
    exit 1
}


trap cleanup 0
trap cleanup_abort 1 2 13 15


usage () {
    cat <<EOF
Usage: $progname [options] corpus|package ...

Install or update the specified corpora from corpus packages to Corpus
Workbench and Korp database.

The arguments may be either corpus package file names, possibly with a full
path name, or corpus names, in which case packages for the corpus are searched
for in the package directory. A full path name may be preceded by a remote
host name and a colon, in which case the package is retrieved from the remote
host without a need to make a local copy of the package file.

Options:
  -h, --help      show this help
  -c, --corpus-root DIR
                  use DIR as the root directory of corpus files (default:
                  $corpus_root)
  -p, --package-dir DIR
                  DIR is the default directory in which to search for corpus
                  packages to be installed; may be a remote directory
                  specified as HOST:DIR (default: CORPUS_ROOT/$pkgsubdir)
  --no-backups    do not make backup copies of existing corpus files
  --backup-suffix SUFFIX
                  use SUFFIX as the backup file suffix (default: $backup_suffix)

Note: The backup copy of a corpus is overwritten by subsequent updates of the
corpus.
EOF
    exit 0
}


# Test if GNU getopt
getopt -T > /dev/null
if [ $? -eq 4 ]; then
    # This requires GNU getopt
    args=`getopt -o "hcp:r:" -l "help,corpus-root:,package-dir:,no-backups,backup-suffix:" -n "$progname" -- "$@"`
    if [ $? -ne 0 ]; then
	exit 1
    fi
    eval set -- "$args"
fi
# If not GNU getopt, arguments of long options must be separated from
# the option string by a space; getopt allows an equals sign.

# Process options
while [ "x$1" != "x" ] ; do
    case "$1" in
	-h | --help )
	    usage
	    ;;
	-c | --corpus-root )
	    corpus_root=$2
	    shift
	    ;;
	-p | --package-dir )
	    pkgdir=$2
	    shift
	    ;;
	--no-backups )
	    backups=
	    ;;
	--backup-suffix )
	    backup_suffix=$2
	    shift
	    ;;
	-- )
	    shift
	    break
	    ;;
	--* )
	    warn "Unrecognized option: $1"
	    ;;
	* )
	    break
	    ;;
    esac
    shift
done

if [ "x$1" = x ]; then
    error "Please specify the names of corpus packages or corpora to install.
For more information, run '$0 --help'."
fi

pkgdir=${pkgdir:-$corpus_root/$pkgsubdir}

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
	ssh "$1" "$2"
    else
	eval "$2"
    fi
}

find_corpus_packages () {
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
    ls_cmd="ls -lt --time-style=$timestamp_format --dereference"
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

filter_corpora () {
    listfile=$1
    corpname_prev=
    corp_pkgfile=
    corpora_to_install=
    # The following cannot be a pipeline because the values of the
    # variables would not be retained.
    sort -t"	" -s -k1,1 -k4,4r $listfile > $listfile.srt
    while read corpname pkghost pkgfile timestamp pkgsize; do
	if [ "x$corpname" = "x$corpname_prev" ]; then
	    :
	    # TODO: Show this only with --verbose
	    # echo "  $corpname: skipping $pkgfile as older than $corp_pkgfile" >> /dev/stderr
	else
	    installed_date=$(grep -E "^[^	]+	$corpname	" $installed_list \
		| cut -d'	' -f4 \
		| sort -r \
		| head -1)
	    if expr "$timestamp" "<=" "$installed_date" > /dev/null; then
		echo "  $corpname: skipping $(format_package_name_host $pkgfile $pkghost) as not newer than the installed package ($timestamp <= $installed_date)" >> /dev/stderr
	    else
		printf "%s\t%s\t%s\t%s\t%s\n" $corpname $pkghost "$pkgfile" \
		    $timestamp $pkgsize
		corpora_to_install="$corpora_to_install $corpname"
	    fi
	    corpname_prev=$corpname
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

# Cat possibly compressed file(s) based on the file name extension
comprcat () {
    case $1 in
	*.bz2 )
	    bzcat "$@"
	    ;;
	*.gz )
	    zcat "$@"
	    ;;
	*.xz )
	    xzcat "$@"
	    ;;
	* )
	    cat "$@"
	    ;;
    esac
}

human_readable_size () {
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
    # FIXME: This probably does not work correctly if datadir is other
    # than $corpus_root/data/$corpus_id
    filelistfile=$1
    grep registry/ $filelistfile |
    while read regfile_base; do
	regfile=$corpus_root/$regfile_base
	corpus_id=${regfile_base##*/}
	datadir=$(echo "$regfile" | sed -e 's,/registry/,/data/,')
	if ! grep -E -ql $corpus_root $regfile 2> /dev/null; then
	    mv $regfile $regfile.orig
	    sed -e "s,^\(HOME\|INFO\) .*/$corpus_id\(/[^/]*\)\?,\1 $datadir\2," \
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
    tsvfile=$1
    $progdir/korp-mysql-import.sh --prepare-tables $tsvfile
    return $?
}

install_dbfiles () {
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
    filelistfile=$1
    install_dbfiles sql $filelistfile Loading
    install_dbfiles tsv $filelistfile Importing
}

convert_timedata () {
    filelistfile=$1
    echo "Converting time data"
    # Find the physical (CWB) corpora in the corpus package
    corpora=$(grep -E '^registry' $filelistfile | sed -e 's,.*/,,')
    for corp in $corpora; do
	$progdir/korp-convert-timedata.sh $corp
    done
}

install_corpus () {
    corp=$1
    corpus_pkg=$2
    pkgtime=$3
    pkgsize=$4
    pkghost=$5
    echo
    echo "Installing $corp from $(format_package_name_host $corpus_pkg $pkghost) (compressed size $(human_readable_size $pkgsize))"
    if [ "x$backups" != x ]; then
	backup_corpus $corpus_pkg $pkghost
    fi
    echo "  Copying CWB files"
    run_command "$pkghost" "cat '$corpus_pkg'" |
    tar xvp -C $corpus_root -f- $(get_tar_compress_opt $pkgname) \
	--wildcards --wildcards-match-slash \
	--transform 's,.*/\(data\|registry\|sql\)/,\1/,' \
	--show-transformed-names '*/data' '*/registry' '*/sql' 2>&1 \
	| tee $filelistfile \
	| sed -e 's/^/    /'
    # Allow missing directory sql
    if grep '^tar:' $filelistfile |
	grep -E -v '^tar: (\*/sql: Not found|Exiting with failure)';
    then
	error "Errors in extracting $corpus_pkg"
    fi
    (
	cd $corpus_root
	ensure_perms $(cat $filelistfile)
    )
    adjust_registry $filelistfile
    install_db $filelistfile
    convert_timedata $filelistfile
    # Log to the list of installed corpora: current time, corpus name,
    # package file name, package file modification time, installing
    # user
    printf "%s\t%s\t%s\t%s\t%s\n" \
	$(date "$timestamp_format") $corp $(basename "$corpus_pkg") \
	$pkgtime $(whoami) >> $installed_list
}

install_corpora () {
    echo
    echo Installing Korp corpora:
    for corp in $corpora_to_install; do
	echo "  $corp"
    done
    while read corpname pkghost pkgfile pkgtime pkgsize; do
	install_corpus $corpname "$pkgfile" $pkgtime $pkgsize $pkghost
    done
    echo
    echo Installation complete
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
install_corpora < $pkglistfile