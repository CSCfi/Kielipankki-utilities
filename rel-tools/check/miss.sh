#! /bin/bash

# a rel-tools/check/ test script
# - call in rel-tools
# - scratch rel-tools/tmp/

source check/libtest.sh

TOPIC="${0##*/}"
TOPIC="${TOPIC%.sh}"

test001 () {
    setup $FUNCNAME
    ./rel-miss --help \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err"
    report "--help"
    cleanup
}

test001

test002 () {
    setup $FUNCNAME
    ./rel-miss check/note.tsv check/word.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --lt "$DIR/out" check/note.tsv
    report "two files/stdout, (empty out)"
    cleanup
}

test002

test003 () {
    setup $FUNCNAME
    ./rel-miss check/note.tsv < check/word.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --lt "$DIR/out" check/note.tsv
    report "file, stdin/stdout, (empty out)"
    cleanup
}

test003

test004 () {
    setup $FUNCNAME
    ./rel-miss check/note.tsv < check/dum.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --eq "$DIR/out" check/note.tsv
    report "file, stdin/stdout, dum in, self out"
    cleanup
}

test004
