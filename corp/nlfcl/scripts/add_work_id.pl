#!/bin/perl
#use encoding "utf8";

#--------------------------------------------------
# adding metadata work-id to ClassicalLibrary
#--------------------------------------------------
#
#

my $rivi;

while (<>){
    $rivi = $_;


    $rivi =~ s/<pdf_url>http\:\/\/www\.doria\.fi\/bitstream\/10024\/([^\/]*?)\/(.*?)<\/pdf_url>/<work_id>$1<\/work_id>/g;



    print $rivi;

}
