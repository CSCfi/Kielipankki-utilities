#! /usr/bin/perl -w

use strict;
use warnings;

my $prevname = "";
my $subcorpname = "";
my $subcorp_sent_nr = 1;
my $sent_id = 1;

while (my $line = <>)
{
    if ($ARGV ne $prevname)
    {
	$subcorpname = $ARGV;
	$prevname = $ARGV;
	$subcorpname =~ s/_tab\.txt//;
	$subcorpname =~ s/^.*\///;
	if ($subcorp_sent_nr > 1)
	{
	    print "</sentence>\n</subcorpus>\n";
	}
	$subcorp_sent_nr = 1;
    }
    chomp ($line);
    if ($line !~ /^\#/ && $line !~ /^\s*$/)
    {
	my @fields = split (/\t/, $line);
	if ($#fields < 9)
	{
	    next;
	}
	if ($fields[0] eq 1)
	{
	    if ($subcorp_sent_nr == 1)
	    {
		print "<subcorpus name=\"$subcorpname\">\n";
	    }
	    else
	    {
		print "</sentence>\n";
	    }
	    print "<sentence id=\"$sent_id\">\n";
	    $sent_id++;
	    $subcorp_sent_nr++;
	}		
	print join ("\t", @fields[1, 2, 3, 4, 6, 7]) . "\n";
    }
}

print "</sentence>\n</subcorpus>\n";
