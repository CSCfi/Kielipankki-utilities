#!/bin/perl
#use encoding "utf8";

#--------------------------------------------------
# last fixes for Ylioppilasaineet
#--------------------------------------------------
#
#



my $rivi;


while (<>){
    $rivi = $_;

    #remove root element
    $rivi =~ s/<(\/)?essays>//g;

    $rivi =~ s/<(\/)?essay>//g;

    
    #Fixes of attribute values
    #$rivi =~ s/(author_sex=")([^\"]*?) P (\[\?\]\")/$1m$3/g;
    $rivi =~ s/(author_sex=")([^\"]*?) P (\[\?\])(\")/$1u$4/g;

    $rivi =~ s/(author_sex=")([^\"]*?) P(\")/$1m$3/g;

    $rivi =~ s/(author_sex=")([^\"]*?) T(\")/$1f$3/g;


    $rivi =~ s/(grade_combined=\"([^\"]*?)\/([^\"]*?)) P(\")/$1$4/g;

    $rivi =~ s/(grade_teacher=\"([^\"]*?))\/([^\"]*?)(\")/$1$4/g;

    $rivi =~ s/(grade_censor=\")([^\"]*?)\/([^\"]*?) P(\")/$1$3$4/g;

    $rivi =~ s/(grade_censor=\")([^\"]*?)\/(([^\"]*?)\")/$1$3/g;

    #Normalizing of topic numbers
    $rivi =~ s/(topic_num=\"([^\"]*?))\[([^\"]*?)(\")/$1$3$4/g;

    $rivi =~ s/(topic_num=\"([^\"]*?))\]([^\"]*?)(\")/$1$3$4/g;

    $rivi =~ s/(topic_num=\"([^\"]*?))\.([^\"]*?)(\")/$1$3$4/g;

    $rivi =~ s/(topic_num=\"([^\"]*?))\:(\")/$1$3/g;

    $rivi =~ s/(topic_num=\"([^\"]*?))\.(\")/$1$3/g;

    $rivi =~ s/(topic_num=\"\d\d?)\s+(\w\")/$1 $2/g;

    $rivi =~ s/(topic_num=\"\d\d?)(\D\")/$1 $2/g;

    $rivi =~ s/(topic_num=\"([^\"]*?))a(\")/$1A$3/g;

    $rivi =~ s/(topic_num=\"([^\"]*?))b(\")/$1B$3/g;

    $rivi =~ s/(topic_num=\"([^\"]*?))c(\")/$1C$3/g;

    $rivi =~ s/(topic_num=\"([^\"]*?))d(\")/$1D$3/g;

    $rivi =~ s/(topic_num=\")T/$1/g;

    print $rivi;

}

