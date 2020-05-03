#! /bin/bash

# a rel-tools/check/ test script
# - call in rel-tools
# - scratch rel-tools/tmp/

source check/libtest.sh

TOPIC="${0##*/}"
TOPIC="${TOPIC%.sh}"

test001 () {
    setup $FUNCNAME
    ./rel-match --help \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err"
    report "--help"
    cleanup
}

test001

test002 () {
    setup $FUNCNAME
    ./rel-match check/note.tsv check/word.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --eq "$DIR/out" check/note.tsv
    report "two files/stdout, self out"
    cleanup
}

test002

test003 () {
    setup $FUNCNAME
    ./rel-match check/note.tsv < check/word.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --eq "$DIR/out" check/note.tsv
    report "file, stdin/stdout, self out"
    cleanup
}

test003

test004 () {
    setup $FUNCNAME
    ./rel-match check/note.tsv < check/dum.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-head --records=0 check/note.tsv |
	    ./rel-cmp --quiet --eq "$DIR/out"
    report "file, stdin/stdout, match dum, empty out"
    cleanup
}

test004

test005 () {
    setup $FUNCNAME
    ./rel-match check/note.tsv < check/dee.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --eq "$DIR/out" check/note.tsv
    report "file, stdin/stdout, match dee, self out"
    cleanup
}

test005
