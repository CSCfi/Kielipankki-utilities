#! /usr/bin/perl -w

use strict;
use warnings;

my $prevname = "";
my $subcorpname = "";
my $sent_id = 1;

while (my $line = <>)
{
    if ($ARGV ne $prevname)
    {
	$subcorpname = $ARGV;
	$prevname = $ARGV;
	$subcorpname =~ s/_tab\.txt//;
	$subcorpname =~ s/^.*\///;
	if ($sent_id > 1)
	{
	    print "</sentence>\n</subcorpus>\n";
	}
	$sent_id = 1;
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
	    if ($sent_id == 1)
	    {
		print "<subcorpus name=\"$subcorpname\">\n";
	    }
	    else
	    {
		print "</sentence>\n";
	    }
	    print "<sentence id=\"$sent_id\">\n";
	    $sent_id++;
	}		
	print join ("\t", @fields[1, 2, 3, 4, 6, 7]) . "\n";
    }
}

print "</sentence>\n</subcorpus>\n";
