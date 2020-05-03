#! /bin/bash

# a rel-tools/check/ test script
# - call in rel-tools
# - scratch rel-tools/tmp/

source check/libtest.sh

TOPIC="${0##*/}"
TOPIC="${TOPIC%.sh}"

test001 () {
    setup $FUNCNAME
    ./rel-union --help \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err"
    report "--help"
    cleanup
}

test001

test002 () {
    setup $FUNCNAME
    ./rel-union check/number.tsv check/numero.tsv check/luku3.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --gt "$DIR/out" check/number.tsv &&
	./rel-cmp --quiet --gt "$DIR/out" check/numero.tsv &&
	./rel-cmp --quiet --gt "$DIR/out" check/luku3.tsv
    report "three files/stdout"
    cleanup
}

test002
