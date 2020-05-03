#! /bin/bash

# a rel-tools/check/ test script
# - call in rel-tools
# - scratch rel-tools/tmp/

source check/libtest.sh

TOPIC="${0##*/}"
TOPIC="${TOPIC%.sh}"

test001 () {
    setup $FUNCNAME
    ./rel-meet --help \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err"
    report "--help"
    cleanup
}

test001

test002 () {
    setup $FUNCNAME
    ./rel-meet check/number.tsv check/number.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --eq "$DIR/out" check/number.tsv
    report "two files/stdout, self out"
    cleanup
}

test002

test003 () {
    setup $FUNCNAME
    ./rel-meet check/number.tsv < check/numero.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --lt "$DIR/out" check/number.tsv &&
	./rel-cmp --quiet --lt "$DIR/out" check/numero.tsv
    report "file, stdin/stdout, in both"
    cleanup
}

test003

test004 () {
    setup $FUNCNAME
    ./rel-meet check/number.tsv check/number.tsv check/number.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --eq "$DIR/out" check/number.tsv
    report "three files/stdout, self out"
    cleanup
}

test004
