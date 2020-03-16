#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

foreach my $line ( <STDIN> ) {

    unless ( $line =~ /^</ )
    {
	my @fields;
	
	if ( $ARGV[0] eq "--gloss" ) # (4th field)
	{
	    @fields = $line =~ /([^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+)(.*)/;
	}
	else # pos (5th field)
	{
	    @fields = $line =~ /([^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+)(.*)/;
	}

	my @values = split('\xA0', $fields[1]);
       
	print $fields[0];
	print $fields[1];
	print $fields[2];
	print "\t";

	my $field = "";
	foreach (@values)
	{
	    unless ($_ =~ /^\-/ or $_ =~ /\-$/)
	    {
		if ( $ARGV[0] eq "--gloss" )
		{
		    # gloss values are separated by nbsps
		    unless ($field eq "")
		    {
			$field = "$field\xA0";
		    }
		    $_ =~ s/\:.*//;
		}
		else
		{
		    # POS values are separated (and surrounded) by vertical lines
		    $field = "$field|";
		}
		$field = "$field$_";
	    }
	}
	if ( $ARGV[0] eq "--pos" )
	{
	    unless ( $field eq "" )
	    {
		$field = "$field|";
	    }
	    else
	    {
		$field = "|?|"; # no simple POS extracted
	    }
	}
	else
	{
	    if ( $field eq "" )
	    {
		$field = "*"; # no simple gloss extracted
	    }
	}

	print $field;
	print "\n";
    }
    else
    {
	print $line;
    }
}
