#!/usr/bin/perl

use strict;
use warnings;
use open qw(:std :utf8);

my $chapter = "false";
my $paragraph = "false";
my $sentence = "false";

my $chapter_number = 0;
my $paragraph_number = 0;
my $sentence_number = 0;

my $paragraph_number_in_chapter = 0;

# egrep -A 3 '^[^ ]+ luku' dickens_fi_preprocessed.txt | egrep -v '^[^ ]+ luku' | egrep -v '^--' | perl -pe 's/^ *\n$//;'
my @titles_fi = 
("Kanslerinoikeudessa",
"Seurapiireissä",
"Alkumatka",
"Kaukohyväntekeväisyyttä",
"Aamuinen seikkailu",
"Koti",
"Aavekuja",
"Monenmoista pahaa",
"Enteitä ja todisteita",
"Lakikirjuri",
"Kallis veljemme",
"Varuillaan",
"Estherin kertomus",
"Galanteriaa",
"Bell Yard",
"Tom-all-Alone",
"Estherin kertomus",
"Lady Dedlock",
"Jatka matkaa",
"Uusi vuokralainen",
"Smallweedin suku",
"Herra Bucket",
"Estherin kertomus",
"Vetoomus oikeudessa",
"Rouva Snagsby näkee kaiken",
"Tarkka-ampujia",
"Vanhoja sotilaita",
"Rautaruukin patruuna",
"Nuori mies",
"Estherin kertomus",
"Hoitaja ja potilas",
"Sovittu aika",
"Tunkeilijat",
"Ruuvipenkki",
"Estherin kertomus",
"Chesney Wold",
"Jarndyce ja Jarndyce",
"Kamppailu",
"Asianajaja ja asiakas",
"Kansakunta ja kotikontu",
"Herra Tulkinghornin huoneessa",
"Herra Tulkinghornin toimistossa",
"Estherin kertomus",
"Kirje ja vastaus",
"Luottamustehtävä",
"Seis, seis!",
"Jon testamentti",
"Silmukka kiristyy",
"Velvollisuudentuntoinen ystävä",
"Estherin kertomus",
"Valistuminen",
"Jääräpäisyyttä",
"Jäljet",
"Ansa laukeaa",
"Pako",
"Takaa-ajo",
"Estherin kertomus",
"Talvinen päivä ja yö",
"Estherin kertomus",
"Tulevaisuudenkuvia",
"Yllätys",
"Toinen yllätys",
"Teräs ja rauta",
"Estherin kertomus",
"Elämä alkaa",
"Lincolnshiressä",
"Estherin kertomus päättyy");

# grep -A 3 'CHAPTER' dickens_clean_preprocessed.txt | egrep -v '^CHAPTER' | egrep -v '^--' | perl -pe 's/^ *\n$//;'
my @titles_en = 
("In Chancery",
 "In Fashion",
 "A Progress",
 "Telescopic Philanthropy",
 "A Morning Adventure",
 "Quite at Home",
 "The Ghost's Walk",
 "Covering a Multitude of Sins",
 "Signs and Tokens",
 "The Law-Writer",
 "Our Dear Brother",
 "On the Watch",
 "Esther's Narrative",
 "Deportment",
 "Bell Yard",
 "Tom-all-Alone's",
 "Esther's Narrative",
 "Lady Dedlock",
 "Moving On",
 "A New Lodger",
 "The Smallweed Family",
 "Mr. Bucket",
 "Esther's Narrative",
 "An Appeal Case",
 "Mrs. Snagsby Sees It All",
 "Sharpshooters",
 "More Old Soldiers Than One",
 "The Ironmaster",
 "The Young Man",
 "Esther's Narrative",
 "Nurse and Patient",
 "The Appointed Time",
 "Interlopers",
 "A Turn of the Screw",
 "Esther's Narrative",
 "Chesney Wold",
 "Jarndyce and Jarndyce",
 "A Struggle",
 "Attorney and Client",
 "National and Domestic",
 "In Mr. Tulkinghorn's Room",
 "In Mr. Tulkinghorn's Chambers",
 "Esther's Narrative",
 "The Letter and the Answer",
 "In Trust",
 "Stop Him!",
 "Jo's Will",
 "Closing in",
 "Dutiful Friendship",
 "Esther's Narrative",
 "Enlightened",
 "Obstinacy",
 "The Track",
 "Springing a Mine",
 "Flight",
 "Pursuit",
 "Esther's Narrative",
 "A Wintry Day and Night",
 "Esther's Narrative",
 "Perspective",
 "A Discovery",
 "Another Discovery",
 "Steel and Iron",
 "Esther's Narrative",
 "Beginning the World",
 "Down in Lincolnshire",
 "The Close of Esther's Narrative");

print "<!-- #vrt positional-attributes: id word lemma upos xpos feats head deprel deps misc -->\n";

my $lang = $ARGV[0];

# English text
if ($lang eq "--eng")
{
    print '<text filename="" title="Bleak House" year="1853" datefrom="18530101" dateto="18531231" timefrom="000000" timeto="235959" author="Charles Dickens" lang="en">'."\n";
}
# Finnish text
elsif ($lang eq "--fin")
{
    print '<text filename="" title="Kolea Talo" year="2006" datefrom="20060101" dateto="20061231" timefrom="000000" timeto="235959" author="Charles Dickens" translator="Kersti Juva" lang="fi" publisher="Tammi">'."\n";
}

foreach my $line ( <STDIN> ) {    

    if ($line =~ /^<chapter /)
    {
	$chapter = "true";
	my $title = "";
	if ($lang eq "--eng")
	{
	    $title = $titles_en[$chapter_number];
	}
	if ($lang eq "--fin")
	{
	    $title = $titles_fi[$chapter_number];
	}
	$title =~ s/'/&quot;/g;
	$line =~ s/<chapter title="">/<chapter title="${title}">/;
	$chapter_number++;
	$paragraph_number_in_chapter = 0;
    }
    elsif ($line =~ /^<\/chapter>/)
    {
	$chapter = "false";
	$paragraph = "false";
	$sentence = "false";
	print "</sentence>\n</paragraph>\n";
    }
    elsif ($line =~ /^<paragraph>/)
    {
	if ($paragraph eq "true")
	{
	    $sentence = "false";
	    print "</sentence>\n</paragraph>\n";
	}
	$paragraph = "true";
	$paragraph_number++;
	$paragraph_number_in_chapter++;
	$line =~ s/<paragraph>/<paragraph id="${paragraph_number}">/;
	if ($paragraph_number_in_chapter < 3)
	{
	    $line =~ s/>/ type="heading">/;
	}
    }
    elsif ($line =~ /^<sentence>/)
    {
	if ($sentence eq "true")
	{
	    print "</sentence>\n";
	}
	$sentence = "true";
	$sentence_number++;
	$line =~ s/<sentence>/<sentence id="${sentence_number}">/;
    }
    unless ($line =~ /^ *$/)
    {
	# Do not quote ampersand in &quot;
	unless ($line =~ /<chapter /)
	{
	    $line =~ s/&/&amp;/g;
	}
	print $line;
    }
}

print "</text>\n";
