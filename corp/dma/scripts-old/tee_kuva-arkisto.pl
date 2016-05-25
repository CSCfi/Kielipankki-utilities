#!/usr/bin/perl

@rivit = <STDIN>;

for ($i = 1; $i < @rivit; ++$i) {
    $rivi = $rivit[$i];
    $rivi =~ s#^[ ]*##;
    $rivi =~ s#[ ]*$##;
    $rivi =~ s#\r##;
    $rivi =~ s#\n##;
  
    if (($rivi !~ /^[0-9][a-z]*_/) || ($rivi =~ /[.]zip/)) {
	next;
    }

    $murrealue = $rivi;
    $murrealue =~ s#^([0-9][a-z]*)_.*#$1#;
    
    $pitaja = $rivi;
    $pitaja =~ s#^[^_]+_([^_]+)_.*#$1#;

    $signum = $rivi;
    $signum =~ s#^[^_]+_[^_]+_([^.]+).*#$1#;
   
    if ($signum =~ /^[a-zöä]+$/) {
	next;
    }
    elsif ($signum !~ /^[0-9][0-9][0-9][a-z]*$/) {
	print "<ERROR: " . $rivi . ">\n";
        next;
    }

    $tdsto = $rivi;

    print $murrealue . "\t" . $pitaja . "\t" . $signum . "\t" . $tdsto . "\r\n";
}

