#!/usr/bin/perl

# Etsii sy�tevirrasta per�kk�iset tietueet, joissa on identtinen text-kentt� ja tulostaa ne rivinalkuisen <dupl>-koodin kera. Lis�ksi ohjelma tulostaa
# virhevirtaan (stderr) tiedot riveist�, joilla on duplikaatteja.

@rivit = <STDIN>;

for ($i = 0; $i < @rivit; ++$i) {
  $rivi = $rivit[$i];

  if ($i >= (@rivit - 1)) {
      next;
  }
 
  $pitaja = $rivi;
  $pitaja =~ s#^([^\t]*\t[^\t]*)\t.*\n#$1#;
  $pitaja =~ s#\t# #g;

  $text1 = $rivi;
  $text2 = $rivit[$i + 1];
  $text1 =~ s#^[^\t]*\t[^\t]*\t[^\t]*\t([^\t]*)\t.*\n#$1#;
  $text2 =~ s#^[^\t]*\t[^\t]*\t[^\t]*\t([^\t]*)\t.*\n#$1#;
 
  if ($text1 eq $text2) {
      print STDERR "Duplikaatti: " . $pitaja . ", r. " . ($i + 1) . " - " . ($i + 1) . "\n";
      print "<dupl>" . $rivi;  
  }
  else {
      print $rivi;
  }
}
