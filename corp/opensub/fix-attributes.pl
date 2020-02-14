#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

my $genre="";
my $lang_orig="";
my $country="";

while (<STDIN>)
{

    if (/^<\!/)
    {
	# <!-- #vrt positional-attributes: word ref lemma lemmacomp pos msd dephead deprel lemma_ud1 pos_ud1 msd_ud1 dephead_ud1 deprel_ud1 lex/ -->
	s/lemmacomp //;
	s/lex\/ //;
    }
    elsif (/^<text /)
    {
	# harmonize attribute values: "Nan", "N/A" and "None" and empty value
	# should have the same representation in the VRT file
	s/="(None|N\/A|Nan|NaN)"/="_"/g;

	# extract genre, lang_orig and country and represent them as sets
	# (i.e. replace "," with "|")
	if (/genre="([^"]+)"/)
	{
	    $genre = $1;
	    $genre =~ s/,/|/g;
	    $genre =~ s/ +//g;
	}
	if (/lang_orig="([^"]+)"/)
	{
	    $lang_orig = $1;
	    $lang_orig =~ s/,/|/g;
	    $lang_orig =~ s/ +//g;
	}
	if (/country="([^"]+)"/)
	{
	    $country = $1;
	    $country =~ s/,/|/g;
	    $country =~ s/ +//g;
	}

	# append "_original" to attributes genre, lang_orig and country
	s/genre="/genre_original="/;
	s/lang_orig="/lang_orig_original="/;
	s/country="/country_original="/;

	# and replace genre, lang_orig and country with the set-valued versions
	s/>/ genre="|$genre|" lang_orig="|$lang_orig|" country="|$country|">/;
    }
    else
    {
	# get rid of lemmacomp (4th field) and lex/ (last field)
	s/^([^\t]+\t[^\t]+\t[^\t]+\t)[^\t]+\t/$1/;
	s/\t[^\t\n]+$//;
    }
    print;
}
