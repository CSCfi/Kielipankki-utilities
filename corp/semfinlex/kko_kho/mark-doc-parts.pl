#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

my $description = "";
my $abstract = "";
my $content = "";
my $kirjav = "";
my $part = "";

while (<>) {
    if (/^ *$/) { next; }
    
    if (/^<dcterms:description[ >]/) { $part = "description"; }
    elsif (/^<dcterms:abstract[ >]/) { $part = "abstract"; }
    elsif (/^<finlex:content[ >]/) { $part = "content"; }
    elsif (/^<kirjav[ >]/) { $part = "kirjav"; }

    if ($part eq "description" ) { $description .= $_; }
    elsif ($part eq "abstract") { $abstract .= $_; }
    elsif ($part eq "content" ) { $content .= $_; }
    elsif ($part eq "kirjav") { $kirjav .= $_; }

    if (/^<\/dcterms:description>/ || /^<\/dcterms:abstract>/ || /^<\/finlex:content>/ || /^<\/kirjav>/) { $part = ""; }
}

# Surround different parts of documents with << ... >> tags 
unless ($description eq "")
{
    print "<<description>>\n";
    print $description;
    print "<</description>>\n";
}
unless ($abstract eq "")
{
    print "<<abstract>>\n";
    print $abstract;
    print "<</abstract>>\n";
}
unless ($content eq "")
{
    print "<<content>>\n";
    print $content;
    print "<</content>>\n";
}
unless ($kirjav eq "")
{
    print "<<kirjav>>\n";
    print $kirjav;
    print "<</kirjav>>\n";
}
