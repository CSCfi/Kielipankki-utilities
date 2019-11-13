#!/bin/perl
#use encoding "utf8";

#--------------------------------------------------
# Cleaning metadata for Aikakauslehtikorpus
#--------------------------------------------------
#
#



my $rivi;


while (<>){
    $rivi = $_;

    #remove stylesheet and dtd info


    $rivi =~ s/<\?xml-stylesheet.*?\?>//g;

    $rivi =~ s/<\!DOCTYPE.*?>//g;

    $rivi =~ s/<text>//g;

    $rivi =~ s/<\/text>//g;

    $rivi =~ s/<gap (.*?)\/>/ /g;


    #adapt path to metadata file
    #for ydin
    $rivi =~ s/\/korpus2\/aikakaus\/(meta\/ydin\/ha\/(ha-1935-01))(.[^\/]*?\.xml)/..\/..\/..\/$1\/$2$3/g;

    $rivi =~ s/\/korpus2\/aikakaus\/(meta\/ydin\/la\/(la-1935))(.[^\/]*?\.xml)/..\/..\/..\/$1\/$2$3/g;

    $rivi =~ s/\/korpus2\/aikakaus\/(meta\/ydin\/su\/(su-1935))(.[^\/]*?\.xml)/..\/..\/..\/$1\/$2$3/g;


    #for perus
    $rivi =~ s/\/korpus2\/aikakaus\/(meta\/(.*?)\/(.[^\/]*?\.xml))/..\/..\/..\/$1/g;


    print $rivi;

}
