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
    $rivi =~ s/lang=\"\"/lang=\"fin\"/g;

    $rivi =~ s/lang=\"other\"/lang=\"fin\"/g;


    #fix apostrophes in text attributes
    $rivi =~ s/(title=\"(.*?))\'/$1\&\#39\;/g;

    $rivi =~ s/(contributor=\"(.*?))\'/$1\&\#39\;/g;



    print $rivi;

}
