#!/usr/bin/perl

# Move parts of text so that they are not left outside paragraphs
# in later stages of processing.
#
# Move <johtl> inside following <saa:SaadosKappaleKooste>.

use strict;
use warnings;
use open qw(:std :utf8);

my $johtolause = "";

while (<>) 
{
    if (/^ +<johtl>/)
    {
	$johtolause = $_;
	$johtolause =~ s/<johtl>(.*)<\/johtl>/$1/;
    }
    elsif ($johtolause ne "" && /^ +<ko>/)
    {
	next;
    }
    elsif ($johtolause ne "" && /^ +<saa:SaadosKappaleKooste>/)
    {
	print;
	print $johtolause;
	$johtolause = "";
    }
    else
    {
	print;
    }
}

if ($johtolause ne "")
{
    print STDERR join('',"Error: could not insert <johtl>: \"",$johtolause,"\"\n");
    exit 1;
}
