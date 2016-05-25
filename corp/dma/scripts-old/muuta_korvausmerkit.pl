#!/usr/bin/perl

# Poistaa search-kentän korvausmerkit tai muuttaa ne oikeinkirjoituksen mukaiseksi.

@rivit = <STDIN>;

for ($i = 0; $i < @rivit; ++$i) {
    $rivi = $rivit[$i];
    $rivi =~ s#\r##;
    $rivi =~ s#\t\t\t#\t-\t-\t#g;
    $rivi =~ s#\t\t#\t-\t#g;
    $rivi =~ s#\cK##g;
    $vali = chr(0xA0);
    $rivi =~ s#$vali# #g;
    $vali = chr(2026);
    $rivi =~ s#$vali#...#g;
    #$rivi =~ s#\x(00A0)# #g;
    #$rivi =~ s#\x(2026)#...#g;

    $rivi =~ s#Yli-ii#Yli-Ii#g;

    # Muuta SKN-muotoilut:
    $rivi =~ s#SKN ([0-9]+) s[.] [0-9]+#SKN $1#g;
    $rivi =~ s#SKN ([0-9]+) - [0-9]+#SKN $1#g;
    $rivi =~ s#SKNA ([0-9]+)#SKNA:$1#g;
    $rivi =~ s#SKNA [?]##g;
    $ekaSarake = $rivi;
    $ekaSarake =~ s#^([^\t]+)\t.*\n#$1#;
    $rivinAlku = $rivi;
    $rivinAlku =~ s#^(.+\t.+\t.+\t.+\t.+\t.+)\t.+\n$#$1#;

    $rivinLoppu = $rivi;
    $rivinLoppu =~ s#^.+\t.+\t.+\t.+\t.+\t.+\t(.+)\n$#$1#;
 
    if ($rivi !~ /^.+\t.+\t.+\t.+\t.+\t.+\t.+\n$/) {
	print STDERR "Virhe rivillä " . $i . ": " . $rivi;
        next;
    }

    # Käsitellään korvausmerkit:
    $rivinLoppu =~ s#\^##g;
    $rivinLoppu =~ s#/##g;
    $rivinLoppu =~ s#\\##g;
    $rivinLoppu =~ s#{##g;
    $rivinLoppu =~ s#}##g;
    $rivinLoppu =~ s#~##g;
    $rivinLoppu =~ s#[|]##g;

    $rivinLoppu =~ s#£#ä#g;
    $rivinLoppu =~ s#å#o#g;
    $rivinLoppu =~ s#%#ö#g;
    $rivinLoppu =~ s#§#t#g;
    $rivinLoppu =~ s#\$#t#g;
    $rivinLoppu =~ s#é#e#g;
    $rivinLoppu =~ s#ô#o#g;
    $rivinLoppu =~ s#ê#e#g;
    $rivinLoppu =~ s#î#i#g;
    $rivinLoppu =~ s#û#u#g;

    $rivinLoppu =~ s/##/ng/g;
    $rivinLoppu =~ s/#/n/g;

    # &-merkin kässittely?

    print $rivinAlku . "\t" . $rivinLoppu . "\n";
}
