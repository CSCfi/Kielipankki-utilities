Date: Mon, 24 Apr 2017 13:03:07 +0000
From: A J Aleksi Sahala
To: Jyrki Niemi
Subject: S24-skriptejä

[...]

1) s24_checknew.py (Python 2)
Tämä skripti kokeilee API:sta kuinka paljon uutta materiaalia sinne on
tullut viimeisen päivityksen jälkeen. Tämän skriptin ´newest´
-muuttuja pitää päivittää käsin vastaamaan API:n sivumäärää aina kun
uusi päivityssetti on haettu.

2) s24_collect.py (Python 2)
Tämä on haravointiskripti, joka ajetaan ´python collect.py [start]
[end]´, jossa [start] ja [end] määrittävät sen, miltä väliltä data
haetaan. Koska API pävittyy lopusta alkuun päin, 0 on aina uusin
datasivu. Tässä tapauksessa haluatte hakea varmaan puuttuvan uusimman
datan, eli silloin arvoiksi tulee 0 ja se luku, minkä s24_checknew.py
antaa, esim. ´python collect.py 0 1405´

API on todella hidas ja epävakaa, eli datan hakemiseen voi helposti
vierähtää kymmeniä tunteja. Skriptejä voi ajaa rinnakkainkin (esim.
useammassa putty-terminaalissa) jos haluaa tavaraa ulos nopeammin.
Skripti tallentaa oletusarvoisesti JSONeja tietyin välein, ts. jos
yhteys katkeaa tai API kaatuu, tiedostonimistä voi päätellä mistä
kohti hakua täytyy jatkaa.

3) s24_json2vrt.py (Python 3)
Muuntaa API:n antaman JSONin VRT-muotoon (Korpin ja jäsentimien lukema
muoto). Tämä ajetaan ´python3 s24conv.py [input.json]´ ja se tuottaa
saman nimisen VRT-filen. Tämä skripti vaatii toimiakseen
vrt_tools.py:n joka on mukana. Skriptissä on pari purkkaviritelmää
jotka on pitänyt korjata pitkään, mutta sen pitäisi toimia.
Virkkeistinkään ei ole missään tapauksessa paras mahdollinen, mutta
hoitaa homman ihan hyvin "nettikielelle".
