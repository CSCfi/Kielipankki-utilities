#! /bin/sh

# Install Korp corpora of the latest corpora package

# TODO:
# - If several packages for the same corpus exist in the same
#   directory, install only the latest one.
# - Backup (optionally?) the previous version of corpus data and
#   registry files, or at least warn if the corpus exists.
# - Options and a usage message.


# Corpus package directory
pkgdir=${CORPUS_PKGDIR:-.}
# Root directory, relative to which the corpus directory resides
rootdir=${ROOTDIR:-/v/corpora}

# Korp MySQL database
korpdb=korp
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

scriptname=`basename $0`
scriptdir=`dirname $0`

pkg_prefix=korpdata_

timestampfile=$pkgdir/korp_fi_latest_corpus_packages_newer.timestamp
installed_list=$pkgdir/korp_fi_installed_corpora.list

tmpdir=${tmpdir:-${TMPDIR:-$pkgdir}}
filelistfile=$tmpdir/$scriptname.files.$$

if [ ! -e "$installed_list" ]; then
    touch "$installed_list"
fi

get_pkg_fname () {
    corp=$1
    pkg_fnames=`for base in $pkg_prefix$corp ${corp}_korp_20\*; do echo "$pkgdir/$base.t?z $pkgdir/$base.tar*"; done`
    ls -t $pkg_fnames 2> /dev/null | head -1 | awk '{print $NF}'
}

if [ "x$1" != "x" ]; then
    corpora=
    for corp in "$@"; do
	corpus_pkg=`get_pkg_fname $corp`
	if [ "x$corpus_pkg" = "x" ]; then
	    echo "Cannot read a package file for corpus $corp; ignoring" \
		> /dev/stderr
	else
	    corpora="$corpora $corp"
	fi
    done
else
    if [ -e "$timestampfile" ]; then
	newer_cond="-newer $timestampfile"
    else
	echo "Timestamp file $timestampfile not found; considering all non-installed corpus packages in $pkgdir" > /dev/stderr
	newer_cond=
    fi
    corpora=`find $pkgdir -name $pkg_prefix\*.t?z -o -name $pkg_prefix\*.tar.* -o -name \*_korp_20\*.t?z -o -name \*_korp_20\*.tar.* $newer_cond \
	| sed -e "s/^.*$pkg_prefix//; s/^.*\/\(.*\)_korp_20.*/\1/; s/\.t.z//; s/\.tar\..*//" \
	| grep -Fvx -f$installed_list \
	| sort`
fi
if [ "x$corpora" = "x" ]; then
    echo "$scriptname: No corpora to install!"
    exit 1
fi

trap "echo Aborting installation; rm -f $filelistfile; exit 1" HUP INT QUIT

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

# Return the size of a file in a human-readable format
filesize () {
    kb=`du -ks $1 | cut -f1`
    if [ "$kb" -lt 10240 ]; then
	echo "$kb KiB"
    else
	echo "$(($kb / 1024)) MiB"
    fi
}


install_file_sql () {
    sqlfile=$1
    comprcat $rootdir/$sqlfile \
	| mysql $mysql_opts $korpdb
    return $?
}

install_file_tsv () {
    tsvfile=$1
    $scriptdir/korp-mysql-import.sh --prepare-tables $tsvfile
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
	    echo "    $file (size `filesize $rootdir/$file`)"
	    install_file_$type "$rootdir/$file"
	    if [ $? -ne 0 ]; then
		echo "$scriptname: Errors in loading $file"
		exit 1
	    fi
	done
    fi
}

install_db () {
    filelistfile=$1
    install_dbfiles sql $filelistfile Loading
    install_dbfiles tsv $filelistfile Importing
}

install_corpus () {
    corpus_pkg=`get_pkg_fname $corp`
    echo
    echo "Installing $corp (compressed size `filesize $corpus_pkg`)"
    echo "  Copying CWB files"
    tar xvap -C $rootdir -f $corpus_pkg --wildcards --wildcards-match-slash \
	--transform 's,.*/\(data\|registry\|sql\)/,\1/,' \
	--show-transformed-names '*/data' '*/registry' '*/sql' 2>&1 \
	| tee $filelistfile \
	| sed -e 's/^/    /'
    if grep 'tar:' $filelistfile; then
	echo "$scriptname: Errors in extracting $corpus_pkg"
	exit 1
    fi
    install_db $filelistfile
    echo $corp >> $installed_list
}

echo Installing Korp corpora:
for corp in $corpora; do
  echo "  $corp"
done

for corp in $corpora; do
    install_corpus $corp
done

rm $filelistfile

echo
echo Installation complete
