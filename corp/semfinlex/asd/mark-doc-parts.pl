#!/usr/bin/perl

# Mark different parts of document with << ... >> tags:
# <<identifiointiosa>>, <<saadososa>>, <<allekirjoitusosa>>
# and <<liiteosat>>.

use strict;
use warnings;
use open qw(:std :utf8);

my $identifiointiosa = "";
my $saadososa = "";
my $allekirjoitusosa = "";
my $liiteosat = "";
my $part = "";

while (<>) {
    if (/^ *$/) { next; }
    
    if (/^<asi:IdentifiointiOsa[ >]/) { $part = "identifiointiosa"; }
    elsif (/^<saa:SaadosOsa[ >]/) { $part = "saadososa"; }
    elsif (/^<asi:PaivaysKooste[ >]/ || /^<asi1:JohdantoTeksti[ >]/ || /^<asi:Allekirjoittaja[ >]/) { $part = "allekirjoitusosa"; }
    elsif (/^<asi:LiiteOsa[ >]/) { $part = "liiteosat"; }
    
    if ($part eq "identifiointiosa" ) { $identifiointiosa .= $_; }
    elsif ($part eq "saadososa") { $saadososa .= $_; }
    elsif ($part eq "allekirjoitusosa" ) { $allekirjoitusosa .= $_; }
    elsif ($part eq "liiteosat") { $liiteosat .= $_; }

    if (/^<\/asi:IdentifiointiOsa>/ || /^<\/saa:SaadosOsa>/ || /^<\/asi:PaivaysKooste>/ || /^<\/asi1:JohdantoTeksti>/ || /^<\/asi:Allekirjoittaja>/ || /^<\/asi:LiiteOsa>/) { $part = ""; }
}

my $retval = 0;
if ( $identifiointiosa eq "" ) { print "missing identifiointiosa\n"; $retval = 1; }
if ( $saadososa eq "" ) { print "missing saadososa\n"; $retval = 1; }
if ( $allekirjoitusosa eq "" ) { print "missing allekirjoitusosa\n"; $retval = 1; }

# Surround different parts of documents with << ... >> tags 
print "<<identifiointiosa>>\n";
print $identifiointiosa;
print "<</identifiointiosa>>\n";
print "<<saadososa>>\n";
print $saadososa;
print "<</saadososa>>\n";
print "<<allekirjoitusosa>>\n";
print $allekirjoitusosa;
print "<</allekirjoitusosa>>\n";

if ($liiteosat ne "")
{
    print "<<liiteosat>>\n";
    print $liiteosat;
    print "<</liiteosat>>\n"
}

exit $retval;
