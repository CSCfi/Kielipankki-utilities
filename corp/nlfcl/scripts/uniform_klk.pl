#!/bin/perl
#use encoding "utf8";

#--------------------------------------------------
# Cleaning metadata timestamp in ClassicalLibrary
#--------------------------------------------------
#
#

my $rivi;

while (<>){
    $rivi = $_;


    $rivi =~ s/<KlK(\d.*?)>/<KlK><number>$1<\/number>/g;

    $rivi =~ s/<\/KlK\d.*?>/<\/KlK>/g;


    #remove empty page elements
    $rivi =~ s/<page .*?\/>//g;
    

    #have page elements on separate line
    $rivi =~ s/(<page .*?>)(.*?)/$1\n$2/g;


    #fix errors in orig data
    $rivi =~ s/(<title>En framtidsman\: teckning ur språkst)(idernas tidehvarf af Anders Allart<\/title>)/$1r$2/g;

    $rivi =~ s/(<number>858<\/number>)/$1<author_fix>Tavaststjerna, Frans August Theodor<\/author_fix>/g;
       
    print $rivi;

}
