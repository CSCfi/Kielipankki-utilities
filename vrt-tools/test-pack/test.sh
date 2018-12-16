# bash this

set -e

### Set working directory

if test -z ${BASH_SOURCE[0]}
then
   date "+%F %T Fail to run any test: no directory"
   exit 2
else
    cd "$(dirname ${BASH_SOURCE[0]})"
    PACK=$(readlink -e ../vrt-pack-dir)
    UNPACK=$(readlink -e ../vrt-unpack-dir)
    date "+%F %T Run tests on ${PACK}"
    date "+%F %T Run tests on ${UNPACK}"
    date "+%F %T Run tests in $(pwd)"
fi

for dir in data.u.tmp \
	       data.u.tmp.res \
	       tmp.u res.u \
	       data.u.tmpx \
	       data.u.tmpx.resx \
	       x \
	       names lines tokens bytes
do
    test -d ${dir} && rm -r ${dir}
done

### Test functions

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

# ADAPT! OR REMOVE!

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

date "+%F %T Test 1: data.u / --suffix .tmp / --suffix .res"

${PACK} --suffix .tmp data.u/
${UNPACK} --suffix .res data.u.tmp/

if ok_file_trip data.u data.u.tmp.res &&
	ok_data_trip data.u data.u.tmp.res
then
    date "+%F %T PASS 1"
else
    date "+%F %T FAIL 1"
fi

### Test 2 ###

date "+%F %T Test 2: data.u / --out tmp.u / --out res.u"

${PACK} --out tmp.u data.u/
${UNPACK} --out res.u tmp.u/

if ok_file_trip data.u res.u &&
	ok_data_trip data.u res.u
then
    date "+%F %T PASS 2"
else
    date "+%F %T FAIL 2"
fi

### Test 3 ###

date "+%F %T Test 3: ../data.u / --suffix .tmpx / --suffix .resx"

(
    cd data.u
    ${PACK} --suffix .tmpx ../data.u/
    ${UNPACK} --suffix .resx ../data.u.tmpx/
)

if ok_file_trip data.u data.u.tmpx.resx &&
	ok_data_trip data.u data.u.tmpx.resx
then
    date "+%F %T PASS 3"
else
    date "+%F %T FAIL 3"
fi

### Test 4 ###

date "+%F %T Test 4: ../data.u / --out ../x/xtmp.u / --out ../x/xres.u"

mkdir x

(
    cd data.u
    ${PACK} --out ../x/xtmp.u ../data.u/
    ${UNPACK} --out ../x/xres.u ../x/xtmp.u/
)

if ok_file_trip data.u x/xres.u &&
	ok_data_trip data.u x/xres.u
then
    date "+%F %T PASS 4"
else
    date "+%F %T FAIL 4"
fi

### Test 5 ###

date "+%F %T Test 5: data.n / names/{tmp.n,res.n}"

mkdir names

${PACK} --out names/tmp.n data.n/
${UNPACK} --out names/res.n names/tmp.n/

if ok_file_trip data.n names/res.n &&
	ok_data_trip data.n names/res.n
then
    date "+%F %T PASS 5"
else
    date "+%F %T FAIL 5"
fi

### Test 6 ###

date "+%F %T Test 6 data.n / lines/{tmp.n,res.n}"

mkdir lines

${PACK} --out=lines/tmp.n --lines=100 data.n/
${UNPACK} --out=lines/res.n lines/tmp.n/

if ok_file_trip data.n lines/res.n &&
	ok_data_trip data.n lines/res.n
then
    date "+%F %T PASS 6"
else
    date "+%F %T FAIL 6"
fi

### Test 7 ###

date "+%F %T Test 7 data.n / tokens/{tmp.n,res.n}"

mkdir tokens

${PACK} --out=tokens/tmp.n --tokens=100 data.n/
${UNPACK} --out=tokens/res.n tokens/tmp.n/

if ok_file_trip data.n tokens/res.n &&
	ok_data_trip data.n tokens/res.n
then
    date "+%F %T PASS 7"
else
    date "+%F %T FAIL 7"
fi

### Test 8 ###

date "+%F %T Test 8 data.n / bytes/{tmp.n,res.n}"

mkdir bytes

${PACK} --out=bytes/tmp.n --bytes=100 data.n/
${UNPACK} --out=bytes/res.n bytes/tmp.n/

if ok_file_trip data.n bytes/res.n &&
	ok_data_trip data.n bytes/res.n &&
	ok_have_names bytes/tmp.n
then
    date "+%F %T PASS 8"
else
    date "+%F %T FAIL 8"
fi
