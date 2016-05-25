#!/usr/bin/perl

# Erottaa murrealueen ja pitäjän omiksi kentikseen eli lisää niiden välille sarkeimen. Lisäksi aakkostaa signumit ja lokaatiokoodit sekä poistaa duplikaatit ja korjaa ilmeisimmät signumoinnin näppäilyvirheet (esim. kuuden numeron sarja erotetaan kahdeksi kolminumeroiseksi). Haastavampia signumi- ja lokaatiovirheitä ohjelma ei korjaa vaan merkitsee ne koodilla <error>. Duplikaattien poistosta ja korjauksista raportoidaan virhevirrassa (stderr), joilloin voidaan varmistua, ettei ohjelma ole töppäillyt.

@rivit = <STDIN>;

for ($i = 0; $i < @rivit; ++$i) {
    $rivit[$i] =~ s#[ ]+\t#\t#g;
    $rivi = $rivit[$i];

    $rivi =~ s#\0240# #g; 
    $rivi =~ s#[ ]+\t#\t#g;
    $rivi =~ s#\t[ ]+#\t#g;
    $rivi =~ s#[ ]+# #g;
    
    if ($rivi =~ /^[0-9][a-z]* [A-ZÖÄÅ]/) {
      $rivi =~ s#^([^ ]+) #$1\t#;
    }

    $pitaja = $rivi;
    $pitaja =~ s#^([^\t]*\t[^\t]*)\t.*\n$#$1#;
    $pitaja =~ s#\t# #g;
 
    $signumit = $rivi;
    $signumit =~ s#([0-9]+)[.][a-zöäå]+#$1#g;
    $signumit =~ s#^[^\t]*\t[^\t]*\t([^\t]*)\t.*\n$#$1#;
    $signumit =~ s#^[ ]+##;
    $signumit =~ s#[ ]+$##;

    @sigLista = split(/ /, $signumit);
   
    $korjatutSignumit = "";

    for ($j = 0; $j < @sigLista; ++$j) {
      $koodi = $sigLista[$j];
      $koodi =~ s#[ ]+$##;

      # Poistetaan tai korjataan tod.näk. lyöntivirheet:
      $koodi =~ s#"##g;
      $koodi =~ s#¨##g;
      $koodi =~ s#'##g;
      $koodi =~ s#´##g;
      $koodi =~ s#1700#170#g;
      
      $ed_koodi = "";

      if ($j > 0) {
	  $ed_koodi = $sigLista[$j - 1];
         $ed_koodi =~ s#[ ]+$##;
      }
  
      if ($ed_koodi eq $koodi) {
          print STDERR "Huom! Poistettu duplikaatti. " . $pitaja . " r. " . $i . ": " . $ed_koodi . "<->" . $koodi . "\n";
          next;
      }
      elsif ($koodi eq "") {
	  next;
      }
      elsif (($koodi =~ /^[0-9]+[a-z][0-9]+/) && (length($koodi) == 7)) {
          $koodi =~ s#(...[a-z])(...)#$1 $2#;
          print STDERR "Huom! Erotettu kahdeksi signumiksi. " . $pitaja . " r. " . $i . ": " . $vanhkoodi . "\n";

      }
      elsif ($koodi !~ /^[0-9][0-9]*[0-9]*[a-z]*$/) {
	  $koodi = "<error>" . $koodi;
      }
      elsif (length($koodi) == 1) {
	  $koodi = "00" . $koodi;
      }
      elsif (length($koodi) == 2) {
          $koodi = "0" . $koodi;
      }
      elsif (($koodi =~ /^[0-9]+[a-z]*/) && (length($koodi) == 6)) {
          $vanhkoodi = $koodi;
          $koodi =~ s#(...)(...)#$1 $2#;
          print STDERR "Huom! Erotettu kahdeksi signumiksi. " . $pitaja . " r. " . $i . ": " . $vanhkoodi . "\n";
      }
      elsif (($koodi =~ /^[0-9]+[a-z]/) && (length($koodi) == 7)) {
          $vanhkoodi = $koodi;
          $koodi =~ s#(...)(...[a-z])#$1 $2#;
          print STDERR "Huom! Erotettu kahdeksi signumiksi. " . $pitaja . " r. " . $i . ": " . $vanhkoodi . "\n";
      }
      elsif (($koodi =~ /[+,E]/) || ($koodi !~ /^[0-9][0-9][0-9][a-z]*$/)) {
	  $koodi = "<error>" . $koodi;
      }
      $korjatutSignumit = $korjatutSignumit . " " . $koodi;
    }

    $rivi =~ s#^([^\t]*\t[^\t]*\t)[^\t]*(\t.*\n)$#$1$korjatutSignumit$2#;

    $signumit = $rivi;
    $signumit = $korjatutSignumit;

    #$lokaatiot = $rivi;
    #$lokaatiot =~ s#^[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t([^\t]*)\t.*\n$#$1#;
    #$lokaatiot =~ s#SKN ([0-9]+)#SKN:$1#;
    #@lokLista = split(/ /, $lokaatiot);

    #$uudetLokaatiot = "";

    #for ($j = 0; $j < @lokLista; ++$j) {
    #    $koodi = $lokLista[$j];
    #
#	if ($koodi eq "") {
	#    next;
	#}
        #elsif ($koodi =~ /^(SKN[:][0-9]+)|([-])$/) {
        #    print "";
	#}
	#elsif ($koodi !~ /^[0-9][0-9]*[0-9]*[a-z]*$/) {
	#    $koodi = "<error>" . $koodi;
	#}
	#elsif (length($koodi) == 1) {
	#    $koodi = "00" . $koodi;
        #}
        #elsif (length($koodi) == 2) {
	#  $koodi = "0" . $koodi;
        #} 
	#elsif (($koodi =~ /[+,E]/) || ($koodi !~ /^[0-9][0-9][0-9][a-z]*$/)) {
	#    $koodi = "<error>" . $koodi;
	#}
        #else {
	 #   $uudetLokaatiot = $uudetLokaatiot . $koodi . " ";
            #if ($signumit !~ m/$koodi( |$)/) {
            #  $rivi =~ s#^([^\t]*\t[^\t]*\t[^\t]*)(\t.*\n)$#$1 $koodi$2#;
	    #}
        #}
    #}

    #$rivi =~ s#^([^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t)[^\t]*(\t.*\n)$#$1$uudetLokaatiot$2#;

    $signumit = $rivi;
    $signumit =~ s#^[^\t]*\t[^\t]*\t([^\t]*)\t.*\n$#$1#;
    $signumit =~ s#^[ ]+##;

    @sigLista = split(/ /, $signumit);

    $sortatut = "";

    foreach(sort @sigLista) {
      $sortatut = $sortatut . $_ . " ";   
    }

    #@locLista = split(/ /, $uudetLokaatiot);
    #$sortatutLokaatiot = "";

    #foreach(sort @locLista) {
    #  $sortatutLokaatiot = $sortatutLokaatiot . $_ . " ";
    #}

    $rivi =~ s#^([^\t]*\t[^\t]*\t)[^\t]*(\t.*\n)$#$1$sortatut$2#;

    #$rivi =~ s#^([^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t)[^\t]*(\t.*\n)$#$1$sortatutLokaatiot$2#;

    #print "ss" . $sortatut . "\n";

    # Loppuviilaus:

    $rivi =~ s#[ ]+# #g;
    $rivi =~ s#([^ ])=#$1 =#g;
    $rivi =~ s#=([^ ])#= $1#g;

    $rivi =~ s#([^ ])\]#$1 ]#g;
    $rivi =~ s#\]([^ ])#] $1#g;

    $rivi =~ s#([^ ])\[#$1 [#g;
    $rivi =~ s#\[([^ ])#[ $1#g;

    $rivi =~ s#(\t| )[(]([^ ]+)[)] #$1( $2 ) #g;
    $rivi =~ s#[ ]+\t#\t#g;

    if ($rivi =~ /<tarkista>/) {
	print STDERR "Tarkista rivi " . $i . "!\n";
    }

    print $rivi;
}
