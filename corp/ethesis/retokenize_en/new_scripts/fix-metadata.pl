#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

foreach my $line ( <STDIN> ) {

    if ($line =~ /(datefrom|dateto|timefrom|timeto)=""/)
    {
	print STDERR "Warning: missing date information: ".$line;
    }
    
    if ($line =~ / type="([^"]*)"/)
    {
	my $type = $1;
	$line =~ s/ type="/ orig_type="/;
	my $replace = "";

	if ($type eq "Doctoral dissertation") { $replace = "ethesis_doctoral_dissertation"; }
	elsif ($type eq "Doctoral dissertation (article-based)") { $replace = "ethesis_doctoral_dissertation_article_based"; }
	elsif ($type eq "Doctoral dissertation (monograph)") { $replace = "ethesis_doctoral_dissertation_monograph"; }
	elsif ($type eq "master&apos;s thesis") { $replace = "ethesis_masters_thesis"; }
	elsif ($type eq "Master&apos;s thesis") { $replace = "ethesis_masters_thesis"; }
	elsif ($type eq "Master&apos;s Thesis") { $replace = "ethesis_masters_thesis"; }
	elsif ($type eq "Opinnäyte") { $replace = "ethesis_masters_thesis"; }
	elsif ($type eq "Pro gradu") { $replace = "ethesis_masters_thesis"; }
	elsif ($type eq "Pro gradu-tutkielma") { $replace = "ethesis_masters_thesis"; }
	elsif ($type eq "Pro gradu -työ") { $replace = "ethesis_masters_thesis"; }
	elsif ($type eq "text") { $replace = "ethesis_masters_thesis"; }
	elsif ($type eq "") { $replace = "_"; }
	else { $replace = "_"; }

	$line =~ s/ orig_type="/ type="${replace}" orig_type="/;
    }

    $line =~ s/ lang="([^"]*)"/ lang="eng"/;
    $line =~ s/=""/="_"/;
    $line =~ s/ +/ /g;
    $line =~ s/=" /="/g;
    $line =~ s/ "/"/g;
    
    print $line;

}

