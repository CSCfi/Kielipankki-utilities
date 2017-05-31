#! /usr/bin/perl -CSD -w
# -*- coding: utf-8 -*-


# Fix a number of minor errors and inconsistencies in the ScotsCorr
# VRT data as converted by Aleksi Sahala. Some of the errors originate
# from the original letters and some have been introduced in the
# conversion process.
#
# Usage: scotscorr-vrt-fix.pl < input.vrt > output.vrt


use feature 'unicode_strings';
use utf8;


# One-off fixes. Here no-break spaces correspond to spaces within
# tokens, whereas normal spaces correspond to token boundaries.
%subst = (
    '{14 de*cember% 1618. \\\\ Send home to s*ir% ro=t= gordoun twa c*on%tractis \\ betuix mcky and Io=n= robsoun w=t= the copie \\ of mcky his dishage {sic}'
    => '14 de*cember% 1618. \\\\ Send home to s*ir% ro=t= gordoun twa c*on%tractis \\ betuix mcky and Io=n= robsoun w=t= the copie \\ of mcky his dishage {sic}',

    '{Cameron: To my lord cardinall of sanctandrois and legait {end}'
    => '{Cameron: To my lord cardinall of sanctandrois and legait} {end}',

    '{Fraser: To my lord and weall beloued husband the Erlle of Eglintoun {end}',
    => '{Fraser: To my lord and weall beloued husband the Erlle of Eglintoun} {end}',

    '{Fraser: To my verie honorable ladye and loving dochter , my Ladye Countess of Eglintoun . {end}'
    => '{Fraser: To my verie honorable ladye and loving dochter , my Ladye Countess of Eglintoun .} {end}',

    '{Fraser: To my verry honnourable lord and lovinge brother my Lord of Eglintoune {end}'
    => '{Fraser: To my verry honnourable lord and lovinge brother my Lord of Eglintoune} {end}',

    '{address> For my Worthey and assurede \\ freandes S=r= Iames Douglas S=r= \\ Archibalde Primrose S=r= William \\ Douglas and David Balfourde of Ballou \\ these {end}'
    => '{address>} For my Worthey and assurede \\ freandes S=r= Iames Douglas S=r= \\ Archibalde Primrose S=r= William \\ Douglas and David Balfourde of Ballou \\ these {end}',

    '{attached to a letter by Sir Robert Gordon of Gordonstoun addressed ‘To my assured \\ freind \\ Cristian forbes \\ spous to doncane \\ forbes burges off \\ Inwernes’ {end}'
    => '{attached to a letter by Sir Robert Gordon of Gordonstoun addressed ‘To my assured \\ freind \\ Cristian forbes \\ spous to doncane \\ forbes burges off \\ Inwernes’} {end}',

    '{<a?s?> {cancelled}' => '{<a?s?> cancelled}',
    '{in margin> Sir {<in margin}' => '{in margin>} Sir {<in margin}',
    '{hand 1>}}' => '{hand 1>}',
    '[<reduced}' => '{<reduced}',
    '{<adjacent}' => '{adjacent>}',

    '{<in Fraser but no longer visible}\\'
    => '{<in Fraser but no longer visible} \\',

    '{address>}For' => '{address>} For',
    '{address>}To' => '{address>} To',
    '{a space vertically}\\\\' => '{a space vertically} \\\\',
    '{centred>}Deare' => '{centred>} Deare',
    '{compressed}\\' => '{compressed} \\',
    '{f2}as' => '{f2} as',
    '{f2}extreme' => '{f2} extreme',
    '{f2}his' => '{f2} his',
    '{f2}with' => '{f2} with',
    '{hand 2>}Bourgy=e=' => '{hand 2>} Bourgy=e=',
    '{intention uncertain}no' => '{intention uncertain} no',
    '{second l unclear}.' => '{second l unclear} .',

    'In{<<I>_extended}' => 'In {<<I> extended}',
    'Lord{a_space_vertically}' => 'Lord {a space vertically}',
    '\\{end}' => '{end}',
    '\\{f2}' => '\\ {f2}',
    'thom?a?s*s%{<reduced}' => 'thom?a?s*s% {<reduced}',
    'w=t={<unclear}' => 'w=t= {<unclear}',
    'yow?{<or_<you>}' => 'yow? {<or <you>}',
    'respect{<character_cancelled}' => 'respect {<character cancelled}',

    '{=increndulous}' => '{=incredulous}',

    '/change of hand>}' => '{change of hand>}',
    );


# Convert underscores to spaces
sub us2sp
{
    my ($s) = @_;
    $s =~ tr/_/ /;
    return $s;
}

# Convert spaces to newlines and no-break spaces to spaces
sub subst_spc
{
    my ($s) = @_;
    $s =~ tr/  / \n/;
    return $s;
}

@text = <>;

for my $line (@text) {
    if ($line =~ /^<text/) {
	# Remove from text attributes remnants of HTML tags
	$line =~ s/&lt;[A-Z]+&gt;//g;
	# Rename attributes srg -> wgr, arg -> agr, lettertypetwo ->
	# lettertype2, scripttypetwo, scripttype2
	$line =~ s/srg="/wgr="/;
	$line =~ s/arg="/agr="/;
	$line =~ s/((?:letter|script)type)two/$1 . "2"/ge;
	# Fix locality East Lothian to Lothian
	$line =~ s/(lcinf=")East (Lothian")/$1$2/;
    }
}

$text = join ("", @text);

# Encode some characters to make substitutions simpler to write; the
# characters are decoded at the end.
$text =~ s/</\001/g;
$text =~ s/>/\002/g;
$text =~ s/"/\003/g;
$text =~ s/ +/ /g;
# $text =~ s/ +/ /g;
# $text =~ s/\n/ /g;
$text =~ s/&lt;/</g;
$text =~ s/&gt;/>/g;
$text =~ s/&quot;/"/g;
$text =~ s/&apos;/'/g;
$text =~ s/&amp;/&/g;

# Convert spaces and no-break spaces in the one-off substitutions
for my $k (keys (%subst)) {
    my $s = subst_spc($subst{$k});
    my $k1 = subst_spc($k);
    $text =~ s/\Q$k1\E/$s/g;
}

# Remove extra closing curly bracket
$text =~ s/^\.\}$/./gm;
# Fix wrong type of opening bracket
$text =~ s/^[\[\(]in\n/{in /gm;
# $text =~ s/^(hand|margin)>}$/{$1>}/gm;
# This fixes errors probably introduced in Aleksi's conversion scripts
$text =~ s/^\\(\{.*?\})/$1/gm;
$text =~ s/^(\{.*?\})/us2sp($1)/gme;

# Remove spurious spaces at the beginning or end of a comment
$text =~ s/^\{=.if.\}/{=if}/gm;
$text =~ s/\{\s+/{/gm;
$text =~ s/(\{<)\s+/$1/gm;
$text =~ s/\s+(>?})/$1/gm;
# Also convert to lower case
$text =~ s/{= *([^a-z]+?)}/\L{=$1}\E/gm;
# Remove remnants of HTML tags
$text =~ s/<[A-Z]+>$//gm;

# Decode characters encoded above
# $text =~ s/ +/\n/g;
# $text =~ s/ +/ /g;
$text =~ s/&/&amp;/g;
$text =~ s/'/&apos;/g;
$text =~ s/"/&quot;/g;
$text =~ s/</&lt;/g;
$text =~ s/>/&gt;/g;
$text =~ s/\003/"/g;
$text =~ s/\002/>/g;
$text =~ s/\001/</g;

print $text;
