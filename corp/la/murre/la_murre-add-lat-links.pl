#! /usr/bin/perl -pw
# -*- coding: utf-8 -*-

# Add LAT (Annex) links and other attributes to VRT sentence and
# paragraph elements from those elements in another VRT file.
#
# Usage: $progname [--link-params-only] lat_link_dir < input.vrt > output.vrt
#
# lat_link_dir contains the files from which the additional attributes
# are extracted. The appropriate file is chosen based on the filename
# attribute of the text element in input.vrt. The element from which
# the attributes are added is chosen based on the id attribute in
# input.vrt and pnum or snum in the extra attribute file.
#
# The script adds all attributes in the additional file except the
# pnum/snum. The following attribute names are converted: beg ->
# begin_time, dur -> duration, urlview -> annex_link. If an element
# has no corresponding element in the additional file, the script adds
# these attributes with empty values.
#
# If --link-params-only is specified, only retain the URL parameters
# part of the URLs.


sub read_linkfile
{
    my ($linkfname) = @_;
    open ($linkf, '<', $linkfname)
	or die "Cannot open $linkfname";
    %link_info = ();
    while (my $line = <$linkf>) {
	if ($line =~ /^<(?:paragraph|sentence) [ps]num="(p?\d+)" (.+)>/) {
	    my ($num, $attrs) = ($1, $2);
	    $attrs =~ s/beg=/begin_time=/;
	    $attrs =~ s/dur=/duration=/;
	    $attrs =~ s/urlview=/annex_link=/;
	    if ($link_params_only) {
		$attrs =~ s/(annex_link=").+?\?/$1/;
	    }
	    $link_info{$num} = $attrs;
	}
    }
}

BEGIN {
    $link_params_only = 0;
    if ($ARGV[0] eq '--link-params-only') {
	$link_params_only = 1;
	shift (@ARGV);
    }
    $linkfile_dir = shift (@ARGV);
}

if (/^<text /) {
    ($fname) = ($_ =~ /filename="(.+?)"/);
    read_linkfile ("$linkfile_dir/$fname.vrt");
} elsif (/^<(paragraph|sentence) /) {
    ($id) = ($_ =~ /id="(p?\d+?)"/);
    $info = (exists ($link_info{$id})
	     ? $link_info{$id}
	     : 'begin_time="" duration="" annex_link=""');
    s/>/ $info>/;
}
