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
# (default: $cwb_regdir), expanding shell wildcards. The result is
# sorted (as done by ls) and uniquified. If no corpus_ids are
# specified, list all corpora found. If some listed corpora are not
# found, call error_cmd (default: error) with an error message and
# return false (1).
list_corpora () {
    local retval error_func error_files registry
    retval=0
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
    # ls sorts its output, so we can use uniq instead of sort -u
    ls $(add_prefix $registry/ "$@") \
	2> $tmp_prefix.corpid_errors |
    sed -e 's,.*/,,' |
    grep '^[a-z_][a-z0-9_-]*$' |
    uniq > $tmp_prefix.corpids
    if [ -s $tmp_prefix.corpid_errors ]; then
	# Use echo to convert newlines to spaces
	# On some systems, the file name in the error message is
	# enclosed in single quotes; on others not.
	error_files=$(echo $(
	    sed -e "s,^.*cannot access .*/\([^:/]*\):.*\$,\1,;
                    s,'\$,," \
		< $tmp_prefix.corpid_errors
	))
	$error_func \
	    "Corpora not found in the CWB corpus registry $registry: $error_files"
        retval=1
    fi
    cat $tmp_prefix.corpids
    rm -rf $tmp_prefix.corpids $tmp_prefix.corpid_errors
    return $retval
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
    local _format
    _format=$1
    shift
    # Output literal \n as the result is to be used in Awk printf
    printf "$_format\\\\n" $*
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
    if [ "x$_new_attrs" != "x" ]; then
        _new_attrdecls="$(_cwb_registry_make_attrdecls "ATTRIBUTE %s" $_new_attrs)"
	cp -p "$_regfile" "$_regfile.old"
	awk '/^ATTRIBUTE/ { prev_attr = 1 }
	     /^$/ && prev_attr { printf "'"$_new_attrdecls"'"; prev_attr = 0 }
	     { print }' "$_regfile.old" > "$_regfile"
        cwb_registry_add_change_comment \
            $_corpus \
            "Added positional attribute$(plural "$_new_attrs") $(delimit ", " $_new_attrs)"
    fi
    ensure_perms "$_regfile" "$_regfile.old"
}

# _make_embedded_attrs depth attrname ...
#
# Output attrnames and their embedded variants (suffixed with a
# digit). If depth = 0, output attrnames as such. If depth = N > 0,
# the output contains "attrname attrname1 ... attrnameN" for each
# attrname. The function can be used for both structures and their
# attributes (struct_attr).
_make_embedded_attrs () {
    local depth attr d result
    depth=$1
    shift
    if [ $depth -le 0 ]; then
        result="$@"
    else
        result=
        for attr in "$@"; do
            result="$result $attr"
            d=1
            while [ $d -le $depth ]; do
                result="$result $attr$d"
                d=$(($d + 1))
            done
        done
    fi
    safe_echo $result
}

