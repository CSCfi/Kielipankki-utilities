#!/bin/perl
#use encoding "utf8";

#--------------------------------------------------
# Fix metadata for STT
#--------------------------------------------------
#
#



my $rivi;


while (<>){
    $rivi = $_;

    #fix filename and lang
    $rivi =~ s/(filename=\")urn\:newsml\:stt\.fi\:\d+?\:(\d+?)\"/$1$2\.xml\"/g;

    $rivi =~ s/(lang=\")fi-FI(\")/$1fin$2/g;


    #fix dates
    $rivi =~ s/(date=\"(\d\d\d\d)-(\d\d)-(\d\d))T([^\"]*?)\"/$1\"/g;

    $rivi =~ s/(datefrom=\"(\d\d\d\d))-(\d\d)-(\d\d)T([^\"]*?)\"/$1$3$4\"/g;

    $rivi =~ s/(dateto=\"(\d\d\d\d))-(\d\d)-(\d\d)T([^\"]*?)\"/$1$3$4\"/g;

    #fix times
    $rivi =~ s/(timefrom=\")(\d\d\d\d)-(\d\d)-(\d\d)T(\d\d)\:(\d\d)\:(\d\d)\"/$1$5$6$7\"/g;

    $rivi =~ s/(timeto=\")(\d\d\d\d)-(\d\d)-(\d\d)T00\:00\:00\"/timeto=\"235959\"/g;

    $rivi =~ s/(timeto=\")(\d\d\d\d)-(\d\d)-(\d\d)T(\d\d)\:(\d\d)\:(\d\d)\"/$1$5$6$7\"/g;

  
    

    #move element tags on their own line
    $rivi =~ s/^\s+(<(\/)?paragraph)/$1/g;

    $rivi =~ s/(\S)(<(\/)?paragraph)/$1\n$2/g;

    $rivi =~ s/(.)(<(\/)?paragraph)/$1\n$2/g;

    $rivi =~ s/(<paragraph([^>]*?)>)(.)/$1\n$3/g;


    #clean feature-set values for subjects
    $rivi =~ s/(subjects([^=]*?)=\")\|(\")/$1$3/g;

    #clean attributes values
    #$rivi =~ s/(headline=\"([^\"]*?)) +(\")/$1$3/g;

    #$rivi =~ s/(creditline=\"([^\"]*?)) +(\")/$1$3/g;
    
    #$rivi =~ s/(author=\"([^\"]*?)) +(\")/$1$3/g;

    #$rivi =~ s/(author=\") +([^ ])([^\"]*?)(\")/$1$2$3$4/g;

    $rivi =~ s/( ([^ \"=]+?)=\"([^\"]+?)) +(\")/$1$4/g;

    $rivi =~ s/( ([^ \"=]+?)=\") +([^ \"])([^\"]+?)(\")/$1$3$4$5/g;

    $rivi =~ s/( ([^ \"=]+?)=\") +(\")/$1$3/g;

    #unify author name
    #$rivi =~ s/(author=\")STT.([A-ZÄÅÖÜ][^\"]*?) ([^\"]*?)\"/$1$2 $3\"/g;
    #$rivi =~ s/(author=\")STT ?– ?/$1/g;
    $rivi =~ s/(author=\") (\")/$1$2/g;
    
    $rivi =~ s/(author=\"([^\" ]*?) ([^\" ]*?)) +?(\")/$1$4/g;

    $rivi =~ s/(author=\"([^\"]*?))    (\")/$1$3/g;

    $rivi =~ s/(author=\"([^\"]*?)) (\")/$1$3/g;

    $rivi =~ s/(author=\")STT-SPT\//$1/g;

    $rivi =~ s/(author=\")STT-SPT–/$1/g;

    $rivi =~ s/(author=\")ST–/$1/g;

    $rivi =~ s/(author=\")\(STT–([^\"\)]*?)\)(\")/$1$2$3/g;

    $rivi =~ s/(author=\")\(STT–([^\"\)]*?)(\")/$1$2$3/g;

    $rivi =~ s/(author=\")STT–- /$1/g;

    $rivi =~ s/(author=\")STT–-/$1/g;

    $rivi =~ s/(author=\")STT ?– ?/$1/g;

    $rivi =~ s/(author=\")STT ?— ?/$1/g;

    $rivi =~ s/(author=\")STT ?- ?/$1/g;

    $rivi =~ s/(author=\")STTT ?– ?/$1/g;

    $rivi =~ s/(author=\")STT – /$1/g;

    $rivi =~ s/(author=\")[´ ]([A-ZÄÖÅÜ])/$1$2/g;

    $rivi =~ s/(author=\")\(STT-([^\"]*?)\)(\")/$1$2$3/g;

    $rivi =~ s/(author=\"([^\"]*?)([^ ])) +?(\")/$1$4/g;

    $rivi =~ s/(author=\") +?(\")/$1$2/g;

    $rivi =~ s/(author=\"([^\"]*?))\/STT(\")/$1$3/g;




    #unifiy creditline
    $rivi =~ s/(creditline=\"STT–\(ST)\(?(\")/$1\)$2/g;

    $rivi =~ s/(creditline=\"STT–\(STT\)stt)\)(\")/$1$2/g;

    $rivi =~ s/(creditline=\"STT–\(STT)\((\)\")/$1$2/g;

    $rivi =~ s/(creditline=\"STT–)(STT–Reuters–DPA\)\")/$1\($2/g;

    $rivi =~ s/(creditline=\"([^\"\(]*?))8(([^\"]*?)\)\")/$1\($3/g;

    $rivi =~ s/(creditline=\"([^\"]*?))9(\")/$1\)$3/g;

    $rivi =~ s/(creditline=\"STT–\(STT–) /$1/g;

    #$rivi =~ s/(creditline=\"(.*?))-((.*?)\")/$1–$3/g;

    $rivi =~ s/(creditline=\"([^\"]*?)) +?– +?(([^\"]*?)\")/$1\&\#x2013\;$3/g;

    $rivi =~ s/(creditline=\"([^\"]*?)) +?— +?(([^\"]*?)\")/$1\&\#x2013\;$3/g;

    $rivi =~ s/(creditline=\"([^\"]*?)) +?– +?(([^\"]*?)\")/$1\&\#x2013\;$3/g;

    $rivi =~ s/(creditline=\"([^\"]*?)) +?- +?(([^\"]*?)\")/$1\&\#x2013\;$3/g;

    $rivi =~ s/(creditline=\"([^\"]*?))– +(([^\"]*?)\")/$1\&\#x2013\;$3/g;

    $rivi =~ s/(creditline=\"([^\"]*?))– +(([^\"]*?)\")/$1\&\#x2013\;$3/g;

    $rivi =~ s/(creditline=\"([^\"]*?))– +(([^\"]*?)\")/$1\&\#x2013\;$3/g;

    $rivi =~ s/(creditline=\"([^\"]*?))- (([^\"]*?)\")/$1\&\#x2013\;$3/g;

    $rivi =~ s/(creditline=\"([^\"]*?))–(([^\"]*?)\")/$1\&\#x2013\;$3/g;

    $rivi =~ s/(creditline=\"([^\"]*?)) +–(([^\"]*?)\")/$1\&\#x2013\;$3/g;

    $rivi =~ s/(creditline=\"([^\"]*?))–-(([^\"]*?)\")/$1\&\#x2013\;$3/g;

    $rivi =~ s/(creditline=\"([^\"]*?))-–(([^\"]*?)\")/$1\&\#x2013\;$3/g;

    $rivi =~ s/(creditline=\"([^\"]*?))––(([^\"]*?)\")/$1\&\#x2013\;$3/g;

    $rivi =~ s/(creditline=\"([^\"]*?))\.-(([^\"]*?)\")/$1\&\#x2013\;$3/g;

    $rivi =~ s/(creditline=\"([^\"]*?)), +(([^\"]*?)\")/$1, $3/g;

    $rivi =~ s/(creditline=\"([^\"]*?)) (\)\")/$1$3/g;

    $rivi =~ s/(creditline=\"([^\"]*?))\)(\)\")/$1$3/g;

    #$rivi =~ s/(creditline=\"([^\"]*?)) +(–) +(([^\"]*?)\")/$1$3$4/g;

    $rivi =~ s/(creditline=\"([^\"]*?)\()([^\"\)]*?)(\")/$1$3\)$4/g;

    $rivi =~ s/(creditline=\"([^\"]*?)\(([^\"]*?))\((\)\")/$1$4/g;

    $rivi =~ s/(creditline=\"([^\"]*?)) (\)\")/$1$3/g;

    $rivi =~ s/(creditline=\"STT–\(([^\"]*?)–) +(([^\"]*?)\")/$1$3/g;

    $rivi =~ s/(creditline=\"STT–\(([^\"]*?)–)–(([^\"]*?)\")/$1$3/g;

    $rivi =~ s/(creditline=\"STT–\(([^\"]*?)) (–([^\"]*?)\")/$1$3/g;

    $rivi =~ s/(creditline=\"([^\"]*?)) (\)\")/$1$3/g;

    #convert endashes
    $rivi =~ s/\&lt\;endash\&gt\;-\&lt\;\/endash\&gt\;/\&\#x2013\;/g;

    #$rivi =~ s/(creditline=\"([^\"]*?))\&lt\;endash\&gt\;–\&lt\;\/endash\&gt\;/$1–/g;

    #$rivi =~ s/(creditline=\"([^\"]*?))\&lt\;endash\&gt\;-\&lt\;\/endash\&gt\;/$1–/g;



    #remove superfluous emtpy spaces at end of attribute values
    #$rivi =~ s/(([^\"]*?)=\"([^\"]*?)) +(\")/$1$4/g;

    #remove root element
    #$rivi =~ s/<(\/)?articles>//g;





    print $rivi;

}

