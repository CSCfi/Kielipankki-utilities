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
    ./rel-cmp --quiet check/note.tsv check/note.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a ! -s "$DIR/out" -a ! -s "$DIR/err"
    report "two files/stdout, note cmp note, quiet"
    cleanup
}

test002

test003 () {
    setup $FUNCNAME
    ./rel-cmp --quiet check/note.tsv < check/note.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a ! -s "$DIR/out" -a ! -s "$DIR/err"
    report "file, stdin/stdout, note cmp note, quiet"
    cleanup
}

test003
