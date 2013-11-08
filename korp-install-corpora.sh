#! /bin/sh

# Install Korp corpora of the latest corpora package

# Corpus package directory
pkgdir=${CORPUS_PKGDIR:-.}
# Root directory, relative to which the corpus directory resides
rootdir=${ROOTDIR:-/}

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

pkg_prefix=korpdata_

timestampfile=$pkgdir/korp_fi_latest_corpus_packages_newer.timestamp
installed_list=$pkgdir/korp_fi_installed_corpora.list

tmpdir=${tmpdir:-${TMPDIR:-$pkgdir}}
filelistfile=$tmpdir/$scriptname.files.$$

if [ ! -e "$installed_list" ]; then
    touch "$installed_list"
fi

if [ "x$1" != "x" ]; then
    corpora=
    for corp in "$@"; do
	corpus_pkg=$pkgdir/$pkg_prefix$corp.tbz
	if [ ! -r $corpus_pkg ]; then
	    echo "Cannot read corpus package file $corpus_pkg; ignoring" \
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
    corpora=`find $pkgdir -name $pkg_prefix\*.tbz $newer_cond \
	| sed -e "s/^.*$pkg_prefix//g; s/\.tbz//g" \
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

echo Installing Korp corpora:
for corp in $corpora; do
  echo "  $corp"
done

for corp in $corpora; do
    corpus_pkg=$pkgdir/$pkg_prefix$corp.tbz
    echo
    echo "Installing $corp (compressed size `filesize $corpus_pkg`)"
    echo "  Copying CWB files"
    tar xvjp -C $rootdir -f $corpus_pkg 2>&1 \
	| tee $filelistfile \
	| sed -e 's/^/    /'
    if grep 'tar:' $filelistfile; then
	echo "$scriptname: Errors in extracting $corpus_pkg"
	exit 1
    fi
    sqlfiles=`grep -E '\.sql(\.(bz2|gz))?$' $filelistfile`
    if [ "x$sqlfiles" != "x" ]; then
	echo "  Loading data into MySQL database"
	for sqlfile in $sqlfiles; do
	    echo "    $sqlfile (size `filesize $rootdir/$sqlfile`)"
	    comprcat $rootdir/$sqlfile \
		| mysql $mysql_opts $korpdb
	    if [ $? -ne 0 ]; then
		echo "$scriptname: Errors in loading $sqlfile"
		exit 1
	    fi
	done
    fi
    echo $corp >> $installed_list
done

rm $filelistfile

echo
echo Installation complete
