#! /usr/bin/perl

# Rename structural attributes (attributes of structures) in VRT
#
# Usage: vrt-rename-struct-attrs.pl STRUCT/SOURCE:TARGET ...
#
# STRUCT is the structure in which the regular expression SOURCE is
# matched on attribute names, and TARGET is the replacement value,
# which may reference to capture groups in SOURCE.
#
# NOTE: This a quick-and-dirty script primarily for use in korp-make.
#
# TODO: Rewrite as a Python script in the VRT Tools, making it more
# robust, as it now also replaces values of the form attrpattern="
# within attribute values.


%renames = ();

for $arg (@ARGV) {
    ($struct, $attr_re, $subst) = split (/[:\/]/, $arg);
    # print "$struct $attr_re $subst\n";
    if (! exists ($renames{$struct})) {
	$renames{$struct} = [];
    }
    # Make full stop match only the characters allowed in VRT
    # attribute names
    $attr_re =~ s/\./[a-z0-9_]/g;
    # It appeared to be tricky to reference to a named capture group
    # in a replacement string variable, but this seems to work.
    push (@{$renames{$struct}},
	  [" " . $attr_re . "(?<q>=[\"\x27])",
	   "\" " . $subst . "\" . \$+{q}"]);
}
@ARGV = ();

$tag_re = "^<(" . join ("|", keys (%renames)) . ") ";
# print "$tag_re\n";

while (<>) {
    if (/$tag_re/) {
	$tag = $1;
	# print "tag:$tag\n";
	for $rename (@{$renames{$tag}}) {
	    # print "$$rename[0] -> $$rename[1]\n";
	    s/$$rename[0]/$$rename[1]/gee;
	}
    }
    print;
}
