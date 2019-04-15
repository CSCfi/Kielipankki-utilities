# bash this in vrt-tools

set -o errtrace pipefail

(
    ./hrt-from-txt |
	./hrt-tokenize-tr |
	./vrt-sparv-huntag |
	./vrt-sparv-swemalt |
	./vrt-sparv-cstlemma
) <<EOF
Härifrån tvättas det ! Av man !

Såsom det nu blev .
EOF
