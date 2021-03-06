#! /bin/bash

# a rel-tools/check/ test script
# - call in rel-tools
# - scratch rel-tools/tmp/

source check/libtest.sh

TOPIC="${0##*/}"
TOPIC="${TOPIC%.sh}"

test001 () {
    setup $FUNCNAME
    ./rel-compose2 --help \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err"
    report "--help"
    cleanup
}

test001

test002 () {
    setup $FUNCNAME
    ./rel-compose2 \
	--cache 3 \
	check/word.tsv \
	check/note.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-join check/word.tsv check/note.tsv |
	    ./rel-drop --field=id |
	    ./rel-cmp --quiet --eq "$DIR/out"
    report "two files/stdout"
    cleanup
}

test002

test003 () {
    setup $FUNCNAME
    ./rel-compose2 \
	--cache 3 \
	check/note.tsv \
	< check/note.tsv \
	       1> "$DIR/out" \
	       2> "$DIR/err"
    test $? = 0 -a -s "$DIR/out" -a ! -s "$DIR/err" &&
	./rel-cmp --quiet --eq "$DIR/out" check/dee.tsv
    report "file, stdin/stdout, dee out"
    cleanup
}

test003
