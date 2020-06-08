#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

foreach my $line ( <STDIN> ) {
    # - remove control characters U+0000 - U+001F (excluding TAB U+0009, LF U+000A and CR U+000D) and U+007F - U+009F,
    #   Unicode line and paragraph separators (U+2028, U+2029) and soft hyphens (U+00AD) and some other strange characters
    # - convert FIGURE SPACE (U+2007) and NARROW NO-BREAK SPACE (U+202F) (and also THIN SPACE, U+2009) and NBSP (U+00A0)
    #   as well as other spaces into ordinary spaces
    $line =~ s/[\x{0000}-\x{0008}\x{000B}\x{000C}\x{000E}-\x{001F}\x{00AD}\x{007F}-\x{009F}\x{2028}\x{2029}\x{00AD}\x{2028}\x{FEFF}\x{FFFF}\x{FFFD}]//g;
    $line =~ s/[\x{2007}\x{202F}\x{2009}\x{00A0}]/ /g;
    $line =~ s/[\x{0085}\x{1680}\x{2000}-\x{200A}\x{202F}\x{205F}\x{3000}]/ /g;
    # Replace HTML entities between 0-31 with space. They sometimes separate words.
    $line =~ s/&#[0-9];/ /g;
    $line =~ s/&#[12][0-9];/ /g;
    $line =~ s/&#3[01];/ /g;
    print $line;	
}
