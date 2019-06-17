#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

while (<>)
{
    if (/^<text url="/)
    {
	s/&/&amp;/g;
    }
    print;
}
