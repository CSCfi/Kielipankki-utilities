#!/usr/bin/perl

# Lis‰‰ tietueen loppuun PDF-linkkien kent‰n. PDF-linkki luodaan murrealue-, pit‰j‰-, ja lokaatio-kenttien pohjalta, mik‰li pit‰j‰ on mainittu ao. if-lauseessa.

@rivit = <STDIN>;

for ($i = 0; $i < @rivit; ++$i) {
    $rivi = $rivit[$i];
    $rivi =~ s#\r##;

    $alue = $rivi;
    $pitaja = $rivi;
    $lokaatio = $rivi;

    $alue =~ s#^([^\t]*)\t.*\n$#$1#;
    $pitaja =~ s#^[^\t]*\t([^\t]*)\t.*\n$#$1#;
    $lokaatio =~ s#^[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t([^\t]*)\t.*\n$#$1#;  
    $lokaatio =~ s#vain digitaalisessa muodossa##;
    $lokaatio =~ s#SKN ([0-9]+)##g;
    $lokaatio =~ s#(SK|O)NA [0-9]+[:][0-9A-Z]+##g;
    $lokaatio =~ s#ONA##;
    $lokaatio =~ s#^[ ]+##;
    $lokaatio =~ s#[ ]+$##;
    $lokaatio =~ s#[ ]+# #g;

    if ($pitaja =~ /^(Hinnerjoki|Honkilahti|Laitila|Masku|Merimasku|Mietoinen|Nousiainen|Rauma|Rym‰ttyl‰|Taivassalo|Halikko|Kaarina|Sauvo|Suomusj‰rvi|Merikarvia|Pori|Loimaa|Pˆyty‰|Somero|Vihti|Honkajoki|Kankaanp‰‰|Kiikka|Parkano|Virrat|Hauho|Juupajoki|Kalvola|Kangasala|Kuru|Ruovesi|S‰‰ksm‰ki|Teisko|Tuulos|Hausj‰rvi|Loppi|Nurmij‰rvi|Tammela|Yp‰j‰|Asikkala|Orimattila|Askola|Myrskyl‰|Pornainen|Artj‰rvi|Kymi|Valkeala|Vehkalahti|Ilmajoki|Isojoki|Jalasj‰rvi|Kauhava|Kurikka|Laihia|Tˆys‰|V‰h‰kyrˆ|Ylih‰rm‰|Haapavesi|Halsua|Himanka|Kalajoki|Kaustinen|K‰lvi‰|K‰rs‰m‰ki|Nivala|Perho|Pyh‰joki|Rautio|Reisj‰rvi|Veteli|Kuivaniemi|Oulujoki|Paavola|Pattijoki|Saloinen|Yli-Ii|Kolari|Ylitornio|J‰llivaara|Keminmlk|Kittil‰|Simo|Sodankyl‰|Kemij‰rvi|Salla|It‰-Ruija|Raisi|Kuhmoinen|Hirvensalmi|Mikkelinmlk|M‰ntyharju|Ristiina|Sulkava|S‰‰minki|Ilomantsi|Juuka|Kes‰lahti|Kitee|Kontiolahti|Kuusj‰rvi|Liperi|Nurmes|Pielisj‰rvi|Polvij‰rvi|Hein‰vesi|Karttula|Kiuruvesi|Lapinlahti|Lepp‰virta|Pieks‰m‰ki|Pyh‰j‰rvi|Siilinj‰rvi|Sonkaj‰rvi|Tuusniemi|Vehmersalmi|Vesanto|Kannonkoski|Karstula|Laukaa|Pihtipudas|Saarij‰rvi|Sumiainen|Uurainen|Keuruu|Lappaj‰rvi|Kajaani|Pudasj‰rvi|Suomussalmi|Heinjoki|Koivisto|Lappee|Luum‰ki|Miehikk‰l‰|Uusikirkko|Viipurinmlk|Virolahti|Joutseno|Lumivaara|Ruokolahti|Tuutari|Lemi|Savitaipale|Sortavala|Uukuniemi)$/) {
      if ($lokaatio =~ /^[0-9a-z]+$/) {
        $rivi =~ s#\n##;     
        $rivi = $rivi . "\t" . $alue . "_" . $pitaja . "_" . $lokaatio . ".pdf\n";
      }
      else {
        $rivi =~ s#\n##;
	$rivi = $rivi . "\t";
        $tulostettu = 0;
	while (($lokaatio =~ /^[0-9a-z]+[, ]/) || ($lokaatio =~ /^[0-9a-z]+$/)) {
	  $temp = $lokaatio;
          if ($lokaatio =~ /^[0-9a-z]+[, ]/) { 
	    $temp =~ s#^([0-9a-z]+)[,]*[ ]+.*$#$1#;
            $lokaatio =~ s#^[0-9a-z]+[,]*[ ]+(.*)$#$1#;
            $lokaatio =~ s#^[ ]+##;
	  }
          elsif ($lokaatio =~ /^[0-9a-z]+$/) {
            $temp =~ s#^([0-9a-z]+)$#$1#;
            $lokaatio =~ s#^[0-9a-z]+$##;
	  }
          else {
	      print $lokaatio . "\n";
	  }
          $lokaatio =~ s#[ ]+$##;
          #$rivi =~ s#\n##;
	  $rivi = $rivi . $alue . "_" . $pitaja . "_" . $temp . ".pdf ";
          $tulostettu = 1;
	}
        if (($lokaatio eq "-") || ($lokaatio =~ /SKNA[:]*[0-9]+[:][0-9]+/) || ($lokaatio =~ /SKN[A]*[:][0-9]+/)) {
	  if (!$tulostettu) {
	    $rivi = $rivi . "-";
	  }
	}
        elsif ($lokaatio ne "") {
          $rivi = $rivi . "<error: loc>"; 
        }
        elsif (!$tulostettu) {
	  $rivi . $rivi . "-";
	}
	$rivi = $rivi . "\n";  
     }
  }
  else {
    $rivi =~ s#\n$##;
    $rivi = $rivi . "\t\n";
  }

  print $rivi; 
}
