#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

while (<>) {

    if (/^<<abstract>>/)
    {
	print join('','<<section type="abstract">>',"\n");
    }
    elsif (/^<<\/abstract>>/)
    {
	print "<</section>>\n";
    }
    else
    {
	print;
    }
}
