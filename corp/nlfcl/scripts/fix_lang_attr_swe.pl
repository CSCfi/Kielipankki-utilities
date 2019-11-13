#!/bin/perl
#use encoding "utf8";

#--------------------------------------------------
# Cleaning metadata in ClassicalLibrary
#--------------------------------------------------
#
#

my $rivi;

while (<>){
    $rivi = $_;

    #remove Document element tag
    $rivi =~ s/<KlK>//g;

    $rivi =~ s/<\/KlK>//g;



    #uniform language attributes
    $rivi =~ s/lang=\"\"/lang=\"swe\"/g;

    $rivi =~ s/lang=\"other\"/lang=\"swe\"/g;

    $rivi =~ s/lang=\"fin\"/lang=\"swe\"/g;


    #fix apostrophe in title of book nr 137 and others
    $rivi =~ s/(title=\"De)\'( va)\'( sjutton)/$1\&\#39\;$2\&\#39\;$3/g;

    $rivi =~ s/(title=\"(.*?))\'/$1\&\#39\;/g;


    print $rivi;

}
