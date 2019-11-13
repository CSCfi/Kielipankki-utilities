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

    #remove stylesheet and dtd info


    $rivi =~ s/<\?xml version.*?\?>//g;

    $rivi =~ s/<\?xml-model.*?\?>//g;

    $rivi =~ s/<TEI (.*?)>/<letter>/g;

    $rivi =~ s/<\/TEI>/<\/letter>/g;

    #prepare rs links
    $rivi =~ s/(<p>Konseptikirjan merkintä(.*?)<rs )((.*?)>(.*?)<\/rs>)/$1relation_type=\"entry_sketchbook\" relation_to=\"$5\" $3/g;

    $rivi =~ s/(<p>Merkintä konseptikirjassa(.*?)<rs )((.*?)>(.*?)<\/rs>)/$1relation_type=\"entry_sketchbook\" relation_to=\"$5\" $3/g;

    $rivi =~ s/(<p>Konseptit (.*?) kirjeeseen <rs )((.*?)>(.*?)<\/rs>)/$1relation_type=\"concept_of\" relation_to=\"$5\" $3/g;


    $rivi =~ s/(<p>([^<]*?)onsepti ([^<]*?) <rs )((.*?)>(.*?)<\/rs>)/$1relation_type=\"concept_of\" relation_to=\"$6\" $4/g;

    $rivi =~ s/(<p>([^<]*?)onsepti ([^<]*?) <rs)(>(.*?)<\/rs>)/$1 relation_type=\"concept_of\" relation_to=\"$5\"$4/g;

    #$rivi =~ s/(<p>Konsepti (.*?)<rs )((.*?)>(.*?)<\/rs>)/$1relation_type=\"concept_of\" relation_to=\"$5\" $3/g;

    #$rivi =~ s/(<p>Konsepti (.*?)<rs)(>(.*?)<\/rs>)/$1 relation_type=\"concept_of\" relation_to=\"$4\" $3/g;


    $rivi =~ s/(<p>Kopio (.*?)<rs )((.*?)>(.*?)<\/rs>)/$1relation_type=\"copy_of\" relation_to=\"$5\" $3/g;

    $rivi =~ s/(<p>Transkriptio (.*?)<rs )((.*?)>(.*?)<\/rs>)/$1relation_type=\"transcript_of\" relation_to=\"$5\" $3/g;

    $rivi =~ s/(Ks. kirje <rs )((.*?)>(.*?)<\/rs>)/$1relation_type=\"concept_of\" relation_to=\"$4\" $2/g;

    $rivi =~ s/(<p>Konseptit (.*?)<rs )((.*?)>(.*?)<\/rs>(.*?)<rs (.*?)>(.*?)<\/rs>(.*?)<\/p>)/$1relation_type=\"concept_of\" relation_to=\"$5, $8\" $3/g;


 ## not working for more than two references
    #work-around
    $rivi =~ s/(<p>Konseptit kirjeisiin <rs )(type=\"ident\">2272<\/rs>)/$1relation_type=\"concept_of\" relation_to=\"2272, 2262, 2263, 2260\" $2/g;

    $rivi =~ s/(<p>Konseptit kirjeisiin <rs )(type=\"ident\">2277<\/rs>)/$1relation_type=\"concept_of\" relation_to=\"2277, 2256, 2280\" $2/g;

    $rivi =~ s/(<p>Konseptit kirjeisiin <rs )(type=\"ident\">1913<\/rs>)/$1relation_type=\"concept_of\" relation_to=\"1913, 1510, 1511, 1512\" $2/g;

    $rivi =~ s/(<p>Konseptit kirjeisiin <rs )(type=\"ident\">2270<\/rs>)/$1relation_type=\"concept_of\" relation_to=\"2270, 2251, 2281, 2261, 2269\" $2/g;

    $rivi =~ s/(<p>Konsepti raporttin <rs )relation_type=\"concept_of\" relation_to=\"544\"((.*?)>(.*?)<\/rs> ja rokotustilastoon <rs (.*?)>(.*?)<\/rs>)/$1relation_type=\"concept_of\" relation_to=\"$4, $6\" $2/g;




    #element gap
    $rivi =~ s/<gap\/>/\&lt\;gap\&gt\;/g;

    $rivi =~ s/<gap \/>/\&lt\;gap\&gt\;/g;
    

    #mark-up for square brackets in data
    $rivi =~ s/\[([^\]]*?)\]/<square_bracket>$1<\/square_bracket>/g;

    ##special cases
    $rivi =~ s/(minun\=)\[(jatkuu aukeaman)/$1<square_bracket>$2 /g;

    $rivi =~ s/(vas\. alareunassa)\](ki)/$1<\/square_bracket>$2/g;

    $rivi =~ s/(nas )\[(viereisen marg\.)/$1<square_bracket>$2 /g;

    $rivi =~ s/(runon sana)\]/$1<\/square_bracket>/g;

    $rivi =~ s/\[(kirja saattais seurata Aejmelaeuksen)/<square_bracket>$1/g;

    $rivi =~ s/(kirjaa)\](\.)/$1<\/square_bracket>$2/g;

    $rivi =~ s/\[(erikoismerkki)\)/<square_bracket>$1<\/square_bracket>/g;


    ##data fixes
    $rivi =~ s/(Kyllä minä maksan Herra Professorille sitte kun saan)/$1<\/p>/g;

    print $rivi;

}
