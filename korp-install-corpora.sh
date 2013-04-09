#! /bin/sh

# Install Korp corpora of the latest corpora package

# Corpus package directory
pkgdir=${pkgdir:-.}
# Root directory, relative to which the corpus directory resides
rootdir=${rootdir:-/}

# Korp MySQL database
korpdb=korp
# Korp MySQL database user
korpdbuser=korp

timestampfile=$pkgdir/korp_fi_latest_corpus_packages_newer.timestamp

tmpdir=${tmpdir:-${TMPDIR:-$pkgdir}}
filelistfile=$tmpdir/`basename $0`.files.$$

trap "echo Aborting installation; rm $filelistfile; exit 1" HUP INT QUIT

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

echo Installing Korp corpora

for pkg in `find $pkgdir -name korpdata_\*.tbz -newer $timestampfile`; do
    echo
    echo Installing `basename $pkg .tbz`
    echo "  Copying CWB files"
    tar xvjp -C $rootdir -f $pkg | tee $filelistfile | awk '{print "    " $0}'
    echo "  Loading data into MySQL database"
    for sqlfile in `egrep '\.sql(\.(bz2|gz))$' $filelistfile`; do
	echo "    $sqlfile"
	comprcat $rootdir/$sqlfile | mysql --user $korpdbuser $korpdb
    done
done

rm $filelistfile

echo
echo Installation complete
