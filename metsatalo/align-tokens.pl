#! /usr/bin/perl -w


use strict;
use warnings;


sub read_tokens
{
    my ($tok_fname) = @_;

    open (TF, '<', $tok_fname)
	or die "$0: Cannot open file: $@\n";
    my @tokens = split (/\s+/, join ('', <TF>));
    close (TF);
    return \@tokens;
}


sub process_input
{
    my ($tokens_r) = @_;

    my $token_nr = 0;
    while (my $line = <>)
    {
	if ($line =~ /^</)
	{
	    print $line;
	}
	else
	{
	    chomp ($line);
	    print "$line\t$$tokens_r[$token_nr]\n";
	    $token_nr++
	}
    }
}


sub main
{
    my $tok_fname = shift (@ARGV);
    my $tokens_r = read_tokens ($tok_fname);
    process_input ($tokens_r);
}


main ();
