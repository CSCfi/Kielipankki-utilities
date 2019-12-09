# -*- coding: utf-8 -*-

# shlib/cwb.sh
#
# Library functions for Bourne shell scripts: functions for Corpus
# Workbench corpora
#
# NOTE: Some functions require Bash. Some functions use "local", which
# is not POSIX but supported by dash, ash.


# Load shlib components for the functions used
shlib_required_libs="base msgs file str"
. $_shlibdir/loadlibs.sh


# list_corpora [--registry registry_dir] [--on-error error_cmd] [corpus_id ...]
#
# List the corpora in the parameters as found in registry_dir
# (default: $cwb_regdir), expanding shell wildcards (but not braces).
# If no corpus_ids are specified, list all corpora found.
# If some listed corpora are not found, call error_cmd (default:
# error) with an error message.
list_corpora () {
    local no_error error_func error_files registry
    no_error=
    error_func=error
    registry=$cwb_regdir
    while [ "x${1##--}" != "x$1" ]; do
	if [ "x$1" = "x--on-error" ]; then
	    error_func=$2
	elif [ "x$1" = "x--registry" ]; then
	    registry=$2
	fi
	shift 2
    done
    if [ "$#" = 0 ]; then
	set -- '*'
    fi
    ls $(add_prefix $registry/ "$@") \
	2> $tmp_prefix.corpid_errors |
    sed -e 's,.*/,,' |
    grep '^[a-z_][a-z0-9_-]*$' > $tmp_prefix.corpids
    if [ -s $tmp_prefix.corpid_errors ]; then
	# Use echo to convert newlines to spaces
	error_files=$(echo $(
	    sed -e 's,^.*cannot access .*/\([^:/]*\):.*$,\1,' \
		< $tmp_prefix.corpid_errors
	))
	$error_func \
	    "Corpora not found in the CWB corpus registry $registry: $error_files"
    fi
    cat $tmp_prefix.corpids
    rm -rf $tmp_prefix.corpids $tmp_prefix.corpid_errors
}

# set_corpus_registry dir
#
# Set the CWB corpus registry directory (CORPUS_REGISTRY, cwb_regdir)
# to dir.
set_corpus_registry () {
    CORPUS_REGISTRY=$1
    export CORPUS_REGISTRY
    corpus_registry_set=1
    cwb_regdir=$CORPUS_REGISTRY
}

# set_corpus_root dir
#
# Set the CWB corpus root directory (corpus_root) to dir and export it
# as CORPUS_ROOT. Also set CORPUS_REGISTRY to dir/registry unless
# already set externally (in which case set cwb_regdir to
# $CORPUS_REGISTRY).
set_corpus_root () {
    CORPUS_ROOT=$1
    export CORPUS_ROOT
    corpus_root=$1
    if [ "x$CORPUS_REGISTRY" = x ] || [ "x$corpus_registry_set" != "x" ]; then
	set_corpus_registry "$corpus_root/registry"
    fi
    cwb_regdir=$CORPUS_REGISTRY
}

# _cwb_registry_find_nonexistent_attrs registry_file prefix attrname ...
_cwb_registry_find_nonexistent_attrs () {
    local _regfile _prefix _new_attrs _attrname
    _regfile=$1
    _prefix=$2
    shift 2
    _new_attrs=
    for _attrname in $*; do
	if ! grep -E -q "^$_prefix$_attrname([ $tab]|\$)" "$_regfile"; then
	    _new_attrs="$_new_attrs $_attrname"
	fi
    done
    echo $_new_attrs
}

# _cwb_registry_make_attrdecls format attrname ...
_cwb_registry_make_attrdecls () {
    local _format _attrname
    _format=$1
    shift
    for _attrname in $*; do
	echo $_attrname;
    done |
    awk '{printf "'"$_format"'\\n", $0}'
}

# cwb_registry_reorder_posattrs corpus attrname1 attrname2
#
# Reorded the positional attributes in the registry file for corpus so
# that attrname2 follows immediately attrname1. If one or both of the
# attributes do not exist, do nothing.
cwb_registry_reorder_posattrs () {
    local corpus regfile
    if [ "x$1" = x ] || [ "x$2" = x ] || [ "x$3" = x ]; then
	lib_error "Invalid arguments to cwb_registry_reorder_posattrs: requires corpus, attrname1, attrname2"
    fi
    corpus=$1
    attrname1=$2
    attrname2=$3
    if ! corpus_exists $corpus; then
	lib_error "cwb_registry_reorder_posattrs: corpus $corpus does not exist"
    fi
    regfile="$cwb_regdir/$corpus"
    # Do nothing if the corpus does not have both the first and the
    # second attribute
    if ! grep -qs "^ATTRIBUTE $attrname1\$" "$regfile" ||
	! grep -qs "^ATTRIBUTE $attrname2\$" "$regfile";
    then
	return
    fi
    awk '
        /^ATTRIBUTE '"$attrname1"'$/ {
            print
            print "ATTRIBUTE '"$attrname2"'"
            next
        }
        /^ATTRIBUTE '"$attrname2"'$/ { next }
        { print }
    ' "$regfile" > "$regfile.new"
    ensure_perms "$regfile.new"
    replace_file "$regfile" "$regfile.new"
}

