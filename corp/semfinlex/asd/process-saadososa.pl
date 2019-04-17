#!/usr/bin/perl

# Process <<saadososa>>

use strict;
use warnings;
use open qw(:std :utf8);

while (<>) {
    s/<<\/?saadososa>>\n//;
    print;
}
