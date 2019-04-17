#!/usr/bin/perl

# Separate each word (including punctuation) on its own line.

use strict;
use warnings;
use open qw(:std :utf8);

foreach my $line ( <STDIN> ) {

    unless ( $line =~ /^</)
    {	
	# escape dots in special cases, e.g. "(1.1.-31.12.)." or "(tanssit. maist.);"
	$line =~ s/\.\)\./¤\.¤\)\./g;
	$line =~ s/\.\)\;/¤\.¤\)\;/g;

	# separate parentheses () and []
	$line =~ s/([^ ])\(/$1 \(/g;
	$line =~ s/\)([^ ])/\) $1/g;
	$line =~ s/([^ ])\[/$1 \[/g;
	$line =~ s/\]([^ ])/\] $1/g;

	# strange punctuation in some files:
	$line =~ s/\; ?\;/\;/g;

	# escape &amp; &quot; &apos; &lt; &gt;
	$line =~ s/\&((amp)|(quot)|(apos)|(lt)|(gt))\;/\&$1¤/g;
	# , ; and : at the end of a word or line is separated
	$line =~ s/(,|\;|:) / $1 /g;
	$line =~ s/(,|\;|:)$/ $1/;
	# unescape &amp; &quot; &apos; &lt; &gt;
	$line =~ s/\&((amp)|(quot)|(apos)|(lt)|(gt))¤/\&$1\;/g;

	# escape some common abbreviations that end in dot and do not (ever?) end a sentence: . -> ¤.¤
	$line =~ s/ esim\./ esim¤\.¤/g;
	$line =~ s/ v\./ v¤\.¤/g;
	$line =~ s/ t\. ?ex\./ t¤\.¤ex¤\.¤/g; # almost always written together: "t.ex."
	$line =~ s/Vt\./Vt¤\.¤/g;
	$line =~ s/Tf\./Tf¤\.¤/g;
	# and abbreviations in capital letters, e.g. 'C.G.E. Mannerheim' or 'J. K. Paasikivi'
	# (must be done twice for overlapping matches)
	$line =~ s/(\p{Upper})\. ?(\p{Upper})/$1¤\.¤ $2/g;
	$line =~ s/(\p{Upper})\. ?(\p{Upper})/$1¤\.¤ $2/g;
	# as well as .. and ... used for missing text or sometimes in tables
	$line =~ s/\.\.(\.?)/¤\.\.$1¤/g;

	# . at the end of a word (followed by space and capital letter or opening parenthesis) or line is separated
	$line =~ s/(.)\. (\p{Upper}|\(|\[)/$1 \. $2/g;
	$line =~ s/\. *$/ \./;
	# .) and .] are handled later

	# separate content inside parentheses from parentheses
	$line =~ s/\(([^\)]+)\)/\( $1 \)/g;
	$line =~ s/\[([^\]]+)\]/\[ $1 \]/g;

	# handle .) and .] that were just separated
	$line =~ s/\. \)/ \.\)/g;
	$line =~ s/\. \]/ \.\]/g;

	# unescape escaped dots
	$line =~ s/¤(\.+)¤/$1/g;

	# separate hyphen, n dash, m dash and horizontal bar in numerical ranges and dates (e.g. 250-300; 1.2.-5.2.)
	$line =~ s/([0-9\.])(\-|\x{2013}|\x{2014}|\x{2015})([0-9])/$1 $2 $3/g;
	# and single-symbol ranges (e.g. ' 250-300 henkeä '; ' alakohdissa a-c mainitut ')
	$line =~ s/( [^ ])(\-|\x{2013}|\x{2014}|\x{2015})([^ ] )/$1 $2 $3/g;

	# separate slash unless surrounded by numerals
	$line =~ s/([^0-9])\/([^0-9])/$1 \/ $2/g;
	
	# separate double quotes
	$line =~ s/"/ " /g;
	
	# previous replacements might have generated too many spaces
	$line =~ s/ +/ /g;
	
	# each word/punctuation on its own line
	$line =~ s/^ +//g;
	$line =~ s/ +$//g;
	$line =~ s/ /\n/g;
    }
    
    print $line;

}
