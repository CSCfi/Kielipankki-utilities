#!/bin/perl
#use encoding "utf8";

#--------------------------------------------------
# Cleaning data in Aikakauslehti
#--------------------------------------------------
#
#

my $rivi;

while (<>){
    $rivi = $_;


    #add newline between text elements
    $rivi =~ s/(<\/text>)(<text)/$1\n$2/g;


    print $rivi;

}
