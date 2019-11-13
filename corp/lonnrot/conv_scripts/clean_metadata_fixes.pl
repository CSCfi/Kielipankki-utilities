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


    #add non-breaking-space to otherwise empty elements
    $rivi =~ s/<(paragraph)([^\/]*?)\/>/<$1$2>\n<\/$1>/g;

    $rivi =~ s/<(line)\/>/<$1>\&\#xA0\;<\/$1>/g;

    $rivi =~ s/<(cell)\/>/<$1>\&\#xA0\;<\/$1>/g;



    #delete empty element addition
    $rivi =~ s/<correction([^\/]*?)\/> //g;


    #delete empty elements hi underline
    $rivi =~ s/<hi rend=\"underline\"\/>//g;


    #change some editor_notes to corrections from the author
    $rivi =~ s/<span type=\"editor_note\" text=\"(den)\">([^<]*?)<\/span>/<correction type=\"addition\" orig=\"\">$1<\/correction>/g;

    $rivi =~ s/<span type=\"editor_note\" text=\"(det)\">([^<]*?)<\/span>/<correction type=\"addition\" orig=\"\">$1<\/correction>/g;

    $rivi =~ s/<span type=\"editor_note\" text=\"(III\. 1872)\">([^<]*?)<\/span>/\[$1\]/g;

    $rivi =~ s/<span type=\"editor_note\" text=\"(IV\.1872)\">([^<]*?)<\/span>/\[$1\]/g;

    $rivi =~ s/<span type=\"editor_note\" text=\"(kirja saattais seurata Aejmelaeuksen kirjaa)\">([^<]*?)<\/span>/\[$1\]/g;

    $rivi =~ s/<span type=\"editor_note\" text=\"(II\. 1872)\">([^<]*?)<\/span>/\[$1\]/g;

    $rivi =~ s/<span type=\"editor_note\" text=\"(allenius)\">([^<]*?)<\/span>/\[$1\]/g;

    $rivi =~ s/(<span type=\"editor_note\" text=\")\*(Lisätty ([^>]*?)\")\/>/$1$2 sign=\"\*\">\&\#xA0\;<\/span>/g;

    #empty editor notes
    $rivi =~ s/(<span type=\"editor_note\" text=\"([^>]*?)\")\/>/$1>\&\#xA0\;<\/span>/g;

    #editor notes with stars
    $rivi =~ s/(<span type=\"editor_note\" text=\"([^>]*?)\")>(\*)(<\/span>)/$1 sign=\"$3\">\&\#xA0\;$4/g;

    $rivi =~ s/(<span type=\"editor_note\" text=\"([^>]*?)\")>(\*\*)(<\/span>)/$1 sign=\"$3\">\&\#xA0\;$4/g;

    $rivi =~ s/(<span type=\"editor_note\" text=\"([^>]*?)\")>(\*\))(<\/span>)/$1 sign=\"$3\">\&\#xA0\;$4/g;


    #editor notes with \#
    $rivi =~ s/(<span type=\"editor_note\" text=\")(\#)(\">)([^<]*?)(<\/span>)/$1erikoismerkki$3\[erikoismerkki\]$5/g;

    #editor notes for special characters
    $rivi =~ s/(<span type=\"editor_note\" text=\"erikoismerkki\">)(.*?)(<\/span>)/$1\[erikoismerkki\]$3/g;

    $rivi =~ s/(<span type=\"editor_note\" text=\"erikoismerkki\: pitkä s\">)(.*?)(<\/span>)/$1\[pitkä s\]$3/g;

    $rivi =~ s/\(erikoismerkki\: pitkä s\)/<span type=\"editor_note\" text=\"erikoismerkki\: pitkä s\">\[pitkä s\]<\/span>/g;

    #fix special cases of editor_note
    $rivi =~ s/(<span type=\"editor_note\" text=\"Lisätty sivun alalalaitaan) (De(.*?))\" sign=\"(\*\))\">\&\#xA0\;(<\/span>)/$1\">$4 $2$5/g;
   
    $rivi =~ s/(<correction type=\"deletion\" orig=\"1 Lttd)\*erikoismerkki\: lispund\/leiviskä(\">(.*?)<\/correction>)/$1$2/g;

    print $rivi;

}
