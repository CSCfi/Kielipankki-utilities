#! /usr/bin/perl -w


use strict;
use warnings;
use Getopt::Long;


sub getopts
{
    my %opts = (lemgrams => 1);
    GetOptions ('lemgrams!' => \$opts{lemgrams});
    return \%opts;
}


sub make_pos
{
    my ($msd) = @_;

    my %posmap = (Coord => "CC",
		  Punct => "Pun",
		  Sub => "CS",
		  Cmpr => "CS",
 		  Cop => "V",
		  Negv => "V",
		  Intj => "Interj",
	          Pp => "Adv",
		  Pcp1 => "V",
		  Prop => "N");
    
    $msd =~ s/\s*<.*?>\s*//g;
    $msd =~ s/^\S+\s(PRON\s)/$1/;
    my ($pos) = ($msd =~ /^(\S+)/);
    $pos =~ s/^(.)(.*)$/$1\L$2\E/;
    return $posmap{$pos} // $pos;
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
    # my $subcorpname = "";
    # my $subcorp_sent_nr = 1;
    my $sent_id = 1;
    while (my $line = <>)
    {
	# if ($ARGV ne $prevname)
	# {
	#     # $subcorpname = $ARGV;
	#     # $prevname = $ARGV;
	#     # $subcorpname =~ s/_tab\.txt//;
	#     # $subcorpname =~ s/^.*\///;
	#     if ($subcorp_sent_nr > 1)
	#     {
	# 	print "</sentence>\n</subcorpus>\n";
	#     }
	#     $subcorp_sent_nr = 1;
	# }
	chomp ($line);
	if ($line =~ /^<s>/)
	{
	    print "<sentence id=\"$sent_id\">\n";
	}
	elsif ($line =~ /^<\/s>/)
	{
	    print "</sentence>\n";
	    $sent_id++;
	}
	elsif ($line !~ /^\#/ && $line !~ /^\s*$/)
	{
	    my @fields = split (/\t/, $line);
	    if ($#fields < 5)
	    {
		next;
	    }
	    # if ($fields[0] eq 1)
	    # {
	    # 	if ($subcorp_sent_nr == 1)
	    # 	{
	    # 	    print "<subcorpus name=\"$subcorpname\">\n";
	    # 	}
	    # 	else
	    # 	{
	    # 	    print "</sentence>\n";
	    # 	}
	    # 	print "<sentence id=\"$sent_id\">\n";
	    # 	$sent_id++;
	    # 	$subcorp_sent_nr++;
	    # }
	    # $fields[3] =~ s/\|.*//;
	    my ($pos) = make_pos ($fields[5]);
	    for my $field (@fields)
	    {
		$field =~ s/^\s+//;
		$field =~ s/\s+$//;
	    }
	    print join ("\t", @fields[3, 4], $pos, @fields[5, 1, 2, 6]);
	    if ($$opts_r{lemgrams})
	    {
		print "\t" . make_lemgram ($fields[4], $pos);
	    }
	    print "\n";
	}
    }
}


sub main
{
    my $opts_r = getopts ();
    process_input ($opts_r);
}


main ();
