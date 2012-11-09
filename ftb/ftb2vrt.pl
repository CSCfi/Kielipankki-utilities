#! /usr/bin/perl -w

use strict;
use warnings;
use Getopt::Long;


sub getopts
{
    my %opts = (lemgrams => 1,
		msd_sep => '|',
		fix_msd_tags => 1);
    GetOptions ('lemgrams!' => \$opts{lemgrams},
		'msd-separator|morpho-tag-separator=s' => \$opts{msd_sep},
		'fix-msd-tags|fix-morpho-tags!' => \$opts{fix_msd_tags});
    return \%opts;
}


sub make_lemgram
{
    my ($lemma, $pos) = @_;

    my %posmap = ("_" => "xx", # Unspecified
		  A => "jj",
		  # AN in the target is not PoS category but a feature,
		  # but we treat it as a category here.
		  Abbr => "an",
		  Adp => "pp",
		  Adv => "ab",
		  CC => "kn",
		  Con => "kn",
		  CS => "sn",
		  Interj => "in",
		  INTERJ => "in",
		  Noun => "nn",
		  N => "nn",
		  Num => "rg",
		  POST => "pp",
		  Pron => "pn",
		  Pun => "xx",
		  V => "vb");
    return "|$lemma..$posmap{$pos}.1|";
}


sub process_input
{
    my ($opts_r) = @_;

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
	    $fields[3] =~ s/\|.*//;
	    for my $field (@fields)
	    {
		$field =~ s/^\s+//;
		$field =~ s/\s+$//;
		$field =~ s/\s{2,}/ /;
	    }
	    if ($$opts_r{fix_msd_tags})
	    {
		$fields[4] =~ tr/<>/[]/;
		$fields[4] =~ s/\s+/$$opts_r{msd_sep}/g;
	    }
	    print join ("\t", @fields[1, 2, 3, 4, 6, 7]);
	    if ($$opts_r{lemgrams})
	    {
		print "\t" . make_lemgram (@fields[2, 3]);
	    }
	    print "\n";
	}
    }
    print "</sentence>\n</subcorpus>\n";
}


sub main
{
    my $opts_r = getopts ();
    process_input ($opts_r);
}


main ();
