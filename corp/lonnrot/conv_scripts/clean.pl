#!/bin/perl
#use encoding "utf8";

#--------------------------------------------------
# Last cleaning for Loennrot
#--------------------------------------------------
#
#



my $rivi;


while (<>){
    $rivi = $_;

    #clean adressee
    $rivi =~ s/(addressee=\"Vastaanottajaluettelo), (\")/$1$2/g;

    #fix attribute name
    $rivi =~ s/(<hi rend=\")undelrine(\">)/$1underline$2/g;

    #remove root element
    $rivi =~ s/<(\/)?letters>//g;


    #remove empty elements
    #$rivi =~ s/<cell\/>//g;

    #$rivi =~ s/<paragraph\/>//g;

    #$rivi =~ s/<gap\/>/\&lt\;gap\&gt\;/g;


    #every tag should be at beginning of a line
    #$rivi =~ s/^\s+(<(\/)?([^>]*?)>)/$1/g;
    
    #$rivi =~ s/(.+?)(<(\/)?([^>]*?)>)/$1\n$2/g;

    #$rivi =~ s/(>)(<(\/)?([^>]*?)>)/$1\n$2/g;
   
    $rivi =~ s/^\s+(<(\/)?paragraph)/$1/g;

    $rivi =~ s/(\S)(<(\/)?paragraph)/$1\n$2/g;

    $rivi =~ s/(.)(<(\/)?paragraph)/$1\n$2/g;
    


    print $rivi;

}
