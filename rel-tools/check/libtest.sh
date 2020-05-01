# sourced in each test script
# test script provides TOPIC

mkdir --parents tmp
export TMPDIR=tmp

setup () {
    TEST="$1"
    DIR=$(mktemp --directory --tmpdir=tmp "$TOPIC-$TEST-XXX")
}

cleanup () {
    if test "${DIR%%/*}" = tmp
    then
	rm -r "$DIR"
    else
	1>&2 echo "not removing: $DIR"
	exit 3
    fi
}

report () {
    STAT="$?"
    MESS="$1"
    if test "$STAT" = 0
    then
	echo -e "$TOPIC\tPASS\t$TEST\t$MESS";
    else
	echo -e "$TOPIC\tFAIL\t$TEST\t$MESS"
    fi
}