# _cwb_registry_add_struct regfile struct depth
#
# If structure struct does not exist in the registry file regfile, add
# it after existing structural attributes (without annotation
# attributes), with recursive embedding of up to depth levels.
_cwb_registry_add_struct () {
    local regfile struct depth
    regfile=$1
    struct=$2
    depth=$3
    cp -p "$regfile" "$regfile.old"
    awk '
        # Return a comment on the allowed nesting depth for struct
        function make_embedding_comment (struct, depth) {
            if (depth == 0) {
                return "(no recursive embedding allowed)"
            } else {
                val = "(" depth " levels of embedding: <" struct ">, "
                for (d = 1; d <= depth; d++) {
                    val = val "<" struct d ">"
                    if (d < depth) {
                        val = val ", "
                    }
                }
                return val ")"
                # cwb-encode would append a full stop after the
                # closing bracket here, but we do not, as cwb-encode
                # does not append it after "(no recursive embedding
                # allowed)"
            }
        }
        function output () {
            print "\n# <'$struct'> ... </'$struct'>"
            print "# " make_embedding_comment("'$struct'", '$depth')
            print "STRUCTURE '$struct'"
            for (d = 1; d <= '$depth'; d++) {
                print "STRUCTURE '$struct'" d
            }
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
    ' "$regfile.old" > "$regfile"
}

# _cwb_registry_get_struct_depth regfile struct
#
# Output the number of recursive embedding levels (nesting depth)
# specified for struct in CWB registry file regfile; 0 if struct does
# not exist in regfile.
_cwb_registry_get_struct_depth () {
    local regfile struct depth
    regfile=$1
    struct=$2
    depth=$(grep -B1 "STRUCTURE $_struct\$" "$_regfile")
    depth=${depth#*\(}
    depth=${depth%% *}
    if [ "x$depth" = x ] || [ "$depth" = "no" ]; then
        depth=0
    fi
    echo $depth
}


# _cwb_registry_add_structattrs regfile struct new_attrs new_attrs_prefixed
#
# Add to CWB registry file regfile structural attributes (annotations)
# new_attrs to structure struct, which is assumed to be already
# present in regfile. new_attrs contains bare attribute (annotation)
# names, whereas new_attrs_prefixed contains them prefixed with
# struct_ and containing the digit-suffixed variants for structures
# allowing recursive embedding (nesting).
_cwb_registry_add_structattrs () {
    local regfile struct new_attrs new_attrs_prefixed new_attrdecls xml_attrs
    regfile=$1
    struct=$2
    new_attrs=$3
    new_attrs_prefixed=$4
    new_attrdecls="$(
        _cwb_registry_make_attrdecls "STRUCTURE %-20s # [annotations]" $new_attrs_prefixed
    )"
    xml_attrs="$(printf ' %s=\\"..\\"' $new_attrs)"
    cp -p "$regfile" "$regfile.old"
    awk '
        /^# <'$struct'[ >]/ { sub(/>/, "'"$xml_attrs"'>") }
        /^STRUCTURE '$struct'(_|$)/ {
            prev_struct = 1
            print
            next
        }
        # Add the declarations at the end of the attribute
        # declarations for struct: before a blank line, a comment
        # line beginning with "# <" or a STRUCTURE declaration of
        # a different structural attribute.
        prev_struct && ! printed \
            && (/^ *$/ || /^# </ \
                || (/^STRUCTURE / && ! /^STRUCTURE '$struct'(_|[0-9]?$)/)) {
            printf "'"$new_attrdecls"'"
            printed = 1
            prev_struct = 0
        }
        { print }
        END {
            if (! printed) { printf "'"$new_attrdecls"'" }
        }
    ' "$regfile.old" > "$regfile"
}

# cwb_registry_add_structattr corpus struct [depth] [attrname ...]
#
# Add structural attributes (annotations) of the structure struct to
# the CWB registry file for corpus at the end of the list of
# structural attributes if they do not already exist.
#
# depth is an integer (0...9) specifying the number of recursive
# embedding (nesting) levels for struct; if omitted, 0 is assumed. If
# the registry file already contains structure struct, the number of
# levels is taken from the registry file and depth has no effect.
# (TODO: Allow changing the number of embedding levels or warn if
# depth differs from the existing number of levels.)
#
# If attrname are not specified, only add struct without annotations.
#
# (The function does not use cwb-regedit, because it would append the
# attributes at the very end of the registry file.)
cwb_registry_add_structattr () {
    local _corpus _struct _depth _regfile _new_attrs _new_attrs_prefixed
    local _new_attrs_embed _added_attrs _attr _attrs
    _corpus=$1
    _struct=$2
    shift 2
    if word_in "$1" "0 1 2 3 4 5 6 7 8 9"; then
        _depth=$1
        shift
    else
        _depth=0
    fi
    # Strip possible trailing slash
    for _attr in "$@"; do
        _attrs="$_attrs ${_attr%/}"
    done
    _regfile="$cwb_regdir/$_corpus"
    _added_attrs=
    # If struct does not exist in the registry file, add it after
    # existing structural attributes
    if ! grep -q "STRUCTURE $_struct\$" "$_regfile"; then
        # If the structure can be nested (embedded), also add
        # structures structN where N = 1...depth
        _added_attrs=$(_make_embedded_attrs $_depth $_struct)
        _cwb_registry_add_struct "$_regfile" $_struct $_depth
    else
        # Get the existing number of struct embedding levels from the
        # registry file
        _depth=$(_cwb_registry_get_struct_depth "$_regfile" $_struct)
    fi
    _new_attrs=$(
	_cwb_registry_find_nonexistent_attrs "$_regfile" \
	    "STRUCTURE ${_struct}_" $_attrs
    )
    if [ "x$_new_attrs" != "x" ]; then
        # Add attribute names suffixed with a digit for each embedding
        # level
        _new_attrs_embed=$(_make_embedded_attrs $_depth $_new_attrs)
	_new_attrs_prefixed=$(add_prefix ${_struct}_ $_new_attrs_embed)
        _cwb_registry_add_structattrs \
            $_regfile $_struct "$_new_attrs" "$_new_attrs_prefixed"
    fi
    _added_attrs="$_added_attrs $_new_attrs_prefixed"
    if [ "x$_added_attrs" != x ]; then
        cwb_registry_add_change_comment \
            $_corpus \
            "Added structural attribute$(plural "$_added_attrs") $(delimit ", " $_added_attrs)"
    fi;
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
#
# NOTE: This function is superseded by corpus_remove_attr further
# below.
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

# _corpus_manage_attr mode [options] corpus attrname_src [attrname_dst]
#
# Copy (if mode = "copy"), rename (if mode = "rename") or alias, i.e.
# symlink (if mode = "alias") attribute attrname_src as attrname_dst,
# or remove (if mode = "remove") attribute attrname_src in corpus:
# both data files and information in the registry file.
#
# Options:
# --backup-suffix SUFFIX: Use SUFFIX instead of .bak-YYYYMMDDhhmmss as
#     the suffix for the backups of the registry file and possible
#     existing destination data files; use "" not to make backups.
# --comment COMMENT: Append comment COMMENT to the standard comment to
#     be added to the registry file. If COMMENT begins with an
#     exclamation mark, omit the standard comment and add only COMMENT
#     (with the leading exclamation mark removed). If COMMENT is
#     empty, omit the comment altogether.
# --omit-comment: Omit the comment (an alias of '--comment ""').
# --attribute-comment: Add comment immediately after the attribute
#     declaration, instead of to the changelog section at the end of
#     the registry file.
#
# Note that options follow mode (to make it easier to pass the
# arguments from specific functions using a fixed mode).
#
# The source attribute must exist and the destination may not be the
# same as the source. If the destination attribute exists, it must
# have the same type as the source. If it is a structural attribute
# with annotations, the bare structure must be the same. If the
# destination attribute does not exist, and if the source attribute is
# structural with annotations, the destination name must contain an
# underscore, or if the source is bare structure, the destination name
# must not contain underscore. If these conditions are not met, the
# function returns 1.
#
# FIXME: Would it actually be better to use hard links instead of
# symbolic ones for alias? Renaming or removing an attribute that
# another attribute links to makes the symbolic links dangle, whereas
# that would not be a problem for hard links. On the other hand,
# hard-linked files are more difficult to recognize as links. Another
# option might be to try to check for such cases and either disallow
# them, warn on them or apply the operation also to the linking
# attribute. We could also have an option for hard links.
_corpus_manage_attr () {
    local mode comment comment_verb corpus attrname_src attrname_dst \
	  attrname_bak cmd attrtype_src attrtype_dst baksuff fnames fname \
	  fname_dst attrtype_word attr_comment comment_extra
    mode=$1
    comment="__DEFAULT"
    comment_extra=
    baksuff=.bak-$(date +%Y%m%d%H%M%S)
    attr_comment=
    while [ "${2#--}" != "$2" ]; do
	if [ "$2" = "--comment" ]; then
	    comment_extra=$3
            if [ "x$comment_extra" = x ]; then
                comment=
            fi
	    shift 2
	elif [ "$2" = "--backup-suffix" ]; then
	    baksuff=$3
	    shift 2
	elif [ "$2" = "--attribute-comment" ]; then
	    attr_comment=1
	    shift
	elif [ "$2" = "--omit-comment" ]; then
	    comment=
	    shift
	else
	    lib_error "_corpus_manage_attr: Unrecognized option $2"
	fi
    done
    corpus=$2
    attrname_src=$3
    # Destination is empty for remove
    attrname_dst=$4
    if [ "$mode" = "copy" ]; then
	cmd="cp -p"
	comment_verb="Copied"
    elif [ "$mode" = "rename" ]; then
	cmd="mv"
	comment_verb="Renamed"
    elif [ "$mode" = "alias" ]; then
	cmd="ln -sf"
	comment_verb="Aliased"
	# Registry information is copied
	mode=copy
    elif [ "$mode" = "remove" ]; then
	cmd="rm -f"
	comment_verb="Removed"
    else
	lib_error "_corpus_manage_attr: Invalid mode \"$mode\""
    fi
    attrtype_src=$(corpus_get_attr_type_full $corpus $attrname_src)
    # Source attribute needs to exist and be different from the
    # destination
    if [ "x$attrtype_src" = x ] || [ "$attrname_src" = "$attrname_dst" ]; then
	return 1
    fi
    if [ $mode = "remove" ]; then
	# Back up the source attribute to be removed
	attrname_bak=$attrname_src
	attrtype_dst=$attrtype_src
    else
	attrname_bak=$attrname_dst
	attrtype_dst=$(corpus_get_attr_type_full $corpus $attrname_dst)
	# If the destination attribute already exists, it needs to
	# have the same type as the source.
	if [ "x$attrtype_dst" != x ] && [ "$attrtype_src" != "$attrtype_dst" ]
	then
	    return 1
	fi
	# If the destination attribute does not exist, and if the
	# source attribute is structural with annotations, the
	# destination name must contain an underscore, or if the
	# source is bare structure, the destination name must not
	# contain underscore.
	if [ "x$attrtype_dst" = x ]; then
	    if { [ "$attrtype_src" = "s_" ] &&
		     ! in_str "_" "$attrname_dst"; } ||
		   { [ "$attrtype_src" = "s" ] &&
			 in_str "_" "$attrname_dst"; }
	    then
		return 1
	    fi
	fi
	# If the source attribute is structural with annotations, the
	# bare structure of the destination needs to be the same
	if [ "$attrtype_src" = "s_" ] &&
	       [ "${attrname_src%%_*}" != "${attrname_dst%%_*}" ]
	then
	    return 1
	fi
    fi
    if [ "${comment_extra#\!}" != "$comment_extra" ]; then
        comment=${comment_extra#\!}
        comment_extra=
    fi
    if [ "$comment" = "__DEFAULT" ]; then
	case $attrtype_src in
	    p* )
		attrtype_word=positional
		;;
	    s* )
		attrtype_word=structural
		;;
	    a* )
		attrtype_word=alignment
		;;
	esac
	comment="$comment_verb $attrtype_word attribute $attrname_src"
	if [ "x$attr_comment" != x ]; then
	    comment="$(date "+%Y-%m-%d"): $comment"
	fi
	if [ $mode != "remove" ]; then
	    comment="$comment to $attrname_dst"
	    if [ "$attrtype_dst" = "$attrtype_src" ]
	    then
		if [ "x$baksuff" != x ]; then
		    comment="$comment; existing $attrname_dst data backed up with suffix $baksuff"
		else
		    comment="$comment, overwriting existing $attrname_dst data"
		fi
	    fi
	elif [ "x$baksuff" != x ]; then
	    comment="$comment; data backed up with suffix $baksuff"
	fi
    fi
    if [ "x$comment_extra" != x ]; then
        comment="$comment: $comment_extra"
    fi
    if [ "x$baksuff" != x ]; then
	cp -p "$cwb_regdir/$corpus" "$cwb_regdir/$corpus$baksuff"
    fi
    # Add comment to the changelog section (default)
    if [ "x$attr_comment" = x ] && [ "x$comment" != x ]; then
	cwb_registry_add_change_comment $corpus "$comment"
    fi
    # For removal, an attribute comment needs to be added before
    # removing the information.
    if [ $mode = "remove" ] && [ "x$attr_comment" != x ] &&
	   [ "x$comment" != x ]
    then
	# Add a blank line after the comment, before the structure
	# block to be removed, to separate it from the structure block
	# after removal, as the trailing blank line of a structure
	# block is also removed.
	cwb_registry_add_attr_comment \
	    --blank=after $corpus $attrname_src "$comment" $attrtype_src
    fi
    cwb_registry_${mode}_attr $corpus $attrname_src $attrname_dst $attrtype_src
    (
	cd "$corpus_root/data/$corpus"
	# This should be safe as data file names cannot contain
	# spaces
	fnames=$(echo $attrname_src.*)
	if [ $attrtype_src = "s" ]; then
	    fnames="$fnames $(echo ${attrname_src}_*.*)"
	fi
	for fname in $fnames; do
	    fname_dst=$attrname_bak${fname#$attrname_src}
	    # Do not back up backup files
	    if [ "x$baksuff" != x ] && [ -e $fname_dst ] &&
		   [ ${fname_dst%.bak*} = $fname_dst ]
	    then
		cp -p $fname_dst $fname_dst$baksuff
	    fi
	    if [ $mode = "remove" ]; then
		fname_dst=
	    fi
	    $cmd $fname $fname_dst
	done
    )
    if [ $mode != "remove" ] && [ "x$attr_comment" != x ] &&
	   [ "x$comment" != x ]
    then
	cwb_registry_add_attr_comment \
	    $corpus $attrname_dst "$comment" $attrtype_src
    fi
}

# corpus_rename_attr [options] corpus attrname_src attrname_dst
#
# Rename attribute attrname_src as attrname_dst in corpus: both data
# files and information in the registry file.
#
# Options:
# --backup-suffix SUFFIX: Use SUFFIX instead of .bak-YYYYMMDDhhmmss as
#     the suffix for the backups of the registry file and possible
#     existing target data files; use "" not to make backups.
# --comment COMMENT: Append comment COMMENT to the standard comment to
#     be added to the registry file. If COMMENT begins with an
#     exclamation mark, omit the standard comment and add only COMMENT
#     (with the leading exclamation mark removed). If COMMENT is
#     empty, omit the comment altogether.
# --omit-comment: Omit the comment (an alias of '--comment ""').
# --attribute-comment: Add comment immediately after the attribute
#     declaration, instead of to the changelog section at the end of
#     the registry file.
corpus_rename_attr () {
    _corpus_manage_attr rename "$@"
}

# corpus_copy_attr [options] corpus attrname_src attrname_dst
#
# Copy attribute attrname_src to attrname_dst in corpus: both data
# files and information in the registry file.
#
# Options:
# --backup-suffix SUFFIX: Use SUFFIX instead of .bak-YYYYMMDDhhmmss as
#     the suffix for the backups of the registry file and possible
#     existing target data files; use "" not to make backups.
# --comment COMMENT: Append comment COMMENT to the standard comment to
#     be added to the registry file. If COMMENT begins with an
#     exclamation mark, omit the standard comment and add only COMMENT
#     (with the leading exclamation mark removed). If COMMENT is
#     empty, omit the comment altogether.
# --omit-comment: Omit the comment (an alias of '--comment ""').
# --attribute-comment: Add comment immediately after the attribute
#     declaration, instead of to the changelog section at the end of
#     the registry file.
corpus_copy_attr () {
    _corpus_manage_attr copy "$@"
}

# corpus_alias_attr [options] corpus attrname_src attrname_dst
#
# Create alias attrname_dst for attribute attrname_src in corpus:
# information in the registry file is copied and data files are
# symlinked.
#
# Options:
# --backup-suffix SUFFIX: Use SUFFIX instead of .bak-YYYYMMDDhhmmss as
#     the suffix for the backups of the registry file and possible
#     existing target data files; use "" not to make backups.
# --comment COMMENT: Append comment COMMENT to the standard comment to
#     be added to the registry file. If COMMENT begins with an
#     exclamation mark, omit the standard comment and add only COMMENT
#     (with the leading exclamation mark removed). If COMMENT is
#     empty, omit the comment altogether.
# --omit-comment: Omit the comment (an alias of '--comment ""').
# --attribute-comment: Add comment immediately after the attribute
#     declaration, instead of to the changelog section at the end of
#     the registry file.
corpus_alias_attr () {
    _corpus_manage_attr alias "$@"
}

# corpus_remove_attr [options] corpus attrname
#
# Remove attribute attrname in corpus: both data files and information
# in the registry file.
#
# Options:
# --backup-suffix SUFFIX: Use SUFFIX instead of .bak-YYYYMMDDhhmmss as
#     the suffix for the backups of the registry file and data files;
#     use "" not to make backups.
# --comment COMMENT: Append comment COMMENT to the standard comment to
#     be added to the registry file. If COMMENT begins with an
#     exclamation mark, omit the standard comment and add only COMMENT
#     (with the leading exclamation mark removed). If COMMENT is
#     empty, omit the comment altogether.
# --omit-comment: Omit the comment (an alias of '--comment ""').
# --attribute-comment: Add comment immediately after the attribute
#     declaration, instead of to the changelog section at the end of
#     the registry file.
#
# Note that this function takes only for a single attribute name as an
# argument, unlike corpus_remove_attrs further above.
corpus_remove_attr () {
    _corpus_manage_attr remove "$@"
}


# _cwb_registry_manage_attr corpus attrname_src attrname_dst attrtype
#                           nonstruct_eval struct_bare_eval
#                           struct_annot_eval
#
# This helper function contains the common code for renaming, copying
# and removing an attribute in the registry file.
#
# Filter the registry file of corpus through transformation code that
# is evaluated by the shell. The transformation code may for example
# rename, copy or remove the source attribute attrname_src (to
# destination attrname_dst). attrtype is the type of the attribute; if
# empty, it is found out. The original registry file is saved with the
# suffix .old.
#
# nonstruct_eval is evaluated for positional and alignment attributes,
# struct_bare_eval for structures without annotations and
# struct_annot_eval for structures with annotations. The evaluated
# code may refer to $attrname_src and $attrname_dst, struct_annot_eval
# also to $struct (the base name of the structure without annotations)
# and $attrname_src0 and $attrname_dst0 (the annotation name without
# the base name).
#
# If the destination attribute name is non-empty and different from
# the source, the destination attribute is removed if their types are
# the same; otherwise, the function exits with an error.
#
# TODO: Should we check that if the source and target attributes are
# structures with annotations, their bare structure is the same?
_cwb_registry_manage_attr () {
    local corpus attrname_src attrname_dst attrtype attrtype_dst \
	  struct_annot_eval struct_bare_eval nonstruct_eval \
	  regfile struct attrname0_src attrname0_dst
    corpus=$1
    attrname_src=$2
    attrname_dst=$3
    if [ "x$4" != x ]; then
	attrtype=$4
    else
	attrtype=$(corpus_get_attr_type_full $corpus $attrname_src)
    fi
    nonstruct_eval=$5
    struct_bare_eval=$6
    struct_annot_eval=$7
    regfile="$cwb_regdir/$corpus"
    # Check for possibly existing destination attribute
    if [ "$attrname_dst" != "$attrname_src" ] && [ "x$attrname_dst" != x ]; then
	attrtype_dst=$(corpus_get_attr_type_full $corpus $attrname_dst)
	if [ "x$attrtype_dst" != x ]; then
	    if [ "$attrtype_dst" = "$attrtype" ]; then
		cwb_registry_remove_attr $corpus $attrname_dst $attrtype
	    else
		error "Destination attribute \"$attrname_dst\" exists and has different type from source attribute \"$attrname_src\""
	    fi
	fi
    fi
    cp -p "$regfile" "$regfile.old" ||
	error "Could not copy $regfile to $regfile.old"
    if [ "$attrtype" = "s" ]; then
	eval "$struct_bare_eval" < "$regfile.old" > "$regfile"
    elif [ "$attrtype" = "s_" ]; then
	struct=${attrname_src%%_*}
	attrname0_src=${attrname_src#*_}
	attrname0_dst=${attrname_dst#*_}
	eval "$struct_annot_eval" < "$regfile.old" > "$regfile"
    else
	eval "$nonstruct_eval" < "$regfile.old" > "$regfile"
    fi
    ensure_perms "$regfile" "$regfile.old"
}

# _cwb_registry_manage_attr_awk corpus attrname_src attrname_dst attrtype
#                               attrdef_awk struct_comment_bare_awk
#                               struct_comment_annot_awk
#                               [struct_extra_line_awk]
#
# A helper function calling _cwb_registry_manage_attr with Awk code to
# be evaluated. Arguments corpus, attrname_src, attrname_dst and
# attrtype are passed as they are.
#
# The *_awk arguments contain Awk statements that are inserted within
# Awk actions (curly braces) in the code to be evaluated, for
# different types of lines:
# - attrdef_awk: attribute definition lines (ATTRIBUTE, STRUCTURE or
#     ALIGNED)
# - struct_comment_bare_awk: the structure comment line if
#     attrname_src is the bare (unannotated) structure
# - struct_comment_annot_awk: the structure comment line if
#     attrname_src is an annotated structure
# - struct_extra_line_awk: for additional comments interleaved with
#     the structure attribute definitions as well as the blank line
#     following the structure attribute definition block
#
# The Awk statements may refer to the shell variables $attrname_src
# and $attrname_dst, struct_comment_annot_awk also to also to $struct
# (the base name of the structure without annotations) and
# $attrname_src0 and $attrname_dst0 (the annotation name without the
# base name). As the code will be evaled, " and $ for the Awk code
# need to be protected with a backslash, unlike the $ in the shell
# variables.
#
# Lines are printed by default, so use "next" in the Awk statements to
# suppress printing.
#
# Note that the functions assumes that the structural attributes with
# annotations for the same structure are assumed to be preceded by a
# comment line of the form
#   # <struct attr1=".." attr2=".."> ... </struct>
# and followed # by a blank line, as generated by cwb-encode.
_cwb_registry_manage_attr_awk () {
    local corpus attrname_src attrname_dst attrtype \
	  attrdef_awk struct_comment_bare_awk struct_comment_annot_awk \
	  struct_extra_line_awk
    corpus=$1
    attrname_src=$2
    attrname_dst=$3
    attrtype=$4
    attrdef_awk=$5
    struct_comment_bare_awk=$6
    struct_comment_annot_awk=$7
    struct_extra_line_awk=$8
    _cwb_registry_manage_attr \
	$1 $2 $3 "$4" \
	'awk "/^(ATTRIBUTE|ALIGNED) $attrname_src\$/ {
	          '"$attrdef_awk"'
              }
              { print }
             "' \
	'awk "# Comment beginning the attribute definitions for a structure
	      /^# <$attrname_src[ >]/ {
                  struct = 1;
                  '"$struct_comment_bare_awk"'
              }
	      /^#(\$|[^ ]| [^<])/ && struct {
	          '"$struct_extra_line_awk"'
	      }
              # Treat an empty line as ending the attribute definitions
	      # for a structure.
              /^ *\$/ && struct {
	          struct = 0;
		  '"$struct_extra_line_awk"'
              }
              /^STRUCTURE $attrname_src([ _]|\$)/ {
	          '"$attrdef_awk"'
	      }
	      { print }
	     "' \
	'awk "/^# <$struct / {
	          '"$struct_comment_annot_awk"'
	      }
              /^STRUCTURE $attrname_src( |\$)/ {
	          '"$attrdef_awk"'
	      }
	      { print }
             "'
}


