#!/bin/perl
#use encoding "utf8";

#--------------------------------------------------
# Cleaning metadata for Loennrot
#--------------------------------------------------
#
#



my $rivi;


while (<>){
    $rivi = $_;

    #add filename to letters


    $rivi =~ s/Filename\: \.\.\/orig_20191002\/((.*?)\.xml)/<letter name=\"$1\">/g;
    #$rivi =~ s/Filename\: (.*?)\.xml\n/<filename>$1<\/filename>/g;

    $rivi =~ s/<letter>//g;



    print $rivi;

}
