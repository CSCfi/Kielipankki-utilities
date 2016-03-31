#! /bin/sh

# Fix the unannotated text files of the Helsinki Corpus of Swahili:
# - Fix Windows-1252 characters to UTF-8
# - Glue full stops to the preceding word
# - Convert Windows CP-1252 apostrophes to ASCII ones
# - Add possibly missing final </text>
# - Add a final newline


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

Fix the unannotated text files of the Helsinki Corpus of Swahili.

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

fix_file_content () {
    # repair-utf8 fixes invalid UTF-8, whereas ftfy
    # <https://github.com/LuminosoInsight/python-ftfy> fixes
    # UTF-8-encoded CP-1252 characters and also converts typographic
    # quotation marks to ASCII ones.
    $scriptdir/repair-utf8 --encoding=cp1252 "$1" |
    ftfy |
    perl -CSD -pe '
        # Remove space before the final full stop
	s/ \.$/./;
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
        }'
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
