#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

while ( <> ) {
    #s/^<(paragraph[^>]*)>/<<$1>>/;
    #s/^<\/paragraph>/<<\/paragraph>>/;
    s/<\/li>/<>/; # insert sentence boundary between list items
    s/^<[^><].*//;
    s/^<</</;
    s/>>$/>/;
    #s/<\/?saadososa.*//;
    #s/<\/?liiteosa.*//;
    s/^\n$//;
    print;
}