# cwb_registry_add_posattr corpus attrname ...
#
# Add positional attributes to the CWB registry file for corpus at the
# end of the list of positional attributes if they do not already
# exist. (The function does not use cwb-regedit, because it would
# append the attributes at the very end of the registry file.)
cwb_registry_add_posattr () {
    local _corpus _regfile _new_attrs _new_attrdecls
    _corpus=$1
    shift
    _regfile="$cwb_regdir/$_corpus"
    _new_attrs=$(
	_cwb_registry_find_nonexistent_attrs "$_regfile" "ATTRIBUTE " $*
    )
    _new_attrdecls="$(_cwb_registry_make_attrdecls "ATTRIBUTE %s" $_new_attrs)"
    if [ "x$_new_attrdecls" != "x" ]; then
	cp -p "$_regfile" "$_regfile.old"
	awk '/^ATTRIBUTE/ { prev_attr = 1 }
	     /^$/ && prev_attr { printf "'"$_new_attrdecls"'"; prev_attr = 0 }
	     { print }' "$_regfile.old" > "$_regfile"
    fi
    ensure_perms "$_regfile" "$_regfile.old"
}

# cwb_registry_add_structattr corpus struct [attrname ...]
#
# Add structural attributes (annotations) of the structure struct to
# the CWB registry file for corpus at the end of the list of
# structural attributes if they do not already exist. If attrname are
# not specified, only add struct without annotations. (The function
# does not use cwb-regedit, because it would append the attributes at
# the very end of the registry file.)
cwb_registry_add_structattr () {
    local _corpus _struct _regfile _new_attrs _new_attrs_prefixed
    local _new_attrdecls _xml_attrs
    _corpus=$1
    _struct=$2
    shift 2
    _regfile="$cwb_regdir/$_corpus"
    if ! grep -q "STRUCTURE $_struct\$" "$_regfile"; then
	cp -p "$_regfile" "$_regfile.old"
	awk '
            function output () {
                printf "\n# <'$_struct'> ... </'$_struct'>\n# (no recursive embedding allowed)\nSTRUCTURE '$_struct'\n"
                printed = 1
            }
            /^$/ { empty = empty "\n"; next }
            /^(# Yours sincerely|ALIGNED)/ {
                output()
                if (empty == "") { empty = "\n" }
            }
            /./ { printf empty; print; empty = "" }
            END {
                if (! printed) { output() }
            }
        ' "$_regfile.old" > "$_regfile"
    fi
    _new_attrs=$(
	_cwb_registry_find_nonexistent_attrs "$_regfile" \
	    "STRUCTURE ${_struct}_" $*
    )
    if [ "x$_new_attrs" != "x" ]; then
	_new_attrs_prefixed=$(
	    echo $_new_attrs |
	    awk '{ for (i = 1; i <= NF; i++) { print "'$_struct'_" $i } }'
	)
	_new_attrdecls="$(
	    _cwb_registry_make_attrdecls "STRUCTURE %-20s # [annotations]" $_new_attrs_prefixed
        )"
	_xml_attrs="$(
	    echo $_new_attrs |
	    awk '{ for (i = 1; i <= NF; i++) { printf " %s=\\\"..\\\"", $i } }'
	)"
	cp -p "$_regfile" "$_regfile.old"
	awk '
            /^# <'$_struct'[ >]/ { sub(/>/, "'"$_xml_attrs"'>") }
            /^STRUCTURE '$_struct'(_|$)/ {
                prev_struct = 1
                print
                next
            }
            prev_struct {
                printf "'"$_new_attrdecls"'"
                printed = 1
                prev_struct = 0
            }
            { print }
            END {
                if (! printed) { printf "'"$_new_attrdecls"'" }
            }
        ' "$_regfile.old" > "$_regfile"
    fi
    ensure_perms "$_regfile" "$_regfile.old"
}

# cwb_index_posattr corpus attrname ...
#
# Index and compress encoded CWB positional attributes attrname in
# corpus (without using cwb-make).
cwb_index_posattr () {
    local _corpus _attrname
    _corpus=$1
    shift
    for _attrname in $*; do
	$cwb_bindir/cwb-makeall -M 2000 $_corpus $_attrname
	$cwb_bindir/cwb-huffcode -P $_attrname $_corpus
	$cwb_bindir/cwb-compress-rdx -P $_attrname $_corpus
	for ext in "" .rdx .rev; do
	    rm "$corpus_root/data/$_corpus/$_attrname.corpus$ext"
	done
    done
}


