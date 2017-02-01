#! /bin/sh
# -*- coding: utf-8 -*-

# Add a lemgram attribute to the Korp data (CWB and MySQL database) of
# a corpus with lemmas and part-of-speech tags.
#
# For more information: korp-corpus-add-lemgrams.sh --help
#
# TODO:
# - Handle lemma and POS when feature set attributes (maybe in
#   vrt-add-lemgrams.py)
# - Convert to using korp-lib.sh


progname=`basename $0`
progdir=`dirname $0`


default_corpus_roots="/v/corpora $WRKDIR/corpora $WRKDIR/korp/corpora /proj/clarin/korp/corpora /wrk/jyniemi/corpora"
default_cwbdirs="/usr/local/cwb/bin /usr/local/bin /proj/clarin/korp/cwb/bin $USERAPPL/bin"

find_existing_dir () {
    _test=$1
    _file=$2
    shift 2
    for dir in "$@"; do
	if [ $_test $dir/$_file ]; then
	    echo $dir
	    break
	fi
    done
}

corpus_root=${CORPUS_ROOT:-$(find_existing_dir -d "" $default_corpus_roots)}

cwb_bindir=${CWBDIR:-$(find_existing_dir -e cwb-decode $default_cwbdirs)}
cwb_perldir=${CWBDIR:-$(find_existing_dir -e cwb-make $default_cwbdirs)}
cwb_regdir=${CORPUS_REGISTRY:-$corpus_root/registry}
tmpdir=${TMPDIR:-${TEMPDIR:-${TMP:-${TEMP:-/tmp}}}}

posmap=
# Use the data directory specified in the registry file of a corpus,
# unless specified via an option
data_rootdir=
cwbdir=
outputdir=.
verbose=
import=1

tmpfname_base=$tmpdir/$progname.$$.tmp

add_lemgrams="$progdir/vrt-add-lemgrams.py"

filegroup=
for grp in korp clarin; do
    if groups | grep -qw $grp; then
	filegroup=$grp
	break
    fi
done
if [ "x$filegroup" = x ]; then
    filegroup=`groups | cut -d' ' -f1`
fi


ensure_perms () {
    chgrp -R $filegroup "$@"
    chmod -R g+rwX "$@"
}

warn () {
    echo "$progname: Warning: $1" >&2
}

error () {
    echo "$progname: $1" >&2
    exit 1
}

echo_verb () {
    if [ "x$verbose" != "x" ]; then
	echo "$@"
    fi
}

cleanup () {
    rm -f $tmpfname_base*
}

cleanup_abort () {
    cleanup
    exit 1
}


trap cleanup 0
trap cleanup_abort 1 2 13 15


usage () {
    cat <<EOF
Usage: $progname [options] corpus

Add a lemgram attribute to the Korp data (CWB and MySQL database) of a corpus
with lemmas and part-of-speech tags.

Options:
  -h, --help      show this help
  -m, --pos-map-file TSV_FILE
                  use TSV_FILE as the file mapping from the values of the pos
                  (part-of-speech) attribute in the corpus to the POS codes
                  used in lemgrams
  --no-mysql-import
                  do not import lemgram data into the Korp MySQL database
                  (table lemgram_index), which may take a long time
  -c, --cwbdir DIR
                  use the CWB binaries in DIR (default: $cwbdir)
  -r, --registry DIR
                  use DIR as the CWB registry (default: $cwb_regdir)
  -d, --data-root-dir DIR
                  use DIR as the corpus data root directory containing the
                  corpus-specific data directories, overriding the data
                  directory specified the registry file
  -o, --output-dir DIR
                  write lemgram attribute file and a TSV file to be imported
                  to Korp MySQL database to DIR (default: $outputdir)
  -v, --verbose   verbose output
EOF
    exit 0
}


# Test if GNU getopt
getopt -T > /dev/null
if [ $? -eq 4 ]; then
    # This requires GNU getopt
    args=`getopt -o "hm:c:r:d:o:v" -l "help,pos-map-file:,no-mysql-import,cwbdir:,registry:,data-root-dir:,output-dir:,verbose" -n "$progname" -- "$@"`
    if [ $? -ne 0 ]; then
	exit 1
    fi
    eval set -- "$args"
fi
# If not GNU getopt, arguments of long options must be separated from
# the option string by a space; getopt allows an equals sign.

# Process options
while [ "x$1" != "x" ] ; do
    case "$1" in
	-h | --help )
	    usage
	    ;;
	-m | --pos-map-file )
	    posmap=$2
	    shift
	    ;;
	--no-mysql-import )
	    import=
	    ;;
	-c | --cwbdir )
	    cwbdir=$2
	    shift
	    ;;
	-r | --registry )
	    cwb_regdir=$2
	    shift
	    ;;
	-d | --data-root-dir )
	    data_rootdir=$2
	    shift
	    ;;
	-d | --output-dir )
	    outputdir=$2
	    shift
	    ;;
	-v | --verbose )
	    verbose=1
	    ;;
	-- )
	    shift
	    break
	    ;;
	--* )
	    warn "Unrecognized option: $1"
	    ;;
	* )
	    break
	    ;;
    esac
    shift
done


