#!/usr/bin/perl

# Remove xml tags that were originally present in the document.
# Exclude sentence boundaries (<>) and paragraphs that were inserted
# in early stages of processing as well as << ... >> tags.
# Convert << ... >> tags into ordinary < ... > tags.

use strict;
use warnings;
use open qw(:std :utf8);

while ( <> ) {
    s/^<(paragraph[^>]*)>/<<$1>>/;
    s/^<\/paragraph>/<<\/paragraph>>/;
    s/^<[^><].*//;
    s/^<</</;
    s/>>$/>/;
    #s/<\/?saadososa.*//;
    #s/<\/?liiteosa.*//;
    s/^\n$//;
    print;
}
