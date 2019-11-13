#!/bin/perl
#use encoding "utf8";

#--------------------------------------------------
# Cleaning metadata for Aikakauslehtikorpus
#--------------------------------------------------
#
#

my $rivi;

while (<>){
    $rivi = $_;

    #clean date and time information
   # $rivi =~ s/datefrom=\"(\d\d\d\d)-(\d\d)-(\d\d)T(.*?)\"/datefrom=\"$1$2$3\"/g;

    #$rivi =~ s/(metadata_file=\")(.*?)\/(.[^\/]*?\.xml\")/$1$3/g;

    $rivi =~ s/(filename=\")(.*?)\/(.[^\/]*?\.xml\")/$1$3/g;

    $rivi =~ s/(issue=\")(.*?)\/(.[^\/]*?\.xml\")/$1$3/g;

    $rivi =~ s/(page=\")(.*?)\/(.[^\/]*?\.xml\")/$1$3/g;

    $rivi =~ s/datefrom=\"(\d\d\d\d)\"/datefrom=\"${1}0101\"/g;

    $rivi =~ s/dateto=\"(\d\d\d\d)\"/dateto=\"${1}1231\"/g;

    $rivi =~ s/(date_modified=\")(\d\d)\.(\d)\.(\d\d\d\d)(\")/$1${4}-0$3-$2$5/g;

    $rivi =~ s/(wordcount=\"\d*?) (\d*?\")/$1$2/g;


    #uniform language attributes
    $rivi =~ s/lang=\"sv\"/lang=\"swe\"/g;

    $rivi =~ s/lang=\"fi\"/lang=\"fin\"/g;

    $rivi =~ s/lang=\"FI\"/lang=\"fin\"/g;
    



    #remove body element
    $rivi =~ s/<body>//g;
    $rivi =~ s/<\/body>//g;

    print $rivi;

}
