# bash this

set -e

### Set working directory

if test -z ${BASH_SOURCE[0]}
then
   date "+%F %T Fail to run any test: no directory"
   exit 2
else
    cd "$(dirname ${BASH_SOURCE[0]})"
    FLATTEN=$(readlink -e ../vrt-flat)
    DEEPEN=$(readlink -e ../vrt-deep)
    LOOKUP=$(readlink -e ../vrt-tdp-alpha-lookup)
    MARMOT=$(readlink -e ../vrt-tdp-alpha-marmot)
    FILLUP=$(readlink -e ../vrt-tdp-alpha-fillup)
    PARSE=$(readlink -e ../vrt-tdp-alpha-parse)
    
    date "+%F %T Run tests on ${LOOKUP}"
    date "+%F %T Run tests on ${MARMOT}"
    date "+%F %T Run tests on ${FILLUP}"
    date "+%F %T Run tests on ${PARSE}"
    date "+%F %T Run tests with ${FLATTEN}"
    date "+%F %T Run tests with ${DEEPEN}"
    date "+%F %T Run tests in $(pwd)"
fi

for dir in marmot.in \
	       marmot marmot.out \
	       parse parse-q parse-v
do
    test -d ${dir} && rm -r ${dir}
done

### Test functions - legacy from another test script - TO ADAPT

ok_file_trip () {
    diff <(cd $1 ; find -name '*.vrt' | sort) \
	 <(cd $2 ; find -name '*.vrt' | sort)
}

ok_data_trip () {
    diff <(
	find $1 -name '*.vrt' |
	    sort |
	    while read f
		  # for want of two newlines
		  # an elaborate dance
	    do
		cat $f
		echo
	    done |
	    grep -v -x '' |
	    grep -v '<!-- Positional attributes'
    ) \
	 <(
	find $2 -name '*.vrt' |
	    sort |
	    xargs cat |
	    grep -v '<!-- Positional attributes'
    )
}

ok_have_names () {
    [ $(
	  find $1 -type f |
	      xargs -n 1 head -n 2 |
	      grep -c '<!-- Positional attributes'
      ) = \
	$( find $1 -type f | wc -l ) ]
}

# ADAPT! OR REMOVE! (wow far from removed copied further)

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

mkdir marmot.in

date "+%F %T Test 1.1: pre-MarMoT lookup at raw stage"

${LOOKUP} --debug raw --out marmot.in/lookup.raw tilsa.vrt

date "+%F %T Test 1.1: PASS without checks"

date "+%F %T Test 1.2: pre-MarMoT lookup at bare stage"

${LOOKUP} --debug bare --out marmot.in/lookup.bare tilsa.vrt

date "+%F %T Test 1.2: PASS without checks"

date "+%F %T Test 1.3: pre-MarMoT lookup at basic stage"

${LOOKUP} --debug basic --out marmot.in/lookup.basic tilsa.vrt

date "+%F %T Test 1.3: PASS without checks"

date "+%F %T Test 1.4: pre-MarMoT lookup at edited stage"

${LOOKUP} --debug edited --out marmot.in/lookup.edited tilsa.vrt

date "+%F %T Test 1.4: PASS without checks"

date "+%F %T Test 1.5: pre-MarMoT lookup at extended stage"

${LOOKUP} --debug extended --out marmot.in/lookup.extended tilsa.vrt

date "+%F %T Test 1.5: PASS without checks"

date "+%F %T Test 1.6: pre-MarMoT actual lookup"

${LOOKUP} tilsa.vrt > marmot.in/lookedup.vrt

if echo -n # what should this test?
then
    date "+%F %T Test 1.6: PASS without checks"
else
    date "+%F %T Test 1.6: FAIL"
fi

### Test 2 ###

date "+%F %T Test 2: MarMoT /flatten /deepen"

mkdir marmot

${FLATTEN} marmot.in/lookedup.vrt |
    ${MARMOT} |
    ${DEEPEN} --out marmot/tagged.vrt

if echo -n # and what should this test?
then
    date "+%F %T Test 2: PASS without checks"
else
    date "+%F %T Test 2: FAIL"
fi

### Test 3 ###

mkdir marmot.out

date "+%F %T Test 3.1: post-MarMoT fillup /debug"

${FILLUP} --debug --out marmot.out/tagged.debug marmot/tagged.vrt

date "+%F %T Test 3.1: PASS without checks"

date "+%F %T Test 3.2: post-MarMoT fillup"

${FILLUP} --out marmot.out/tagged.vrt marmot/tagged.vrt

date "+%F %T Test 3.2: PASS without checks"

### Test 4 ###

date "+%F %T Test 4.1: parse quietly /flatten /deepen"

mkdir parse-q

${FLATTEN} marmot/tagged.vrt |
    ${PARSE} --quiet 2> parse-q/quiet.err |
    ${DEEPEN} --out parse-q/quiet.vrt

if echo -n # and this?
then
    date "+%F %T Test 4.1: PASS without checks"
else
    date "+%F %T Test 4.1: FAIL"
fi

date "+%F %T Test 4.2: parse with default noise level /flatten /deepen"

mkdir parse

${FLATTEN} marmot/tagged.vrt |
    ${PARSE} 2> parse/default.err |
    ${DEEPEN} --out parse/default.vrt

if echo -n # and this?
then
    date "+%F %T Test 4.2: PASS without checks"
else
    date "+%F %T Test 4.2: FAIL"
fi

date "+%F %T Test 4.3: parse with high verbosity /flatten /deepen"

mkdir parse-v

${FLATTEN} marmot/tagged.vrt |
    ${PARSE} --verbose 2> parse-v/verbose.err |
    ${DEEPEN} --out parse-v/verbose.vrt

if echo -n # and this?
then
    date "+%F %T Test 4.3: PASS without checks"
else
    date "+%F %T Test 4.3: FAIL"
fi