# corpus_remove_attrs corpus attrname ...
#
# Remove the listed attribute names from corpus: both data files and
# information in the registry file.
corpus_remove_attrs () {
    local corpus attrname attrtype
    corpus=$1
    shift
    for attrname in $*; do
	attrtype=$(corpus_get_attr_type $corpus $attrname)
	if [ "x$attrtype" != x ]; then
	    cwb_registry_remove_attr $corpus $attrname $attrtype
	    rm "$corpus_root/data/$corpus/$attrname."*
	    if [ $attrtype = "s" ] && ! in_str _ $attrname; then
		rm "$corpus_root/data/$corpus/$attrname"_*.*
	    fi
	fi
    done
}

# cwb_registry_remove_attr corpus attrname [attrtype]
#
# Remove attribute attrname of type attrypte from the registry file of
# corpus. If attrtype is omitted, it is found out.
cwb_registry_remove_attr () {
    local corpus attrname attrtype regfile struct attrname0
    corpus=$1
    attrname=$2
    if [ "x$3" != x ]; then
	attrtype=$3
    else
	attrtype=$(corpus_get_attr_type $corpus $attrname)
    fi
    regfile="$cwb_regdir/$corpus"
    cp -p "$regfile" "$regfile.old" ||
	error "Could not copy $regfile to $regfile.old"
    if [ $attrtype = "s" ]; then
	if in_str _ $attrname; then
	    struct=${attrname%%_*}
	    attrname0=${attrname#*_}
	    grep -v "^STRUCTURE $attrname" "$regfile.old" |
		awk "/^# <$struct / {
		         sub(/ $attrname0=\"\.\.\"/, \"\"); print; next
		     }
		     { print }
		" > "$regfile"
	else
	    awk "/^# <$attrname[ >]/,/^ *$/ {next}
                 {print}" "$regfile.old" > "$regfile"
	fi
    else
	grep -v -E "^(ATTRIBUTE|ALIGNED) $attrname" "$regfile.old" > "$regfile"
    fi
    ensure_perms "$regfile" "$regfile.old"
}


# corpus_list_attrs [options] corpus attrtypes [attr_regex]
#
# List the names of attributes in corpus, of the types listed in
# attrtypes, a space-separated list of attribute types that are words
# beginning with p (positional), s (structural), a (alignment) or "*"
# (any type). If attr_regex is specified, list only the attributes
# matching it (an extended regular expression as recognized by AWK).
#
# In the output, each attribute name is on its own line. Returns 1 if
# the registry file for corpus is not found or attrtypes contains an
# invalid attribute type.
#
# Options:
#   --show-type: Precede each attribute name is preceded by its type
#     (p, s, a) and a space.
#   --feature-set-slash: Suffix the names of feature-set-valued
#     attributes with a slash. Note that this may slow down the
#     function.
corpus_list_attrs () {
    local corpus attrtypes attrtype attrtypes_re show_type slashes attr_re attrs attrname
    show_type=
    slashes=
    while [ "x${1##--*}" = x ]; do
	if [ "x$1" = "x--show-type" ]; then
	    show_type=1
	elif [ "x$1" = "x--feature-set-slash" ]; then
	    slashes=1
	else
	    lib_error "corpus_list_attrs: unrecognized option $1"
	fi
	shift
    done
    corpus=$1
    attrtypes=$2
    attr_re=".*"
    if [ "x$3" != x ]; then
	attr_re=$3
    fi
    if [ ! -e $cwb_regdir/$corpus ]; then
	return 1
    fi
    if [ "$attrtypes" = "*" ]; then
	attrtypes="p s a"
    fi
    attrtypes_re=
    for attrtype in $attrtypes; do
	case $attrtype in
	    [pP]* )
		attrtype="ATTRIBUTE"
		;;
	    [sS]* )
		attrtype="STRUCTURE"
		;;
	    [aA]* )
		attrtype="ALIGNED"
		;;
	    * )
		return 1
		;;
	esac
	attrtypes_re="$attrtypes_re|$attrtype"
    done
    attrtypes_re=${attrtypes_re#|}
    attrs="$(
	awk "BEGIN {
	         map[\"ATTRIBUTE\"] = \"p\"
		 map[\"STRUCTURE\"] = \"s\"
		 map[\"ALIGNED\"] = \"a\"
	     }
	     /^($attrtypes_re) (\\<$attr_re\\>)/ {print map[\$1] \" \" \$2}
        " $cwb_regdir/$corpus
	)"
    if [ "x$slashes" != x ]; then
	attrs="$(
	    echo "$attrs" |
		while read attrtype attrname; do
		    printf "$attrtype $attrname"
		    if [ "$attrtype" != "a" ] &&
			   corpus_attr_is_featset_valued $corpus $attrtype $attrname; then
			printf "/"
		    fi
		    printf "\n"
		done
	    )"
    fi
    if [ "x$show_type" = x ]; then
	echo "$attrs" |
	    cut -d" " -f2
    else
	echo "$attrs"
    fi
}


# corpus_has_attr corpus attrtypes attrname
#
# Return true if corpus has attribute attrname of any of the types in
# attrtype, a space separated list of p (positional), s (structural),
# a (alignment) or "*" (any).
corpus_has_attr () {
    local corpus attrtypes attrname
    corpus=$1
    attrtypes=$2
    attrname=$3
    corpus_list_attrs $corpus "$attrtypes" |
    grep -E -q -s "^$attrname$"
}

# corpus_get_attrtype corpus attrname
#
# Output the type of attribute attrname in corpus: p (positional), s
# (structural) or a (alignment).
corpus_get_attr_type () {
    nth_arg 1 $(corpus_list_attrs --show-type $1 '*' $2)
}

# corpus_attr_is_featset_valued corpus attrtype attrname
#
# Return true (0) if the attribute attrname of type attrtype in corpus
# is feature-set-valued. attrtype should begin with either p
# (positional) or s (structural) (lower- or upper-case). On error,
# return 2.
corpus_attr_is_featset_valued () {
    local corpus attrtype attrname errfile result
    corpus=$1
    attrtype=$2
    attrname=$3
    errfile=$tmp_prefix.corpus_attr_is_featset_valued.err
    case $attrtype in
	[pP]* )
	    result=$(
		$cwb_bindir/cwb-lexdecode -P $attrname -p '[^|].*[^|]' \
					    $corpus 2> "$errfile" |
		    head -1 | wc -l
		)
	    if [ -s "$errfile" ]; then
		cat "$errfile" > /dev/stderr
		return 2
	    else
		return $result
	    fi
	    ;;
	[sS]* )
	    # Structure without annotated values cannot have be
	    # feature-set-valued
	    if [ "${attrname##*_}" = "$attrname" ]; then
		return 1
	    fi
	    # Heuristic: most likely an attribute whose first 100
	    # values look like feature-sets is feature-set-valued.
	    result=$(
		$cwb_bindir/cwb-s-decode -n $corpus -S $attrname 2> "$errfile" |
		    head -100 | grep -c '^|.*|$'
		  )
	    if [ -s "$errfile" ]; then
		cat "$errfile" > /dev/stderr
		return 2
	    else
		[ "$result" = "100" ]
		return
	    fi
	    ;;
	* )
	    return 2
    esac
}

