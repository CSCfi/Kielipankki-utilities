# bash this in vrt-tools

set -o errtrace pipefail

(
    ./hrt-from-txt |
	./hrt-tokenize-udpipe |
	./vrt-udpipe
) <<EOF
Tämän hetken Ylen uutissivulta poimittua:

Älykaiuttimilla on joskus myös ihmiskorvat – laitteiden tallenteita
kuunnellaan puheohjelmien kehittämiseksi

Esimerkiksi verkkokauppa Amazonilla on tuhansia työntekijöitä
tarkastamassa puhekäskyjä noudattavan Alexa-ohjelman tallenteita,
kirjoittaa uutissivusto Bloomberg.
EOF

echo 

./hrt-udpipe <<EOF
Tämän hetken Ylen uutissivulta poimittua:

Älykaiuttimilla on joskus myös ihmiskorvat – laitteiden tallenteita
kuunnellaan puheohjelmien kehittämiseksi

Esimerkiksi verkkokauppa Amazonilla on tuhansia työntekijöitä
tarkastamassa puhekäskyjä noudattavan Alexa-ohjelman tallenteita,
kirjoittaa uutissivusto Bloomberg.
EOF
