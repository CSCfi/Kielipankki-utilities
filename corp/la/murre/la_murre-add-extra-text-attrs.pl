#! /usr/bin/perl -p

# Add extra attributes to VRT text elements based on an info file in
# TSV format.
#
# Usage: $progname info_file.tsv < input.vrt > output.vrt
#
# The first line of the info file contains the field (column) names
# that are used as attribute names. Only those attributes are added
# whose names begin with a lowercase letter. The values for each text
# element in the input are taken in from the following lines: from the
# second line for the first element, from the third line to the second
# element and so on.


BEGIN {
    $infofname = shift (@ARGV);
    open ($infofile, "<", $infofname)
	or die ("Cannot open $infofname");
    $heading = 1;
    @infoattrs = ();
    @attrnames = {};
    while ($line = <$infofile>) {
	chomp ($line);
	@fields = split (/\t/, $line);
	if ($heading) {
	    @attrnames = @fields;
	    $heading = 0;
	} else {
	    @attrs = ();
	    for ($i = 0; $i <= $#fields; $i++) {
		if ($attrnames[$i] =~ /^[a-z]/) {
		    push (@attrs, $attrnames[$i] . "=\"" . $fields[$i] . "\"");
		}
	    }
	    push (@infoattrs, join (" ", @attrs));
	}
    }
    $textnum = 0;
}

if (/^<text/) {
    s/>/ $infoattrs[$textnum]>/;
    $textnum++;
}
