# bash this in vrt-tools

set -o errtrace pipefail

(
    ./hrt-from-txt |
	./hrt-tokenize-tr |
	./vrt-tdp-alpha-lookup |
	./vrt-tdp-alpha-marmot |
	./vrt-tdp-alpha-fillup |
	./vrt-tdp-alpha-parse --quiet |
	./vrt-drop --dots
) <<EOF
Ihminen on valloittanut avaruuden .

Eihän nyt metrinen avaruus voi olla kovin iso .
EOF
