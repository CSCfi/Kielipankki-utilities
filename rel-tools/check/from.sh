#! /bin/bash

# a rel-tools/check/ test script
# - call in rel-tools
# - scratch rel-tools/tmp/

source check/libtest.sh

TOPIC="${0##*/}"
TOPIC="${TOPIC%.sh}"

test001 () {
    setup $FUNCNAME
    ./rel-from --help \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err"
    report "--help"
    cleanup
}

test001

test002 () {
    setup $FUNCNAME
    ./rel-from --tag=id check/abc.txt \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err"
    report "file/stdout, --tag=id"
    cleanup
}

test002

test003 () {
    setup $FUNCNAME
    ./rel-from --unique check/abc.txt \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err"
    report "file/stdout, --unique"
    cleanup
}

test003

test004 () {
    setup $FUNCNAME
    ./rel-from --unique --map v1=gr,v2=ln check/abc.txt \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --eq "$DIR/out" check/abc.tsv
    report "file/stdout, --unique --map v1=gr,v2=ln"
    cleanup
}

test004

test005 () {
    setup $FUNCNAME
    echo -n |
	./rel-from --unique \
		   1> "$DIR/out" \
		   2> "$DIR/err"
    test $? = 0 -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --eq "$DIR/out" check/dum.tsv
    report "stdin/stdout, dum"
    cleanup
}

test005

test006 () {
    setup $FUNCNAME
    (echo ; echo) |
	./rel-from --unique \
		   1> "$DIR/out" \
		   2> "$DIR/err"
    test $? = 0 -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --eq "$DIR/out" check/dee.tsv
    report "stdin/stdout, dee"
    cleanup
}

test006
