#!/usr/bin/perl

# Postprocess result from fsm2vrt.py to handle dates.
# Read from standard input and write to standard output.

use strict;
use warnings;
use open qw(:std :utf8);

foreach my $line ( <STDIN> ) {

    if ( $line =~ /^</ )
    {
	$line =~ s/date="([0-9]{2})\/(Jan)\/([0-9]{4})"/date="$3-01-$1"/g;
	$line =~ s/date="([0-9]{2})\/(Feb)\/([0-9]{4})"/date="$3-02-$1"/g;
	$line =~ s/date="([0-9]{2})\/(Mar)\/([0-9]{4})"/date="$3-03-$1"/g;
	$line =~ s/date="([0-9]{2})\/(Apr)\/([0-9]{4})"/date="$3-04-$1"/g;
	$line =~ s/date="([0-9]{2})\/(May)\/([0-9]{4})"/date="$3-05-$1"/g;
	$line =~ s/date="([0-9]{2})\/(Jun)\/([0-9]{4})"/date="$3-06-$1"/g;
	$line =~ s/date="([0-9]{2})\/(Jul)\/([0-9]{4})"/date="$3-07-$1"/g;
	$line =~ s/date="([0-9]{2})\/(Aug)\/([0-9]{4})"/date="$3-08-$1"/g;
	$line =~ s/date="([0-9]{2})\/(Sep)\/([0-9]{4})"/date="$3-09-$1"/g;
	$line =~ s/date="([0-9]{2})\/(Oct)\/([0-9]{4})"/date="$3-10-$1"/g;
	$line =~ s/date="([0-9]{2})\/(Nov)\/([0-9]{4})"/date="$3-11-$1"/g;
	$line =~ s/date="([0-9]{2})\/(Dec)\/([0-9]{4})"/date="$3-12-$1"/g;
    }
    print $line;
}
