#!/bin/perl
#use encoding "utf8";

#--------------------------------------------------
# Cleaning metadata for Aikakauslehti
#--------------------------------------------------
#
#

my $rivi;



while (<>){
    $rivi = $_;

    #clean issue information

    #for perus
 
    $rivi =~ s/(issue=\")(.*?)(\d\d\d\d)-0(\d)\.xml(\")/$1$4\/$3$5/g;

    $rivi =~ s/(issue=\")(.*?)(\d\d\d\d)-([1-9]\d)\.xml(\")/$1$4\/$3$5/g;
    
    $rivi =~ s/(issue=\")(.*?)(\d\d\d\d)-0(\d)-0(\d)\.xml(\")/$1$4-$5\/$3$6/g;

    $rivi =~ s/(issue=\")(.*?)(\d\d\d\d)-([1-9]\d-[1-9]\d)\.xml(\")/$1$4\/$3$5/g;

    $rivi =~ s/(issue=\")(.*?)(\d\d\d\d)\.xml(\")/$1$3$4/g;


    #for ydin with page number

    $rivi =~ s/(issue=\")(.*?)(\d\d\d\d)-0(\d)-\d\d\d_man\.xml(\")/$1$4\/$3$5/g;


    $rivi =~ s/(issue=\")(.*?)(\d\d\d\d)-([1-9]\d)-\d\d\d_man\.xml(\")/$1$4\/$3$5/g;

    $rivi =~ s/(issue=\")(.*?)(\d\d\d\d)-(\d\d-\d\d)-\d\d\d_man\.xml(\")/$1$4\/$3$5/g;

    $rivi =~ s/(issue=\")(.*?)(\d\d\d\d)-\d\d\d_man\.xml(\")/$1$3$4/g;


    #clean page numbers

    $rivi =~ s/(page=\")(.*?)-00(\d)_man\.xml(\")/$1$3$4/g;

    $rivi =~ s/(page=\")(.*?)-0([1-9]\d)_man\.xml(\")/$1$3$4/g;
    
    $rivi =~ s/(page=\")(.*?)-([1-9][1-9]\d)_man\.xml(\")/$1$3$4/g;

    $rivi =~ s/(page=\")(.*?)\d\d\.xml(\")/$1$3/g;

    #clean element paragraph
    #$rivi =~ s/<paragraph (.*?)>/<paragraph>/g;

    #delete empty paragraphs, add line break after paragraph tags
    $rivi =~ s/<paragraph (.*?)\/>//g;
    
    $rivi =~ s/(<paragraph (.*?)>)/$1\n/g;

    $rivi =~ s/(.*?)(<\/paragraph>)/$1\n$2/g;

    $rivi =~ s/(.*?)(<paragraph (.*?)>)/$1\n$2/g;

   

    print $rivi;

}
