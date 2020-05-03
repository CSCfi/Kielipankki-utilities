#! /bin/bash

# a rel-tools/check/ test script
# - call in rel-tools
# - scratch rel-tools/tmp/

source check/libtest.sh

TOPIC="${0##*/}"
TOPIC="${TOPIC%.sh}"

test001 () {
    setup $FUNCNAME
    ./rel-sample --help \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err"
    report "--help"
    cleanup
}

test001

test002 () {
    setup $FUNCNAME
    ./rel-sample < check/tau.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --eq "$DIR/out" check/tau.tsv
    report "stdin/stdout, no option"
    cleanup
}

test002

test003 () {
    setup $FUNCNAME
    ./rel-sample --records=3 check/tau.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --lt "$DIR/out" check/tau.tsv
    report "file/stdout, --records=3"
    cleanup
}

test003

test004 () {
    setup $FUNCNAME
    ./rel-sample --records=3 --tag=org check/tau.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --ne "$DIR/out" check/tau.tsv
    report "file/stdout, --records=3 --tag=org"
    cleanup
}

test004
