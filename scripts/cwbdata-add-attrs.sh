#! /bin/sh
# -*- coding: utf-8 -*-


# TODO:
# - Allow updating existing (positional) attributes (input-attrs in
#   new-attrs) only if --force.
# - Allow argument substitution in the generator: {corpid}, {infile}.
# - Allow passing options to korp-make.


progname=$(basename $0)
progdir=$(dirname $0)

usage_header="Usage: $progname [options] corpus ...

Add (encode) new attributes to the CWB data of corpora, generated by a script
from existing attribute values. The script is specified with the option
--generator.

The corpus names (identifiers) may contain shell wildcards."

optspecs='
input-attrs|input-attributes|input-positional-attributes=ATTRS
    The existing positional attributes to be passed to the generator
    script in VRT format; the attribute names in ATTRS are separated
    by spaces.
input-struct-attrs|input-structural-attributes=ATTRS
    The existing structural attributes to be passed to the generator
    script in VRT format. ATTRS is a space-separated list of attribute
    names of the form STRUCT_ATTR.
new-attrs|new-attributes=ATTRS
    The new positional attributes to be added, in the order that they
    are generated by the generator script. The attribute names in
    ATTRS are separated by spaces; a trailing slash in an attribute
    name indicates that it is a feature set attribute. The strucutral
    attributes generated by the generator are automatically added (or
    updated) to the corpus.
generator=CODE
    CODE is the Bourne shell code for generating the new attributes.
    CODE is passed the values of input attributes in VRT format in
    standard input, and it should output the new attributes in the
    standard output. Typically CODE consists of a call of a script,
    with possible arguments. CODE is evaluated, so that the arguments
    may contain spaces if they are quoted appropriately. CODE may also
    contain a shell pipeline.
c|corpus-root=DIR "$corpus_root" { set_corpus_root "$1" }
    Use DIR as the root directory of corpus files.
v|verbose
    Output some progress information.
'

config_file_optname=config-file


. $progdir/korp-lib.sh


cwbdata2vrt=$progdir/cwbdata2vrt-simple.sh
korp_make=$progdir/korp-make


# Process options
eval "$optinfo_opt_handler"


if [ "x$1" = x ]; then
    error "No corpus name specified"
fi
if [ "x$input_attrs" = x ]; then
    error "Please specify --input-attributes"
fi
if [ "x$new_attrs" = x ]; then
    error "Please specify --new-attributes"
fi
quiet_opt=
if [ "x$verbose" = x ]; then
    quiet_opt=--quiet
fi

corpora=$(list_corpora "$@")


corpus_add_attrs () {
    local corp newattrs_vrt corp_token_cnt newattrs_token_cnt
    corp=$1
    newattrs_vrt=$tmp_prefix.newattrs.vrt
    echo_verb "Extracting input and generating new attributes"
    $cwbdata2vrt --output-file "-" --omit-attribute-comment \
	--pos-attrs "$input_attrs" --struct-attrs "$input_struct_attrs" $corp |
    eval "$generator" > "$newattrs_vrt"
    corp_token_cnt=$(get_corpus_token_count $corp)
    newattrs_token_cnt=$(vrt_get_token_count "$newattrs_vrt")
    if [ "$corp_token_cnt" != "$newattrs_token_cnt" ]; then
	warn "Corpus $corp: Attributes not added because token count for new attributes ($newattrs_token_cnt) differs from corpus token count ($corp_token_cnt)"
	return
    fi
    echo_verb "Encoding new attributes"
    $korp_make --augment-data --input-attrs "$new_attrs" --no-word-attr \
	--no-package $quiet_opt $corp "$newattrs_vrt"
}


for corp in $corpora; do
    echo_verb "Adding attributes to corpus $corp"
    corpus_add_attrs $corp
done
