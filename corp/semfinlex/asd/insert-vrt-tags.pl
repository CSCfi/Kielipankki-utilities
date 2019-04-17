#!/usr/bin/perl

# Mark parts of document:
#
#  <saa:Osa> as <part>
#  <saa:Luku> as <chapter>
#  <saa:Pykala> as <section>
#
# Also mark paragraphs (can be optional) and sentence boundaries.

use strict;
use warnings;
use open qw(:std :utf8);

my $before = "";
my $after = "";

while (<>) {

    ## PARTS
    if (/^<saa:Osa saa1:identifiointiTunnus="([^"]*)">/)
    {
	my $osa_id = $1;
	# Finnish: OSA, OSASTO, Osa, Osasto, osa, osasto
	$osa_id =~ s/(((O|o)sa(sto)?)|(OSA(STO)?))\.?//g;
	# Swedish: DEL, AVDELNINGEN, AVDELNING, Avdelning, Avdelningen, avdelning, avdelningen
	$osa_id =~ s/(AVDELNING(EN)?|(A|a)vdelning(en)?)\.?//;
	$osa_id =~ s/DEL//;

	# e.g. " II A " -> "II_A"
	$osa_id =~ s/^ +//;
	$osa_id =~ s/ +$//;
	$osa_id =~ s/ /_/g;

	if ( $osa_id eq "" ) { $osa_id = "EMPTY"; }

	$before = join('','<<part id="',$osa_id,'">>',"\n");
    }
    elsif (/^<\/saa:Osa>/) { $after = "<</part>>\n"; }

    ## CHAPTERS
    # <saa:Luku saa1:identifiointiTunnus="6 luku">
    # <saa:Luku saa1:identifiointiTunnus="">
    # 2 LUKU (31.3.1879/12)
    # "Kiinteistövarallisuuden hallinta ja hoito"
    elsif (/^<saa:Luku saa1:identifiointiTunnus="([^"]*)">/)
    {
	my $luku_id = $1;
	if ($luku_id =~ /([0-9]+( [a-z] )?)/)
	{
	    $luku_id = $1;
	    $luku_id =~ s/ //g;
	}
	elsif ($luku_id =~ /([IVX]+)/)
	{
	    $luku_id = $1;
	}
	else
	{
	    $luku_id = "EMPTY";
	}
	print join('','<<chapter id="',$luku_id,'">>',"\n");
    }
    elsif (/^<saa:Luku>/)
    {
	$before = join('','<<chapter id="EMPTY"',">>\n");
    }
    elsif (/^<\/saa:Luku>/) { $after = "<</chapter>>\n"; }

    ## SECTIONS    
    # <saa:Pykala saa1:pykalaLuokitusKoodi="VoimaantuloPykala" saa1:identifiointiTunnus="27 §.">
    # <saa:Pykala saa1:pykalaLuokitusKoodi="Pykala" saa1:identifiointiTunnus="32 §.">
    # <saa:Pykala saa1:identifiointiTunnus="Voimaantulo" saa1:pykalaLuokitusKoodi="VoimaantuloSaannos">
    # <saa:Pykala saa1:pykalaLuokitusKoodi="Pykala">
    # <saa:Pykala>
    elsif (/^<saa:Pykala /)
    {
	if (/saa1:identifiointiTunnus="([^"]+)"/)
	{
	    my $pykala_id = $1;
	    if ($pykala_id =~ /.{12}/)
	    {
		$pykala_id = "EMPTY";
	    }
	    else
	    {
		$pykala_id =~ s/[\.§]//g;
		$pykala_id =~ s/\&amp\;//g; # sometimes this is part of tag
		$pykala_id =~ s/ //g; # e.g. "21 a " -> "21a"
	    }
	    $before = join('','<<section id="',$pykala_id,'"',">>\n");
	}
	else # saa1:identifiointiTunnus has an empty value or is not given at all
	{
	    $before = join('','<<section id="EMPTY"',">>\n");
	}
    }
    elsif (/^<saa:Pykala>/)
    {
	$before = join('','<<section id="EMPTY"',">>\n");
    }
    elsif (/^<\/saa:Pykala>/) { $after = "<</section>>\n"; }

    ## PARAGRAPHS
    # <saa:KohdatMomentti>
    # <saa:SaadosLiite>
    # <saa:SaadosNimeke>
    # <saa:UusiNimeke>
    # <saa:Johtolause>
    # <saa:SaadosValiotsikkoKooste>
    # <saa:SaadosOtsikkoKooste>
    # <asi:SisaltoLiite>
    elsif (/^<saa:KohdatMomentti>/) { $before = join('','<<paragraph type="paragraph">>',"\n"); }
    elsif (/^<\/saa:KohdatMomentti>/) { $after = join('',"<</paragraph>>\n"); }
    elsif (/^<saa:SaadosLiite>/) { $before = join('','<<paragraph type="SAADOSLIITE">>',"\n"); }
    elsif (/^<\/saa:SaadosLiite>/) { $after = join('',"<</paragraph>>\n"); }
    elsif (/^<saa:SaadosNimeke>/) { $before = join('','<<paragraph type="SAADOSNIMEKE">>',"\n"); }
    elsif (/^<\/saa:SaadosNimeke>/) { $after = join('',"<</paragraph>>\n"); }
    elsif (/^<saa:UusiNimeke>/) { $before = join('','<<paragraph type="UUSI_NIMEKE">>',"\n"); }
    elsif (/^<\/saa:UusiNimeke>/) { $after = join('',"<</paragraph>>\n"); }
    elsif (/^<saa:Johtolause>/) { $before = join('','<<paragraph type="JOHTOLAUSE">>',"\n"); }
    elsif (/^<\/saa:Johtolause>/) { $after = join('',"<</paragraph>>\n"); }
    elsif (/^<saa:Saados(Valiotsikko|Otsikko)Kooste>/) { $before = join('','<<paragraph type="heading">>',"\n"); }
    elsif (/^<\/saa:Saados(Valiotsikko|Otsikko)Kooste>/) { $after = join('',"<</paragraph>>\n"); }
    elsif (/^<asi:SisaltoLiite>/) { $before = join('','<<paragraph type="SISALTOLIITE">>',"\n"); }
    elsif (/^<\/asi:SisaltoLiite>/) { $after = join('',"<</paragraph>>\n"); }

    ## SENTENCES
    # <sis:KappaleKooste>
    # <sis:SaadosKappaleKooste> (can be directly under saa:SaadosOsa)
    # <saa:MomenttiJohdantoKooste>
    # <saa:MomenttiKohtaKooste> (can be directly inside saa:Pykala)
    # <saa:MomenttiAlakohtaKooste>
    # <saa:MomenttiKooste> (can sometimes be inside <saa:KohdatMomentti>)
    # <saa:SaadosNimekeKooste>

    elsif (/^<saa:(Momentti|MomenttiKohta|SaadosKappale|SaadosNimeke)Kooste>/) { $before = join('','<<?paragraph type="paragraph">>',"\n"); }
    elsif (/^<\/saa:(Momentti|MomenttiKohta|SaadosKappale|SaadosNimeke)Kooste>/) { $before = "<>\n"; $after = "<</?paragraph>>\n"; }

    elsif (/^<\/sis:(Saados)?KappaleKooste>/) { $before = "<>\n"; }
    elsif (/^<\/saa:Momentti(Johdanto|Alakohta)Kooste>/) { $before = "<>\n"; }

    print $before;
    $before = "";
    print;
    print $after;
    $after = "";
}
