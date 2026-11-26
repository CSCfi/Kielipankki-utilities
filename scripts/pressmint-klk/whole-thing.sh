#!/usr/bin/env bash

# run this
# in PressMint-FI root
# in Jussi's laptop (being him!)
# to build the first TEI samples

# extract and check ...
SCRIPTNAME="${BASH_SOURCE[0]}"
case "$SCRIPTNAME" in
    /home/jpiitula/proj/KLK-TEI/whole-thing.sh) ;;
    *) 1>&2 echo "unexpected script name: $SCRIPTNAME"
       exit 2
esac

# find there this /whole-thing.sh (hm, TODO drop .sh)
# find there klk-vrt-to-tei
# find there make-root-file
SCRIPTHOME=$(dirname $SCRIPTNAME)

case "$PWD" in
    /home/jpiitula/proj/PressMint-FI/Samples/PressMint-FI) ;;
    *) 1>&2 echo "not in Samples/PressMint-FI: $PWD"
       exit 2
esac

# these were _not_ meant to be!
# mkdir -p PressMint-FI.TEI
# mkdir -p PressMint-FI.TEI.ana

(
    $SCRIPTHOME/klk-vrt-to-tei \
	--corpus=klk-fi-v2 \
	--syntax=turkunlp \
	./Sources/fi-v2-sample-1820-1910s.vrt

    $SCRIPTHOME/klk-vrt-to-tei \
	--corpus=klk-sv-v2 \
	--syntax=språkbanken \
	./Sources/sv-v2-sample-1820-1910s.vrt

    $SCRIPTHOME/make-root-file
)

(
    $SCRIPTHOME/klk-vrt-to-tei \
	--ana \
	--corpus=klk-fi-v2 \
	--syntax=turkunlp \
	./Sources/fi-v2-sample-1820-1910s.vrt

    $SCRIPTHOME/klk-vrt-to-tei \
	--ana \
	--corpus=klk-sv-v2 \
	--syntax=språkbanken \
	./Sources/sv-v2-sample-1820-1910s.vrt

    $SCRIPTHOME/make-root-file --ana
)

set +e # ignore exit status: output is diagnostic messages
xmllint --xinclude --format --encode utf8 --noout ./PressMint-FI.xml
xmllint --xinclude --format --encode utf8 --noout ./PressMint-FI.ana.xml

echo "no output indicates that both versions are at least well-formed"