# cwb_registry_remove_attr corpus attrname [attrtype]
#
# Remove attribute attrname of type attrypte from the registry file of
# corpus. If attrtype is omitted, it is found out.
cwb_registry_remove_attr () {
    _cwb_registry_manage_attr_awk \
	$1 $2 $2 "$3" \
	'next' \
	'next' \
	'sub(/ $attrname0_src=\"\.\.\"/, \"\")' \
	'next'
}

# cwb_registry_rename_attr corpus attrname_src attrname_dst [attrtype]
#
# Rename attribute attrname_src (of type attrtype) as attrname_dst in
# the registry file of corpus. If attrtype is omitted, it is found
# out.
cwb_registry_rename_attr () {
    _cwb_registry_manage_attr_awk \
	$1 $2 $3 "$4" \
	'sub(/$attrname_src/, \"$attrname_dst\")' \
	'sub(/<$attrname_src/, \"<$attrname_dst\");
         sub(/<\/$attrname_src/, \"</$attrname_dst\")' \
	'sub(/ $attrname0_src=/, \" $attrname0_dst=\")'
}

# cwb_registry_copy_attr corpus attrname_src attrname_dst [attrtype]
#
# Copy attribute attrname_src (of type attrtype) to attrname_dst in
# the registry file of corpus. If attrtype is omitted, it is found
# out.
cwb_registry_copy_attr () {
    # This would be complicated if not impossible to implement using
    # _cwb_registry_manage_awk.
    _cwb_registry_manage_attr \
	$1 $2 $3 "$4" \
	'awk "/^(ATTRIBUTE|ALIGNED) $attrname_src\$/ {
	          print
		  print gensub(/$attrname_src/, \"$attrname_dst\", 1)
		  next
              }
              { print }
             "' \
	'awk "/^# <$attrname_src[ >]/ {
                  struct = 1
    		  copy = gensub(/<$attrname_src/, \"<$attrname_dst\", 1)
    		  copy = gensub(/<\/$attrname_src/, \"</$attrname_dst\", 1, \\
                                copy)
              }
	      /^#(\$|[^ ]| [^<])/ && struct {
	          copy = copy \"\n\" \$0
	      }
              # Treat an empty line as ending the attribute definitions
	      # for a structure.
              /^ *\$/ && struct {
	          struct = 0
		  print
		  print copy
		  # Current empty line is printed again below as the
		  # last line of the copy
              }
              /^STRUCTURE $attrname_src([ _]|\$)/ {
    		  copy = copy \"\n\" gensub(/$attrname_src/, \"$attrname_dst\", 1)
	      }
	      { print }
	     "' \
	'awk "/^# <$struct / {
	          sub(/ $attrname0_src=\"\.\.\"/, \"& $attrname0_dst=\\\"..\\\"\")
	      }
              /^STRUCTURE $attrname_src( |\$)/ {
	          print
		  print gensub(/$attrname_src/, \"$attrname_dst\", 1)
		  next
	      }
	      { print }
             "'
}

# cwb_registry_comment_out_attr corpus attrname [attrtype]
#
# Comment out attribute attrname (of type attrtype) in the registry
# file of corpus. If attrtype is omitted, it is found out.
cwb_registry_comment_out_attr () {
    _cwb_registry_manage_attr_awk \
	$1 $2 $2 "$3" \
	'sub(/^/, \"# \")' \
	'sub(/^/, \"# \")' \
	'sub(/ $attrname0_src=/, \" #$attrname0_src=\")' \
	'if (/[^ ]/ && ! /^# # <$attrname_src/) { sub(/^/, \"# \") }'
}

# cwb_registry_add_attr_comment [--blank=before|after|before+after]
#                               corpus attrname comment [attrtype]
#
# Add a comment before the attribute attrname (of type attrtype) in
# the registry file of corpus. For bare (unannotated) structural
# attributes, the comment is added before the leading comment line
# containing <struct attr1=".."> ... If attrtype is omitted, it is
# found out. comment may contain multiple lines; each line is prefixed
# with "# ". If --blank is specified, a blank line is added before,
# after, or before and after the comment, according to its argument.
cwb_registry_add_attr_comment () {
    local comment blank print_stmt
    blank=
    if [ "${1#--blank=}" != "$1" ]; then
	blank=${1#--blank=}
	shift
    fi
    # Convert newlines to "\\n" for Awk code to be evaled
    comment="$(safe_echo "$3" | sed -e 's/^/# /; s/$/\\\\n/' | tr -d '\n')"
    print_stmt='printf \"%s\", \"'"$comment"'\"'
    if in_str "before" "$blank"; then
	print_stmt='print \"\"; '"$print_stmt"
    fi
    if in_str "after" "$blank"; then
	print_stmt="$print_stmt"'; print \"\"'
    fi
    _cwb_registry_manage_attr_awk \
	$1 $2 $2 "$4" \
	'# struct is an implementation detail of
	 #_cwb_registry_manage_attr_awk but that is needed to not add
	 # comments to each annotated attribute of a bare structure.
	 if (! struct) { '"$print_stmt"' }' \
	"$print_stmt" \
	'' \
	''
}

# cwb_registry_add_change_comment corpus comment
#
# Add comment as a changelog entry at the end of a registry file of
# corpus, after the heading "## Changelog". The entry contains the
# date (YYYY-MM-DD), followed by a colon and the comment. If the
# changelog heading is absent, it is added. The new entry is added as
# the topmost one after the changelog heading (most recent first).
#
# If comment contains multiple lines, each new line is preceded by a
# "#", followed by spaces to align it with the first line of the
# comment text (following the date).
cwb_registry_add_change_comment () {
    local comment regfile
    corpus=$1
    comment=$2
    # Convert newlines to \n followed by # and indentation for Awk
    comment="$(date "+%Y-%m-%d"): $(printf "%s" "$comment" |
    		    		    tr '\n' '\a' |
				    sed -e 's/\a/\\n#             /g')"
    regfile="$cwb_regdir/$corpus"
    cp -p "$regfile" "$regfile.old" ||
	error "Could not copy $regfile to $regfile.old"
    awk '
        function add_comment() {
	    print "# '"$comment"'"
        }
	insert_comment { add_comment(); insert_comment = 0 }
	log_heading_seen && /^##/ { insert_comment = 1 }
        /^## Changelog/ { log_heading_seen = 1 }
	{ print }
	END {
	    if (! log_heading_seen) {
	        print "\n\n##"
		print "## Changelog"
		print "##"
	        add_comment()
	    }
	}
    ' < "$regfile.old" > "$regfile"
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

# corpus_get_attr_type corpus attrname
#
# Output the type of attribute attrname in corpus: p (positional), s
# (structural) or a (alignment).
corpus_get_attr_type () {
    nth_arg 1 $(corpus_list_attrs --show-type $1 '*' $2)
}

# corpus_get_attr_type_full corpus attrname
#
# Output the type of attribute like corpus_get_attr_type, but with
# "s_" for a structural attribute with annotations (such as
# sentence_id) and "s" for a bare structural attribute (such as
# sentence).
corpus_get_attr_type_full () {
    local attrtype
    attrtype=$(corpus_get_attr_type "$@")
    if [ "$attrtype" = "s" ] && in_str "_" "$2"; then
	attrtype=s_
    fi
    echo "$attrtype"
}

# struct_attr_get_struct attrname
#
# Output the bare structure for a structural attribute attrname with
# annotations, such as "sentence" for "sentence_id".
struct_attr_get_struct () {
    echo "${1%%_*}"
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
            # If the attribute has no values which do not begin or end
            # in a vertical bar or are not lone vertical bars, assume
            # that it is feature-set-valued
	    result=$(
		$cwb_bindir/cwb-lexdecode -P $attrname -p '[^|].*[^|]|[^|]' \
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
	    # Structure without annotated values cannot be
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


# corpus_get_posattr_values corpus attr [pattern]
#
# Output the values of the positional attribute attr in corpus,
# matching the regular expression pattern if specified. (pattern is an
# extended regular expression recognized by cwb-lexdecode.) The output
# contains one value per line.
corpus_get_posattr_values () {
    local corpus attr pattern_opt
    corpus=$1
    attr=$2
    pattern_opt=
    if [ "x$3" != x ]; then
        pattern_opt="-p $3"
    fi
    $cwb_bindir/cwb-lexdecode -P $attr $pattern_opt $corpus
}

# corpus_posattr_contains_values corpus attr pattern
#
# Return true if the positional attribute attr of corpus contains
# values matching the regular expression pattern.
corpus_posattr_contains_values () {
    [ x"$(corpus_get_posattr_values "$@")" != x ]
}


# corpus_exists corpus
#
# Return true if corpus exists (cwb-describe-corpus returns true).
corpus_exists () {
    $cwb_bindir/cwb-describe-corpus $1 > /dev/null 2> /dev/null
}

# corpus_id_is_valid corpus
#
# Return true if corpus is a valid CWB corpus id: contains only ASCII
# letters and digits, underscores and hyphens, and begins with an
# ASCII letter or an underscore.
corpus_id_is_valid () {
    local corpus
    corpus=$1
    test "$corpus" = "${corpus#*[!a-zA-Z0-9_-]}" &&
	test "$corpus" = "${corpus#[0-9-]}"
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

# The directory for CWB Perl utility scripts
cwb_perl_bindir=${CWB_PERL_BINDIR:-$(
                      find_existing_dir -e cwb-make $default_cwb_bindirs)}

# Append CWB Perl library path to PERL5LIB so that the CWB Perl
# scripts can be used even if the library is not on a standard path.
# Assume that the library dir contains CWB.pm.
cwb_perl_libdir=${CWB_PERL_LIBDIR:-$(
                      find_dir_with_file CWB.pm ${cwb_perl_bindir%/bin})}
if [ "$cwb_perl_libdir" != "" ]; then
    if [ "$PERL5LIB" != "" ]; then
        PERL5LIB=$PERL5LIB:$cwb_perl_libdir
    else
        PERL5LIB=$cwb_perl_libdir
    fi
    export PERL5LIB
fi
