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

    #change text_new to text
    $rivi =~ s/<(\/?)text_new/<$1text/g;

    #clean whitespaces in text attributes
    $rivi =~ s/(Suomalaisen Kirjallisuuden)&#xA;(.*?)(Seura)/$1 $3/g;

    $rivi =~ s/(repository=\"(.*?)Kansalliskirjaston)\&\#xA\; +(Digitoidut Aineistot)\&\#xA\; +(\")/$1 $3$4/g;

    $rivi =~ s/((.*?)=\"([^\"]*?)) +(\&\#xA\;) +(([^\"]*?)\")/$1 $5/g;

    $rivi =~ s/((.*?)=\"([^\"]*?))(\&\#xA\;) +(([^\"]*?)\")/$1 $5/g;

    $rivi =~ s/(\&\#xA\;) +/ /g;

    $rivi =~ s/(<alternative text=\") (([^>]*?)\">)/$1$2/g;

    #format date attributes
    #$rivi =~ s/(datefrom=\")(\d+)-(\d+)-(\d+)(\")/$1$2$3$4$5/g;
    $rivi =~ s/(datefrom=\")(\d\d\d\d)-(\d\d)-(\d\d)([^\"]*?)(\")/$1$2$3$4$6/g;

    #$rivi =~ s/(dateto=\")(\d+)-(\d+)-(\d+)(\")/$1$2$3$4$5/g;
    $rivi =~ s/(dateto=\")(\d\d\d\d)-(\d\d)-(\d\d)([^\"]*?)(\")/$1$2$3$4$6/g;

    $rivi =~ s/(year=\")(\d\d\d\d)-(\d\d)-(\d\d)([^\"]*?)(\")/$1$2$6/g;

    #uniform language information
    $rivi =~ s/(lang=\")svenska(\")/$1swe$2/g;

    $rivi =~ s/(lang=\")ruotsi(\")/$1swe$2/g;

    $rivi =~ s/(lang=\")(\")/$1swe$2/g;

    
    $rivi =~ s/(lang=\")finska(\")/$1fin$2/g;

    $rivi =~ s/(lang=\")suomi(\")/$1fin$2/g;


    #standardize attribute div_type
    $rivi =~ s/(div_type=\")maininta_konseptikirjassa(\")/$1merkinta_konseptikirjassa$2/g;

    $rivi =~ s/(div_type=\")merkinta_kirjekonseptissa(\")/$1merkinta_konseptikirjassa$2/g;

    $rivi =~ s/(div_type=\")merkinta_konseptikirjassas(\")/$1merkinta_konseptikirjassa$2/g;

    $rivi =~ s/(div_type=\")(\")/$1kirje$2/g;



    #add newline between text elements
    $rivi =~ s/(<\/text>)(<text)/$1\n$2/g;

    
    #paragraph tags should be on their own line
    $rivi =~ s/(<(\/)?paragraph([^>]*?)>)(.*?)/$1\n$4/g;


    #fixes for attribute addressee
    $rivi =~ s/addressee=\"Neovius tai Roos, Anders Fabian tai Samuel\"/addressee=\"Neovius, Anders Fabian tai Roos, Samuel\"/g;

    $rivi =~ s/(addressee=\"Castrén, )Math?ias( Alexander\")/$1Matthias$2/g;

    $rivi =~ s/(addressee=\")Gustaf Asp, Adolf Fredrik Borg(\")/$1Asp, Gustaf ja Borg, Adolf Fredrik$2/g;

    $rivi =~ s/(addressee=\"Lindfors, Mårten Johan) Lindfors(\")/$1$2/g;

    $rivi =~ s/(addressee=\")(R|r)abbee?(, Frans Johan\")/$1Rabbe$3/g;

    $rivi =~ s/(addressee=\")([^\"]*?)\. (\")/$1$2\.$3/g;

    $rivi =~ s/(addressee=\")([^\"]*?)\, (\")/$1$2$3/g;

    $rivi =~ s/(addressee=\")(Hamer, Nils Justus Albert) Hamer(\")/$1$2$3/g;

    $rivi =~ s/(addressee=\")(Kellgren, Abraham Herman August) Kellgren(\")/$1$2$3/g;

    $rivi =~ s/(addressee=\")(Malmgren, Anders Johan) Malmgren(\")/$1$2$3/g;

    $rivi =~ s/(addressee=\")(Renvall,) 1520(\")/$1$2 T\. T\.$3/g;

    #additions for new data 2019
    $rivi =~ s/(addressee=\")(\" bibl=\"1654\")/$1Hahnsson, Johan Adrian$2/g;

    $rivi =~ s/(addressee=\")(\" bibl=\"1655\")/$1Hahnsson, Johan Adrian$2/g;

    $rivi =~ s/(addressee=\")(\" bibl=\"1656\")/$1Hahnsson, Johan Adrian$2/g;

    $rivi =~ s/(addressee=\")(\" bibl=\"1276\")/$1Collan, Karl$2/g;

    $rivi =~ s/(addressee=\"Lang) (Adolf Reinhold), (Cavonius) (Gustaf Adolf\")/$1, $2 ja $3, $4/g;

    $rivi =~ s/(addressee=\"Malmgren) (Karl), (Himberg) (Efraim\")/$1, $2 ja $3, $4/g;


    #Fixes for attribute author
    $rivi =~ s/(author=\")([^\"]*?)\. (\")/$1$2\.$3/g;

    $rivi =~ s/(author=\")([^\"]*?)\, (\")/$1$2$3/g;

    $rivi =~ s/(author=\")([^\"]*?) (\")/$1$2$3/g;

    #notes in square brackets
    #$rivi =~ s/(Kirjekopion sivulla leima \"Arciv A)\[(kademii)\]( N)\[(auk)\]( SSSR )\[(Neuvostoliiton tiedeakatemian arkisto)\]( (.*?)\".)/$1\&\#91\;$2\&\#93\;$3\&\#91\;$4\&\#93\;$5\&\#91\;$6\&\#93\;$7/g;

    #$rivi =~ s/([^\"])\[([^\[]*?)\]/$1<span type=\"editor_note\">$2<\/span>/g;




    print $rivi;

}

