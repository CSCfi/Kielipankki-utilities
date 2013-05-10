#! /bin/sh

# Install Korp corpora of the latest corpora package

# Corpus package directory
pkgdir=${pkgdir:-.}
# Root directory, relative to which the corpus directory resides
rootdir=${rootdir:-/}

# Korp MySQL database
korpdb=korp
# Assume that the Korp MySQL database user and password are specified
# in a MySQL option file

scriptname=`basename $0`

timestampfile=$pkgdir/korp_fi_latest_corpus_packages_newer.timestamp
installed_list=$pkgdir/korp_fi_installed_corpora.list

tmpdir=${tmpdir:-${TMPDIR:-$pkgdir}}
filelistfile=$tmpdir/$scriptname.files.$$

if [ "$1x" != "x" ]; then
    corpora=
    for corp in "$@"; do
	corpus_pkg=$pkgdir/korpdata_$corp.tbz
	if [ ! -r $corpus_pkg ]; then
	    echo "Cannot read corpus package file $corpus_pkg; ignoring" \
		> /dev/stderr
	else
	    corpora="$corpora $corp"
	fi
    done
else
    corpora=`find $pkgdir -name korpdata_\*.tbz -newer $timestampfile \
	| sed -e 's/^.*korpdata_//g; s/\.tbz//g' \
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
    corpus_pkg=$pkgdir/korpdata_$corp.tbz
    echo
    echo "Installing $corp (compressed size `filesize $corpus_pkg`)"
    echo "  Copying CWB files"
    tar xvjp -C $rootdir -f korpdata_$corp.tbz 2>&1 \
	| tee $filelistfile \
	| sed -e 's/^/    /'
    if grep 'tar:' $filelistfile; then
	echo "$0: Errors in extracting $corpus_pkg"
	exit 1
    fi
    sqlfiles=`grep -E '\.sql(\.(bz2|gz))?$' $filelistfile`
    if [ "x$sqlfiles" != "x" ]; then
	echo "  Loading data into MySQL database"
	for sqlfile in $sqlfiles; do
	    echo "    $sqlfile (size `filesize $rootdir/$sqlfile`)"
	    comprcat $rootdir/$sqlfile \
		| mysql $korpdb
	    if [ $? -ne 0 ]; then
		echo "$0: Errors in loading $sqlfile"
		exit 1
	    fi
	done
    fi
    echo $corp >> $installed_list
done

rm $filelistfile

echo
echo Installation complete
