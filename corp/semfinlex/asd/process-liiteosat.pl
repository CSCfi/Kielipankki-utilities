#!/usr/bin/perl

# Process <<liiteosat>>

use strict;
use warnings;
use open qw(:std :utf8);

while (<>) {
    s/<<liiteosat>>/<<part type="LIITEOSAT">/;
    s/<<\/liiteosat>>/<<\/part>>/;
    print;
}
