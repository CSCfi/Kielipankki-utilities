#! /bin/sh
# -*- coding: utf-8 -*-

# Usage: korp-convert-timedata.sh [options] corpus ...
#
# For more information, run korp-convert-timedata.sh --help


progname=`basename $0`
progdir=`dirname $0`

shortopts="hc:t:v"
longopts="help,convert:,corpus-root:,tsv-dir:,import-database,verbose"

convert_types=all
tsvdir=$CORPUS_TSVDIR
tsvsubdir=sql
import_database=
verbose=

dbname="korp"

. $progdir/korp-lib.sh


usage () {
    cat <<EOF
Usage: $progname [options] corpus ...

Convert to and add corpus time data in the format required by Korp backend
version 2.8.

Convert existing timespans data in the Korp MySQL database to the new timedata
format, add finer granulartities to text datefrom/dateto and timefrom/timeto
attributes if missing, and add FirstDate and LastDate to the corpus .info
file.

Corpus names are specified in lower case. Shell wildcards may be used in them.

Options:
  -h, --help      show this help
  --convert TYPES
                  convert the Korp timedata types listed in TYPES, separated
                  by commas or spaces: one or more of textattrs (text
                  date/time from/to attributes), mysql (MySQL tables), info
                  (.info file) or all (all of the above) (default: $convert_types)
  -c, --corpus-root DIR
                  use DIR as the root directory of corpus files for the
                  source files (CORPUS_ROOT) (default: $corpus_root)
  -t, --tsv-dir DIRTEMPL
                  use DIRTEMPL as the directory template to which to write
                  Korp MySQL TSV data files; DIRTEMPL is a directory name
                  possibly containing the placeholder {corpid} for corpus id
                  (default: CORPUS_ROOT/$tsvsubdir)
  --import-database
                  import the MySQL database tables to the database
  -v, --verbose   verbose output
EOF
    exit 0
}

# Process options
while [ "x$1" != "x" ] ; do
    case "$1" in
	-h | --help )
	    usage
	    ;;
	--convert )
	    shift
	    convert_types=$1
	    ;;
	-c | --corpus-root )
	    shift
	    set_corpus_root "$1"
	    ;;
	-t | --tsv-dir )
	    shift
	    tsvdir=$1
	    ;;
	--import-database )
	    import_database=--import-database
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


tsvdir=${tsvdir:-$corpus_root/$tsvsubdir}

if [ "x$1" = x ]; then
    error "Please specify corpora"
fi

corpora=$(list_corpora "$@")

verbose_opt=
if [ "x$verbose" != x ]; then
    verbose_opt=--verbose
fi


make_timedata () {
    # Use a temporary file instead of a pipe (that would create a
    # subprocess), so that exit_on_error really exits
    exit_on_error $progdir/timespans-adjust-granularity.py \
	--granularity=$1 --from-field=2 --to-field=3 --count-field=4 \
	> $tmp_prefix.timedata.tsv
    sort < $tmp_prefix.timedata.tsv
}

add_registry_attrs () {
    _corpus=$1
    awk '
        BEGIN {
            split ("datefrom timefrom dateto timeto", attrs)
        }
        /^# <text / {
            new = ""
            for (i = 1; i <= 4; i++) {
                if (! match ($0, " " attrs[i] "=")) {
                    new = new " " attrs[i] "=\"..\""
                }
            }
            sub (/>/, new ">")
        }
        /^STRUCTURE text_/ {
            prevtext = 1
            match ($0, /_[^ \t]+/)
            textattrs[substr ($0, RSTART + 1, RLENGTH - 1)] = 1
        }
        /^$/ {
            if (prevtext) {
                for (i = 1; i <= 4; i++) {
                    if (! (attrs[i] in textattrs)) {
                        printf "STRUCTURE %-20s # [annotations]\n", "text_" attrs[i]
                    }
                }
            }
            prevtext = 0
        }
        { print }
        ' $cwb_regdir/$_corpus > $tmp_prefix.registry_new
    if ! cmp -s $cwb_regdir/$_corpus $tmp_prefix.registry_new; then
	cp -p $cwb_regdir/$_corpus $cwb_regdir/$_corpus.bak
	mv $tmp_prefix.registry_new $cwb_regdir/$_corpus
	ensure_perms $cwb_regdir/$_corpus $cwb_regdir/$_corpus.bak
    fi
}

