#! /bin/bash

# a rel-tools/check/ test script
# - call in rel-tools
# - scratch rel-tools/tmp/

source check/libtest.sh

TOPIC="${0##*/}"
TOPIC="${TOPIC%.sh}"

test001 () {
    setup $FUNCNAME
    ./rel-keep --help \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err"
    report "--help"
    cleanup
}

test001

test002 () {
    setup $FUNCNAME
    ./rel-keep check/numero.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --eq "$DIR/out" check/dee.tsv
    report "file/stdout, dee out"
    cleanup
}

test002

test003 () {
    setup $FUNCNAME
    ./rel-keep --field=mean check/numero.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --ne "$DIR/out" check/dee.tsv
    report "file/stdout, --field=mean"
    cleanup
}

test003

test004 () {
    setup $FUNCNAME
    ./rel-keep --field=mean,word check/numero.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --eq "$DIR/out" check/numero.tsv
    report "file/stdout, --field=mean,word, self out"
    cleanup
}

test004

