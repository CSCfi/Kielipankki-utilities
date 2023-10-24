#! /bin/sh
# -*- coding: utf-8 -*-


# TODO:
# - Ensure that field headings work
# - Fix fieldspec mappings to work
# - Ordered input by default
# - Convert to use vrt-convert-chars instead of vrt-convert-chars.py
#   (not quite straightforward)


progname=`basename $0`
progdir=`dirname $0`

usage_header="Usage: $progname [options] corpus [input.tsv ...]

Add (encode) CWB structural attributes to a corpus already encoded from input
in TSV format by either using attribute values in the order that they are in
the input or based on a key (id) in the input."

optspecs='
struct-name|structural-attribute-name|element-name=STRUCT "text"
    Add the attributes to structural attribute (element) STRUCT.
attribute-names=ATTRNAMELIST attrnames
    Add the attributes listed in ATTRNAMELIST, separated by spaces. The list
    items may be either simple attribute names or mappings of the form
    ATTRNAME:FIELDSPEC, where FIELDSPEC is either an input field number or
    name as specified by the input field headings. For simple attribute names,
    if --input-has-field-headings has not been specified, the attributes are
    taken from the input in the order in which they are specified in
    ATTRNAMELIST, skipping the possible key field. If an attribute name is
    followed by a slash (/), the values of the attribute are treated as
    feature sets: vertical bars in them are preserved unencoded.
input-has-field-headings has_headings
    The first line of the TSV input is a field heading row.
input-in-corpus-order|ordered-input ordered_input
    Add the values in the input in the order they are specified to the
    structures STRUCT, instead of matching by a key attribute.
key-attribute-name=ATTRNAME "id" key_attr
    Use the attribute in structure STRUCT as the key by which to choose values
    from the input, unless --input-in-corpus-order is specified.
key-field=FIELDSPEC "1" key_field
    Use the field FIELDSPEC as the key field in the input to be matched by the
    values of the key attribute to choose the values, unless
    --input-in-corpus-order is specified. FIELDSPEC may be either a field
    number (beginning from 1) or a field name, if --input-has-heading-row is
    specified.
force|overwrite
    Overwrite possible existing values in the corpus data of the attributes to
    be added.
'


. $progdir/korp-lib.sh

# cleanup_on_exit=

cwb_s_decode=$cwb_bindir/cwb-s-decode
cwb_s_encode=$cwb_bindir/cwb-s-encode
encode_special_chars="$progdir/vrt-convert-chars.py --encode"
structpos_file=$tmp_prefix.struct_pos
input_file=$tmp_prefix.input


# Process options
eval "$optinfo_opt_handler"


make_attrnames_bare () {
    local attrspec attrname
    attrnames_bare=
    for attrspec in $attrnames; do
        # Remove possible mapping
        attrname=${attrspec%:*}
        # Remove possible trailing slash marking feature-set attribute
        attrname=${attrname%/}
	attrnames_bare="$attrnames_bare $attrname"
    done
}

check_existing_attrs () {
    local corpus attrname attrname_full existing_attrs msg_prefix pron
    corpus=$1
    existing_attrs=
    for attrname in $attrnames_bare; do
	attrname_full=${struct_name}_$attrname
	if corpus_has_attr $corpus s $attrname_full; then
	    existing_attrs="$existing_attrs $attrname_full"
	fi
    done
    if [ "x$existing_attrs" != x ]; then
	if [ $(count_words $existing_attrs) = 1 ]; then
	    msg_prefix="Attribute$existing_attrs already exists"
	    pron="it"
	else
	    msg_prefix="Attributes$existing_attrs already exist"
	    pron="them"
	fi
	msg_prefix="$msg_prefix in corpus $corpus"
	if [ "x$force" != x ]; then
	    warn "$msg_prefix; overwriting $pron as --force was specified"
	else
	    error "$msg_prefix; please specify --force to overwrite $pron" 
	fi
    fi
}

make_struct_pos () {
    local corpus key_struct
    corpus=$1
    key_struct=${struct_name}
    if [ "x$ordered_input" = x ]; then
	key_struct=${key_struct}_${key_attr}
    fi
    $cwb_s_decode $corpus -S $key_struct
}

