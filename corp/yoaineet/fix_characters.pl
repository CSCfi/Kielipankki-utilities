#!/bin/perl
#use encoding "utf8";

#--------------------------------------------------
# Fix characters for Ylioppilasaineet
#--------------------------------------------------
#
#



my $rivi;


while (<>){
    $rivi = $_;

    #remove characters
    $rivi =~ s/\{Alpha\}//g;

    $rivi =~ s/\{cong\}//g;

    $rivi =~ s/\{Beta\}//g;

    $rivi =~ s/\{equals\}//g;
    
    $rivi =~ s/\{nabla\}//g;

    $rivi =~ s/\{gt\}//g;



    #rename characers
    $rivi =~ s/\{rho\}/\&\#xf8\;/g;

    $rivi =~ s/\{Epsilon\}/\&\#xb0\;/g;



    print $rivi;

}