fix_text_timedata () {
    _corpus=$1
    echo_verb "  Updating text date and time attributes in CWB data"
    $cwb_bindir/cwb-s-decode $_corpus -S text \
	> $tmp_prefix.text.tsv 2> $tmp_prefix.text.err
    if grep -q "Can't access s-attribute" $tmp_prefix.text.err; then
	echo_verb "    No structural attribute 'text' in corpus $_corpus; skipping"
	return
    fi
    for attrname in datefrom timefrom dateto timeto; do
	_fname=$tmp_prefix.$attrname.tsv
	$cwb_bindir/cwb-s-decode $_corpus -S text_$attrname \
	    2> $_fname.err |
	cut -d"$tab" -f3 > $_fname
	if grep -q "Can't access s-attribute" $_fname.err; then
	    cat /dev/null > $_fname
	fi
    done
    for fromto in from to; do
	# If incomplete date, ignore possible time
	paste $tmp_prefix.date$fromto.tsv $tmp_prefix.time$fromto.tsv |
	awk -F"$tab" 'length($1) < 8 { $2 = "" } { print $1 $2 }' \
	    > $tmp_prefix.$fromto.tsv
    done
    paste $tmp_prefix.text.tsv $tmp_prefix.from.tsv $tmp_prefix.to.tsv |
    $progdir/timespans-adjust-granularity.py \
	--granularity=second --from-field=3 --to-field=4 --no-counts |
    sed -e 's/^\([^\t]*\t[^\t]*\t\)\(........\)\(......\)\t\(........\)\(......\)/\1\2\t\3\t\4\t\5/' \
	-e 's/^\([^\t]*\t[^\t]*\t\t\)/\1\t\t/' > $tmp_prefix.fromto_new.tsv
    while read attrname fieldnum; do
	if [ -e $corpus_root/data/$_corpus/text_$attrname.avs ]; then
	    echo_verb "    Attribute text_$attrname already exists; backing up existing data files."
	    for ext in avs avx rng; do
		cp -p $corpus_root/data/$_corpus/text_$attrname.$ext \
		    $corpus_root/data/$_corpus/text_$attrname.$ext.bak
	    done
	fi
	cut -d"$tab" -f1,2,$fieldnum $tmp_prefix.fromto_new.tsv |
	$cwb_bindir/cwb-s-encode -B -d $corpus_root/data/$_corpus \
	    -V text_$attrname
    done <<EOF
datefrom 3
timefrom 4
dateto 5
timeto 6
EOF
    add_registry_attrs $_corpus
}

update_info () {
    _corpus=$1
    echo_verb "  Adding FirstDate and LastDate to corpus .info file"
    $progdir/cwbdata-extract-info.sh --update --tsv-dir "$tsvdir" \
	$verbose_opt $_corpus |
    indent_input 4
}

make_mysql_timedata () {
    _corpus=$1
    $progdir/korp-make-timedata-tables.sh --corpus-root=$corpus_root \
	--tsv-dir=$tsvdir $import_database $verbose_opt $_corpus |
    cat_verb |
    indent_input 2
}

run_convert_stage () {
    type=$1
    shift
    if [ "x$convert_types" = "xall" ] ||
	{ echo $convert_types | grep -E -iq "\b$type\b"; };
    then
	"$@"
    fi
}

convert_timedata () {
    _corpus=$1
    run_convert_stage "textattrs?" fix_text_timedata $_corpus
    run_convert_stage "mysql" make_mysql_timedata $_corpus
    run_convert_stage "info" update_info $_corpus
}


for corpus in $corpora; do
    echo_verb "Converting time data in corpus $corpus"
    convert_timedata $corpus
done
