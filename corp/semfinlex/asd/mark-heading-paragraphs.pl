#!/usr/bin/perl

# Mark heading paragraphs. Heading paragraphs will contain
# <saa:(Osa|Luku|Pykala)TunnusKooste> and the following
# <saa:SaadosOtsikkoKooste>, if it is present.
# Also extract title of heading paragraph and print it after
# the paragraph as <<title="TITLE">>.

use strict;
use warnings;
use open qw(:std :utf8);

my $title = "";
my $tunnuskooste = 0;
my $waiting = 0;
my $saadosotsikkokooste = 0;

my $delayed = "";

while (<>) {
    if (/^<saa:(Osa|Luku|Pykala)TunnusKooste[ >]/) { $tunnuskooste = 1; $delayed .= join('','<<paragraph type="heading">>',"\n"); }
    elsif (/^<saa:SaadosOtsikkoKooste[ >]/) { $saadosotsikkokooste = 1; }
    elsif (/^<\/saa:(Osa|Luku|Pykala)TunnusKooste/) { $tunnuskooste = 0; $waiting = 1; }
    elsif (/^<\/saa:SaadosOtsikkoKooste/) { $saadosotsikkokooste = 0; }
    elsif ($tunnuskooste eq 1 || $saadosotsikkokooste eq 1) { $title .= $_; $title =~ s/\n/ /g; }
    elsif ($waiting eq 1) { $waiting = 0; $delayed .= join('','<</paragraph>>',"\n"); $title =~ s/^ +//; $title =~ s/ +$//; $title =~ s/"/&quot;/g ;$title =~ s/'/&apos;/g; $title =~ s/<[^>]*>//g; unless ($title eq "") { $delayed = join('','<<title="',$title,'">>',"\n",$delayed); } $title = ""; }

    if ($tunnuskooste eq 1 || $saadosotsikkokooste eq 1 || $waiting eq 1) { $delayed .= $_; }
    else
    {
	# remove SaadosOtsikkoKooste as it is already inside paragraph and mark it as a sentence boundary
	if ($delayed =~ /<<paragraph type="heading">>/)
	{
	    $delayed =~ s/<saa:SaadosOtsikkoKooste>/<>/g;
	    $delayed =~ s/<\/saa:SaadosOtsikkoKooste>\n//g;
	}
	print $delayed;
	$delayed = "";
	print;
    }
}
