#!/usr/bin/perl

# Käsitellään erikoistapaukset.

@rivit = <STDIN>;

for ($i = 1; $i < @rivit; ++$i) {
    $rivi = $rivit[$i];
    if ($rivi =~ /<ERROR: 8d_Savitaipale_390/) {
      print "8d\tSavitaipale\t390\t8d_Savitaipale_390-397.pdf\r\n";
      print "8d\tSavitaipale\t391\t8d_Savitaipale_390-397.pdf\r\n";
      print "8d\tSavitaipale\t392\t8d_Savitaipale_390-397.pdf\r\n";
      print "8d\tSavitaipale\t393\t8d_Savitaipale_390-397.pdf\r\n";
      print "8d\tSavitaipale\t394\t8d_Savitaipale_390-397.pdf\r\n";
      print "8d\tSavitaipale\t395\t8d_Savitaipale_390-397.pdf\r\n";
      print "8d\tSavitaipale\t396\t8d_Savitaipale_390-397.pdf\r\n";
      print "8d\tSavitaipale\t397\t8d_Savitaipale_390-397.pdf\r\n";
    }
    else {
      print $rivi;
    }
}

