#! /bin/sh

# Fix the files of the Helsinki Corpus of Swahili.
# - Fix Windows-1252 characters to UTF-8
# - Convert Windows CP-1252 apostrophes to ASCII ones
# - Add possibly missing final </text>
# - Add a final newline
#
# For unannotated files (*.shu):
# - Glue full stops to the preceding word
#
# For annotated files (*.anl):
# - Add missing sentence start and end tags


progname=`basename $0`
progdir=`dirname $0`

scriptdir=$progdir/../../scripts

shortopts="ho:"
longopts="help,output-dir:,relative-input-dir:"

output_dir=
relative_input_dir=

. $scriptdir/korp-lib.sh


usage () {
    cat <<EOF
Usage: $progname [options] file ...

Fix the files of the Helsinki Corpus of Swahili.

Uses a slightly different set of fixes depending on the file extension:
.shu (unannotated text files) or .anl (analysed, VRT-like files).

Options:
  -h, --help
  -o, --output-dir DIR
  --relative-input-dir DIR
EOF
    exit 0
}

# Process options
while [ "x$1" != "x" ] ; do
    case "$1" in
	-h | --help )
	    usage
	    ;;
	-o | --output-dir )
	    shift
	    output_dir=$1
	    ;;
	--relative-input-dir )
	    shift
	    relative_input_dir=$1
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

fix_shu () {
    perl -pe '
        # Remove space before the final full stop
	s/ \.$/./;'
}

fix_anl () {
    perl -ne '
        if (/^\s*$/) {
           next;
        }
        if (/^<sentence.*id="(.*?)"/) {
            $s_id = $1;
            $s_idn = 0;
            print $prev;
            # If the previous sentence element was not closed, add an
            # end tag
            print "</sentence>\n" if ($in_s);
            $in_s = 1;
            $prev = $_;
            next;
        } elsif (/^<\/sentence/) {
            $in_s = 0;
        } elsif (/^<s>\t/ && $prev =~ /^"<(\d+?)\.>"\s+<Heur>/) {
            # If the lemma is <s> and the previous line contains a
            # number ending in a full stop and marked with <Heur>, add
            # a sentence break, with the new sentence id taken from
            # the previous line
            print "</sentence>\n" if ($in_s);
            $prev = "<sentence id=\"$1\">\n";
            $s_id = $1;
            $s_idn = 0;
            $in_s = 1;
            next;
        } elsif (! /^</ && ! /^"<(\d+?)\.>"\s+<Heur>/ && ! $in_s) {
            # A token line with no sentence open: add a sentence start
            # tag with the id n-m, where n is the id of the previous
            # specified sentence and m a running number starting from
            # 1 for each n
	    $s_idn += 1;
            print $prev;
	    $prev = ("<sentence id=\"$s_id" . sprintf ("-%02d", $s_idn)
                     . "\">\n");
            $in_s = 1;
            next;
        } elsif (/^<\/text/) {
            # If the line preceding the text end tag was a sentence
            # start tag, remove the latter; otherwise, if it was not a
            # sentence end tag, add one
            if ($prev =~ /^<sentence/) {
                $prev = "";
            } elsif ($prev !~ /^<\/sentence/) {
                print $prev;
                $prev = "</sentence>\n";
            }
            $prev .= $_;
            last;
        }
        print $prev if ($prev);
        $prev = $_;
        END {
            print $prev if ($prev && $prev !~ /^<sentence/);
        }'
	# } elsif (/^\($$/) {
	# 	if ($$. > 1) {
	# 		print "</text>\n";
	# 	}
	# 	print "<text>\n";
	# 	next;
}

fix_file_content () {
    # repair-utf8 fixes invalid UTF-8, whereas ftfy
    # <https://github.com/LuminosoInsight/python-ftfy> fixes
    # UTF-8-encoded CP-1252 characters and also converts typographic
    # quotation marks to ASCII ones.
    specific_fixer=fix_$(echo "$1" | sed -e 's/.*\.//')
    $scriptdir/repair-utf8 --encoding=cp1252 "$1" |
    ftfy |
    perl -CSD -pe '
        # Add a possibly missing newline to the end of the file
	if (! /\n$/) {
	    $_ = "$_\n";
	}
        if (/^<text/ && ! / year=/) {
            # Replace datefrom (and dateto) with year, month and day
            s/datefrom="(\d{4})(\d\d)(\d\d)"/year="$1" month="$2" day="$3"/;
            s/\s+dateto=".*?"//;
        } elsif (/^<\/text>/) {
            $text_end = 1;
        } else {
            # Normalize Unicode ellipsis U+2026 to ASCII ...
            s/\x{2026}/.../g;
        }
        END {
            # Add missing text end tag
            print "</text>\n" unless ($text_end);
        }' |
    $specific_fixer
}

check_file () {
    s_start=$(grep -c '^<sentence' "$1")
    s_end=$(grep -c '^</sentence' "$1")
    if [ $s_start != $s_end ]; then
	echo "sentence tag counts differ: $s_start start tags, $s_end end tags"
    fi
    text_end=$(grep -c '^</text' "$1")
    if [ $text_end != 1 ]; then
	echo "$text_end </text> tags"
    fi
}

fix_file () {
    file=$1
    if [ "x$output_dir" = x ]; then
	infile=$file.orig
	outfile=$file
	if [ ! -e $file.orig ]; then
	    cp -p $file $file.orig
	fi
    else
	infile=$file
	if [ "x$relative_input_dir" != x ]; then
	    outfile=$(echo $file | sed -e "s,^$relative_input_dir,,; s,//*,/,g")
	    if [ "x$outfile" = "x$file" ]; then
		warn "$file not in $relative_input_dir; skipping"
	    fi
	else
	    outfile=$file
	fi
	outfile=$output_dir/$outfile
	mkdir -p $(dirname $outfile)
    fi
    echo "Fixing $infile to $outfile"
    fix_file_content "$infile" > "$outfile"
    check_file "$outfile"
}

fix_files () {
    for file in "$@"; do
	if [ -d "$file" ]; then
            fix_files "$file"/*
	else
	    fix_file "$file"
	fi
    done
}


fix_files "$@"