find_prog () {
    _progname=$1
    shift
    _progpath=
    for dir in "$@"; do
	if [ -x $dir/$_progname ]; then
	    _progpath=$dir/$_progname
	    break
	fi
    done
    if [ "x$_progpath" = x ]; then
	_progpath=$(which $_progname 2> /dev/null)
    fi
    test "x$_progpath" != x ||
    error "$_progname not found in any of the directories $@ nor on PATH"
    echo $_progpath
}

cwbdirs="$cwb_bindir $cwbdir $cwbdir/bin"
cwb_decode=$(find_prog cwb-decode $cwbdirs)
cwb_encode=$(find_prog cwb-encode $cwbdirs)
cwb_describe_corpus=$(find_prog cwb-describe-corpus $cwbdirs)
cwb_make=$(find_prog cwb-make $cwb_perldir $cwbdir $cwbdir/bin)


add_lemgrams=$progdir/vrt-add-lemgrams.py
mysql_import=$progdir/korp-mysql-import.sh

test -d "$cwb_regdir" ||
error "Cannot access registry directory $cwb_regdir"

test "x$1" != x ||
error "Please specify corpus name; for usage information, run $progname --help"


get_corpus_dir () {
    corpname=$1
    if [ "x$data_rootdir" != x ]; then
	echo "$data_rootdir/$corpname"
    else
	echo `
	$cwb_describe_corpus -r "$cwb_regdir" $corpname |
	grep '^home directory' |
	sed -e 's/.*: //; s/\/$//'`
    fi
}


corpus=$1
regfile=$cwb_regdir/$corpus

test -e $regfile ||
error "Corpus $corpus not found in registry $cwb_regdir"

corpus_datadir=$(get_corpus_dir $corpus)

test -d "$corpus_datadir" ||
error "Corpus data directory $corpus_datadir not found"

test "x$posmap" != x ||
error "Please specify a part-of-speech mapping file with --pos-map-file"

test -r "$posmap" ||
error "Cannot read part-of-speech mapping file $posmap"

ls "$corpus_datadir"/lex.* > $tmpfname_base.ls 2>&1 &&
error "Corpus $corpus already contains lemgram files:
$(cat $tmpfname_base.ls)"

for attr in lemma pos; do
    grep -q "ATTRIBUTE $attr" $regfile ||
    error "Corpus $corpus does not contain attribute $attr required for lemgrams"
done

mkdir -p "$outputdir" || error "Cannot create output directory $outputdir"

lemma_pos_vrt="$outputdir/${corpus}_lemma_pos.vrt"
lemgrams_vrt="$outputdir/${corpus}_lex.vrt"
lemgrams_tsv="$outputdir/${corpus}_lemgrams.tsv"

corpus_u=$(echo $corpus | sed -e 's/\(.*\)/\U\1\E/')

echo_verb "Decoding attributes lemma and pos"
$cwb_decode -r "$cwb_regdir" -C $corpus -P lemma -P pos > "$lemma_pos_vrt"

echo_verb "Constructing lemgrams"
$add_lemgrams --lemma-field=1 --pos-field=2 --pos-map-file "$posmap" \
    < "$lemma_pos_vrt" |
cut -d'	' -f3 > "$lemgrams_vrt"

echo_verb "Encoding the lemgram (lex) attribute"
$cwb_encode -f "$lemgrams_vrt" -c utf8 -v -x -B -s -d "$corpus_datadir" \
    -p - -P lex/

if grep -q 'ATTRIBUTE lex' $regfile; then
    warn "Attribute lex already declared in the registry file"
else
    echo_verb "Adding the attribute lex to the registry file"
    cp -p $regfile $regfile.bak
    gawk '
	/^ATTRIBUTE / {attrs = 1}
	/^ *$/ && attrs {print "ATTRIBUTE lex"; attrs = 0}
	{print}' < $regfile.bak > $regfile
    ensure_perms $regfile $regfile.bak
fi

echo_verb "Indexing and compressing the lex attribute"
# FIXME: We should check if cwb-make succeeds
$cwb_make -r "$cwb_regdir" -M 2000 -V -g $filegroup -p 664 $corpus_u lex

echo_verb "Making lemgram data for the MySQL database"
tr -d '|' < "$lemgrams_vrt" |
sort |
uniq -c |
gawk '{printf "%s\t%s\t0\t0\t'$corpus_u'\n", $2, $1}' > "$lemgrams_tsv"

if [ "x$import" != x ]; then
    echo_verb "Importing the lemgram data into the Korp MySQL database"
    $mysql_import --prepare-tables "$lemgrams_tsv"
else
    cat <<EOF
Skipping importing lemgrams into the Korp MySQL database.
You can import the data later manually by running
  $mysql_import --prepare-tables "$lemgrams_tsv"
EOF
fi

cat <<EOF
Lemgram data added to the corpus $corpus.

To use the lemgram data in Korp, add the attribute declaration for the
lemgram attribute "lex" to the Korp configuration of the corpus $corpus
(the property "attributes" of settings.corpora.$corpus), typically by
adding the line

  lex : attrs.lemgram_hidden,

To copy the lemgram data to another Korp installation, do the following:

  1. Copy the CWB lemgram data files $corpus_datadir/lex.* to the corpus
     data directory in the target.
  2. Copy the CWB registry file $regfile to the target registry directory.
  3. Import the MySQL data file "$lemgrams_tsv":
       $mysql_import --prepare-tables "$lemgrams_tsv"
  4. Copy to the target the appropriate configuration file with the lex
     attribute added as described above.
EOF
