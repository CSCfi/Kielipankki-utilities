# bash this

set -e


### Set working directory

if test -z ${BASH_SOURCE[0]}
then
   date "+%F %T Fail to run any test: no directory"
   exit 2
else
    cd "$(dirname ${BASH_SOURCE[0]})"
    PROG=$(readlink -e ../vrt-huntag-suc)
    date "+%F %T Run tests on ${PROG}"
    date "+%F %T Run tests in $(pwd)"
fi

for dir in std ouf inf fif imp
do
    test -d ${dir} && rm -r ${dir}
done

### Test functions

ok_file_count () {
    [ $(ls $1 | wc -l) = $2 ]
}

ok_result () {
    [ $(wc -l < $1) = 106 ] &&
	[ $(grep -c '^<' $1) = 21 ] &&
	[ $(grep -c -P '\t' $1) = 85 ]
}

ok_backup () {
    [ $(wc -l < $1) = 106 ] &&
	[ $(grep -c '^<' $1) = 21 ] &&
	[ $(grep -c -P '\t' $1) = 0 ]
}

ok_empty () {
    [ -e $1 -a ! -s $1 ]
}

### Test 1 ###

date "+%F %T Test 1: std/ (standard input to standard output)"

mkdir std

${PROG} < text.vrt > std/outer.vrt 2> std/outer.err

if ok_file_count std 2 &&
	ok_result std/outer.vrt
then
    date "+%F %T PASS 1"
else
    date "+%F %T FAIL 1"
fi

### Test 2 ###

date +"%F %T Test 2: ouf/ (standard input to output file)"

mkdir ouf

${PROG} -o ouf/outer.vrt < text.vrt > ouf/outer.out 2> ouf/outer.err

(
    cd ouf
    ${PROG} -o inner.vrt < ../text.vrt > inner.out 2> inner.err
)

if ok_file_count ouf 6 &&
	ok_result ouf/outer.vrt &&
	ok_result ouf/inner.vrt &&
	ok_empty ouf/outer.out &&
	ok_empty ouf/inner.out
then
    date "+%F %T PASS 2"
else
    date "+%F %T FAIL 2"
fi

# Test 3

date "+%F %T Test 3: inf/ (input file to standard output)"

mkdir inf

${PROG} text.vrt > inf/outer.vrt 2> inf/outer.err

(
    cd inf
    ${PROG} ../text.vrt > inner.vrt 2> inner.err
)

if ok_file_count inf 4 &&
	ok_result inf/outer.vrt &&
	ok_result inf/inner.vrt
then
    date "+%F %T PASS 3"
else
    date "+%F %T FAIL 3"
fi

# Test 4

date "+%F %T Test 4: fif/ (input file to output file)"

mkdir fif

${PROG} -o fif/outer.vrt text.vrt > fif/outer.out 2> fif/outer.err

(
    cd fif
    ${PROG} -o inner.vrt ../text.vrt > inner.out 2> inner.err
)

if ok_file_count fif 6 &&
	ok_result fif/outer.vrt &&
	ok_result fif/inner.vrt &&
	ok_empty fif/outer.out &&
	ok_empty fif/inner.out
then
    date "+%F %T PASS 4"
else
    date "+%F %T FAIL 4"
fi

# Test 5

date "+%F %T Test 5: imp/ (in place)"

mkdir imp

cp text.vrt imp/outersans.vrt
cp text.vrt imp/outerback.vrt
cp text.vrt imp/innersans.vrt
cp text.vrt imp/innerback.vrt

${PROG} -i imp/outersans.vrt > imp/outersans.out 2> imp/outersans.err
${PROG} -i -b - imp/outerback.vrt > imp/outerback.out 2> imp/outerback.err

(
    cd imp
    ${PROG} -i innersans.vrt > innersans.out 2> innersans.err
    ${PROG} -i -b - innerback.vrt > innerback.out 2> innerback.err
)

if ok_file_count imp 14 &&
	ok_result imp/outersans.vrt &&
	ok_result imp/outerback.vrt &&
	ok_result imp/innersans.vrt &&
	ok_result imp/innerback.vrt &&
	ok_backup imp/outerback.vrt- &&
	ok_backup imp/innerback.vrt- &&
	ok_empty imp/outersans.out &&
	ok_empty imp/outerback.out &&
	ok_empty imp/innersans.out &&
	ok_empty imp/innerback.out
then
    date "+%F %T PASS 5"
else
    date "+%F %T FAIL 5"
fi

if ok_backup text.vrt
then
    date "+%F %T Original FINE"
else
    date "+%F %T Original CORRUPTED"
fi
