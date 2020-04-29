#! /bin/bash

# a rel-tools/check/ test script
# - call in rel-tools
# - scratch rel-tools/tmp/

source check/libtest.sh

TOPIC="${BASH_SOURCE##*/}"
TOPIC="${TOPIC%.sh}"

test001 () {
    setup $FUNCNAME
    ./rel-rename --help \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err"
    report "--help"
    cleanup
}

test001

test002 () {
    setup $FUNCNAME
    ./rel-rename check/tau.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err"
    report "file/stdout, no field options"
    cleanup
}

test002

test003 () {
    setup $FUNCNAME
    ./rel-rename --maps=pi=half,tau=full < check/tau.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err"
    report "file/stdout, two fields in one long option"
    cleanup
}

test003