get_fieldnum () {
    local attrspec attrnum fieldname fieldnum
    attrspec=$1
    attrnum=$2
    fieldname=${attrspec#*:}
    if [ "$fieldname" = "$attrspec" ]; then
	fieldnum=$attrnum
    elif is_int $fieldname; then
	if [ $fieldname -le $input_field_count ]; then
	    fieldnum=$fieldname
	else
	    error "Input field number $fieldname greater than the number of input fields $input_field_count"
	fi
    elif [ "x$has_headings" != x ]; then
	fieldnum=$(word_index $fieldname $heading_fieldnames)
	if [ "$fieldnum" -eq -1 ]; then
	    error "Field $fieldname not found on the input heading line"
	fi
    else
	error "Field name mapping ($attrspec) is meaningful only with --input-has-field-headings"
    fi
    echo "$fieldnum"
}

check_input_length () {
    local corpus infile input_line_count corpus_struct_count msg_prefix
    corpus=$1
    infile=$2
    input_line_count=$(wc -l < "$infile")
    if [ "x$has_headings" != x ]; then
        input_line_count=$(($input_line_count - 1))
    fi
    if [ $input_line_count = 0 ]; then
        error "Empty input"
    fi
    if [ "x$ordered_input" = x ]; then
        return
    fi
    corpus_struct_count=$(get_corpus_struct_count $corpus $struct_name)
    if [ $input_line_count != $corpus_struct_count ]; then
        msg_prefix="Input contains $input_line_count lines but corpus has $corpus_struct_count $struct_name structures"
        if [ "x$force" = x ]; then
            error "$msg_prefix; please specify --force to ignore"
        else
            warn "$msg_prefix; proceeding anyway as --force was specified"
        fi
    fi
}

order_by_key () {
    local struct_count fieldnum saved_lc_all
    struct_count=$(nth_arg 1 $(wc -l "$structpos_file"))
    fieldnum=$key_fieldnum
    seq $struct_count > $tmp_prefix.structnum
    saved_lc_all=$LC_ALL
    LC_ALL=C
    # Prefix the structure positions with line numbers to be able to
    # restore the order later and sort it by the key field (format
    # "linenum begin end key").
    paste $tmp_prefix.structnum "$structpos_file" |
    sort -t"$tab" -k4,4 > $tmp_prefix.structposnum
    # Read input from stdin and sort it by the key field.
    sort -t"$tab" -k$fieldnum,$fieldnum |
    # Join by the key field to get lines containing structure
    # positions and the values of the attributes to be added (format
    # "key linenum begin end value ...").
    join -t"$tab" -14 -2$fieldnum -a1 $tmp_prefix.structposnum - |
    # Restore the original structure order
    sort -t"$tab" -k2,2n |
    # Remove line numbers and key field values (format "begin end
    # value ...")
    cut -f3- |
    # Add empty values where the values were missing
    awk -F"$tab" "BEGIN { fieldcnt = $input_field_count }"'
                  {
		      if (NF < fieldcnt) {
			  for (i = NF; i < fieldcnt; i++) {
			      $0 = $0 "\t"
			  }
		      }
		      print
                  }'
    LC_ALL=$saved_lc_all
}

process_input () {
    local corpus linenum1
    corpus=$1
    shift
    comprcat "$@" > "$input_file.tmp"
    check_input_length $corpus "$input_file.tmp"
    input_field_count=$(count_words $(head -1 "$input_file.tmp"))
    if [ "x$has_headings" = x ]; then
        linenum1=1
    else
        linenum1=2
	heading_fieldnames=$(head -1 "$input_file.tmp")
    fi
    # Call make_input_fieldnums here because it requires (indirectly
    # in get_fieldnum) $heading_fieldnames and it sets
    # $featset_fieldnums_opt required below
    make_input_fieldnums
    tail -n+$linenum1 "$input_file.tmp" |
    $encode_special_chars $featset_fieldnums_opt |
    if [ "x$ordered_input" = x ]; then
	order_by_key
    else
	paste "$structpos_file" - 
    fi > "$input_file"
}

make_input_fieldnums () {
    local heading_fieldnames attrspec attrnum fieldnum attrname \
          featset_fieldnums
    input_fieldnums=
    featset_fieldnums=
    key_fieldnum=$(get_fieldnum $key_field $key_field)
    attrnum=1
    for attrspec in $attrnames; do
        fieldnum=$(get_fieldnum $attrspec $attrnum)
	input_fieldnums="$input_fieldnums $fieldnum"
        attrname=${attrspec%:*}
        # If attribute name ends in a slash, treat it as having
        # feature-set values
        if [ $attrname != ${attrname%/} ]; then
            # Numbers in featset_fieldnums take into account the
            # possible key field, as it is included in the input to
            # vrt-convert-chars.py
            if [ "x$ordered_input" = x ] && [ $fieldnum -ge $key_fieldnum ];
            then
                fieldnum=$(($fieldnum + 1))
            fi
            featset_fieldnums="$featset_fieldnums $fieldnum"
        fi
	attrnum=$(($attrnum + 1))
    done
    # featset_fieldnums_opt is global
    featset_fieldnums_opt=
    if [ "x$featset_fieldnums" != x ]; then
        # Delimit field numbers with commas to be able to use
        # $featset_fieldnums_opt without double quotes
        featset_fieldnums_opt="--feature-set-attributes=$(delimit "," $featset_fieldnums)"
    fi
}

encode_attr () {
    local corpus attrname fieldnum
    corpus=$1
    attrname=$2
    fieldnum=$(($3 + 2))
    cut -f1,2,$fieldnum "$input_file" |
    awk -F"$tab" 'NF < 3 { print $0 "\t"; next } { print }' |
    exit_on_error $cwb_s_encode -d $corpus_root/data/$corpus -B -c utf8 \
    	-V ${struct_name}_$attrname
}

encode_attrs () {
    local corpus attrnum attrname fieldnum
    corpus=$1
    attrnum=1
    for attrname in $attrnames_bare; do
	fieldnum=$(nth_arg $attrnum $input_fieldnums)
	encode_attr $corpus $attrname $fieldnum 
	cwb_registry_add_structattr $corpus $struct_name $attrname
	attrnum=$(($attrnum + 1))
    done
}

main () {
    local corpus
    corpus=$1
    if [ "x$corpus" = x ]; then
	error "Please specify corpus id as the first argument"
    fi
    shift
    if [ "x$attrnames" = x ]; then
	error "Please specify attribute name via --attribute-names"
    fi
    make_attrnames_bare
    check_existing_attrs $corpus
    make_struct_pos $corpus > "$structpos_file"
    process_input $corpus "$@"
    encode_attrs $corpus
}


main "$@"
