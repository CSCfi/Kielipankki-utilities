#! /bin/bash

# a rel-tools/check/ test script
# - call in rel-tools
# - scratch rel-tools/tmp/

source check/libtest.sh

TOPIC="${0##*/}"
TOPIC="${TOPIC%.sh}"

test001 () {
    setup $FUNCNAME
    ./rel-cmp --help \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err"
    report "--help"
    cleanup
}

test001

test002 () {
    setup $FUNCNAME
    ./rel-cmp --quiet --cmp check/note.tsv check/note.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a ! -s "$DIR/out" -a ! -s "$DIR/err"
    report "two files/stdout, --cmp note note, --quiet"
    cleanup
}

test002

test003 () {
    setup $FUNCNAME
    ./rel-cmp --quiet --cmp check/note.tsv < check/note.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a ! -s "$DIR/out" -a ! -s "$DIR/err"
    report "file, stdin/stdout, --cmp note note, --quiet"
    cleanup
}

test003

test004 () {
    setup $FUNCNAME
    ./rel-cmp --quiet --eq check/luku3.tsv check/luku3.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a ! -s "$DIR/out" -a ! -s "$DIR/err"
    report "two files/stdout, --eq luku3 luku3, --quiet"
    cleanup
}

test004

test005 () {
    setup $FUNCNAME
    ./rel-cmp --quiet --ne check/luku3.tsv check/luku3.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 100 -a ! -s "$DIR/out" -a ! -s "$DIR/err"
    report "two files/stdout, --ne luku3 luku3, --quiet"
    cleanup
}

test005

test005 () {
    setup $FUNCNAME
    ./rel-cmp --quiet --le check/luku3.tsv check/luku3.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a ! -s "$DIR/out" -a ! -s "$DIR/err"
    report "two files/stdout, --le luku3 luku3, --quiet"
    cleanup
}

test005

test006 () {
    setup $FUNCNAME
    ./rel-cmp --quiet --lt check/luku3.tsv check/luku3.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 100 -a ! -s "$DIR/out" -a ! -s "$DIR/err"
    report "two files/stdout, --lt luku3 luku3, --quiet"
    cleanup
}

test006

test007 () {
    setup $FUNCNAME
    ./rel-cmp --quiet --lt check/luku3.tsv check/luku8.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a ! -s "$DIR/out" -a ! -s "$DIR/err"
    report "two files/stdout, --le luku3 luku8, --quiet"
    cleanup
}

test007

test008 () {
    setup $FUNCNAME
    ./rel-cmp --quiet --lt check/luku3.tsv check/luku8.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a ! -s "$DIR/out" -a ! -s "$DIR/err"
    report "two files/stdout, --lt luku3 luku8, --quiet"
    cleanup
}

test008
