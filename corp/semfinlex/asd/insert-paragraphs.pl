#!/usr/bin/perl

# Insert paragraph tags around text that would else be left
# outside paragraphs in later stages of processing.
#
# Mark <viite> as <paragraph type="VIITE">.
# Mark <saa:Pykala> on one line as <paragraph type="paragraph">.

use strict;
use warnings;
use open qw(:std :utf8);

while (<>)
{
    s/^ *<viite>(.*)<\/viite>/<paragraph type="VIITE">$1<\/paragraph>/;
    s/^ *(<saa:Pykala>)(.*)(<\/saa:Pykala>)/$1<paragraph type="paragraph">$2<\/paragraph>$3/;
    print;
}