# corpus_exists corpus
#
# Return true if corpus exists (cwb-describe-corpus returns true).
corpus_exists () {
    $cwb_bindir/cwb-describe-corpus $1 > /dev/null 2> /dev/null
}

# get_corpus_token_count corpus
#
# Print the number of tokens in corpus.
get_corpus_token_count () {
    $cwb_bindir/cwb-describe-corpus -s $1 |
    awk '$1 ~ /^size/ {print $3}'
}

# get_corpus_struct_count corpus struct
#
# Print the number of structures struct in corpus.
get_corpus_struct_count () {
    $cwb_bindir/cwb-describe-corpus -s $1 |
    awk "/^s-ATT $2"' / {print $3}'
}


# get_corpus_posattr_type_count corpus attrname
#
# Print the number of distinct values ("types") for the positional
# attribute attrname in corpus.
get_corpus_posattr_type_count () {
    $cwb_bindir/cwb-describe-corpus -s $1 |
    awk "/^p-ATT $2 "' / {print $5}'
}


# get_corpus_struct_type_count corpus attrname
#
# Print the number of distinct values ("types") for the structural
# attribute attrname in corpus.
get_corpus_struct_type_count () {
    $cwb_bindir/cwb-s-decode -n $1 -S $2 |
	sort -u |
	wc -l
}


# get_attr_num attrname attrlist
#
# Output the one-based number of positional attribute attrname
# (possibly followed by a slash) in attrlist.
get_attr_num () {
    # set -vx
    local attrname attrlist index
    attrname=$1
    attrlist=$2
    index=$(word_index $attrname $attrlist)
    if [ "$index" = -1 ]; then
	index=$(word_index $attrname/ $attrlist)
    fi
    echo $index
    # set +vx
}


# Initialize variables

# Root directory, relative to which the corpus directory resides
set_corpus_root ${CORPUS_ROOT:-$(find_existing_dir -d "" $default_corpus_roots)}

# The directory in which CWB binaries reside
cwb_bindir=${CWB_BINDIR:-$(find_existing_dir -e cwb-describe-corpus $default_cwb_bindirs)}
