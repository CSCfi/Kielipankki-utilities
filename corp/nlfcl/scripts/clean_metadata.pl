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

    #clean date and time information
   # $rivi =~ s/datefrom=\"(\d\d\d\d)-(\d\d)-(\d\d)T(.*?)\"/datefrom=\"$1$2$3\"/g;

    $rivi =~ s/datefrom=\"(\d\d\d\d)\"/datefrom=\"${1}0101\"/g;

    #$rivi =~ s/dateto=\"(\d\d\d\d)-(\d\d)-(\d\d)T(.*?)\"/dateto=\"$1$2$3\"/g;
    $rivi =~ s/dateto=\"(\d\d\d\d)\"/dateto=\"${1}1231\"/g;


    #$rivi =~ s/timefrom=\"(.*?)T(\d\d)\:(\d\d)\:(\d\d)\.(.*?)\"/timefrom=\"$2$3$4\"/g;
    $rivi =~ s/timefrom=\"(.*?)\"/timefrom=\"000000\"/g;

    $rivi =~ s/timeto=\"(.*?)\"/timeto=\"235959\"/g;


    #uniform language attributes
    $rivi =~ s/lang=\"sv\"/lang=\"swe\"/g;

    $rivi =~ s/lang=\"fi\"/lang=\"fin\"/g;

    $rivi =~ s/lang=\"eng\"/lang=\"swe\"/g;

    $rivi =~ s/lang=\"u\"/lang=\"fin\"/g;


    #shorten date of digitalization
    $rivi =~ s/digitized=\"(\d\d\d\d-\d\d-\d\d).*?\"/digitized=\"$1\"/g;

    #clean author and contributor fields
    $rivi =~ s/(author=\"([^\"]*?)) \(kirjoittaja\.\)/$1/g;

    $rivi =~ s/(contributor=\"[^\"]*?[a-z][a-z])\./$1/g;

    $rivi =~ s/(author|contributor)=\"([^\"]*?([A-Z]|Th))( \([^\"]*?\))?\"/$1="$2.$4"/g;

    $rivi =~ s/\(kuv\)\/ill\.\)/(kuv\/ill.)/g;


    #clean pdflink
    $rivi =~ s/\|http\:\/\/www\.doria\.fi\/bitstream\/handle\/10024\/((.*?)\.pdf)/\|$1/g;

    $rivi =~ s/(\|([^\"]*?)\.pdf ) /$1/g;

    #add newline between text elements
    $rivi =~ s/(<\/text>)(<text)/$1\n$2/g;

    $rivi =~ s/^\s+(<(\/)?text)/$1/g;

    
    #also <page> tags should be at beginning of line
    $rivi =~ s/^\s+(<(\/)?page)/$1/g;

    #remove multiple spaces from attribute values
    $rivi =~ s/(title=\"Ne prophetat\. : ) (Haggaj. Sacharia. Maleachi\")/$1$2/g;

    $rivi =~ s/(publisher=\"\[Turku\] \: ) (\[tekijä\], 1810 \(Turussa \: Frenckell\))/$1$2/g;


    print $rivi;

    

}
