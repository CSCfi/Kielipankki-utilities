#!/bin/perl
#use encoding "utf8";

#--------------------------------------------------
# Fixes for STT
#--------------------------------------------------
#
#



my $rivi;


while (<>){
    $rivi = $_;

    #remove XML declarations
    $rivi =~ s/<\?xml version=\"1\.0\" encoding=\"UTF-8\"\?>//g;

    #attributes from newsItem
    $rivi =~ s/(<newsItem guid=\"urn\:newsml\:stt\.fi\:([^\"]*?\"))([^>]*?)xml\:(lang=\"([^\"]*?\"))([^>]*?)>/$1 $4>/g;

    $rivi =~ s/<catalogRef([^\>]*?)\/>//g;

    #newsItem tags on their own line
    $rivi =~ s/(>)(<\/newsItem>)/$1\n$2/g;

    #prepare metadata for xsl conversion
    $rivi =~ s/(<subject ([^>]*?) qcode=\"sttdepartment\:\d+\")>/$1 info=\"sttdepartment\">/g;

    $rivi =~ s/(<subject ([^>]*?) qcode=\"sttsubj\:\d+\")>/$1 info=\"sttsubject\">/g;

    $rivi =~ s/(<genre qcode=\"sttgenre\:\d+\")>/$1 info=\"sttgenre\">/g;

    $rivi =~ s/(<genre qcode=\"sttversion\:\d+\")>/$1 info=\"sttversion\">/g;


    $rivi =~ s/(<subject ([^>]*?) qcode=\"sttsubj\:\d\d000000\")/$1 level=\"level1\"/g;

    $rivi =~ s/(<subject ([^>]*?) qcode=\"sttsubj\:\d\d\d\d[1-9]000\")/$1 level=\"level2\"/g;

    $rivi =~ s/(<subject ([^>]*?) qcode=\"sttsubj\:\d\d\d\d\d\d\d[1-9]\")/$1 level=\"level3\"/g;

    $rivi =~ s/(<broader ([^>]*?) qcode="(\w+)\:\d+")>/$1 info="$3">/g;




    #clean headline
    #$rivi =~ s/(<headline>)EMBARGO (([^<]*?)<\/headline>)/$1$2/g;

    #$rivi =~ s/(<headline>)ÄLÄ PÄIVITÄ ENÄÄ (([^<]*?)<\/headline>)/$1$2/g;

    #$rivi =~ s/(<headline>)ÄLÄ KÄYTÄ (([^<]*?)<\/headline>)/$1$2/g;

    #$rivi =~ s/(<headline>)ÄLÄ KÄYTÄ TÄTÄ ENÄÄ (([^<]*?)<\/headline>)/$1$2/g;

    #$rivi =~ s/(<headline>([^<]*?)) \/\/\/([^\/]*?)\/\/\/(<\/headline>)/$1$4/g;


    print $rivi;

}

