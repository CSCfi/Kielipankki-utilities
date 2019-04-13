# bash this in vrt-tools

set -o errtrace pipefail

(
    cat <<EOF
<!-- #vrt positional-attributes: word -->
<text>
<paragraph>
<sentence>
EOF
    for k in {1..30}
    do
	# not _quite_ what Kari Aronpuro wrote
	for w in ei tikka tapa eikä ämpäri kuku
	do
	    echo $w
	done
    done
    cat <<EOF
</sentence>
</paragraph>
</text>
EOF
) | ./vrt-simple-tear |
    ./vrt-simple-mend

(
    cat <<EOF
<!-- #vrt positional-attributes: word -->
<text>
<paragraph>
<sentence>
EOF
    for k in {1..30}
    do
	# not _quite_ what Kari Aronpuro wrote
	for w in ei tikka tapa eikä ämpäri kuku
	do
	    echo $w
	done
    done
    cat <<EOF
</sentence>
</paragraph>
</text>
EOF
) | ./vrt-simple-tear |
    ./vrt-tdp-alpha-lookup |
    ./vrt-tdp-alpha-marmot |
    ./vrt-tdp-alpha-fillup |
    ./vrt-tdp-alpha-parse --quiet |
    ./vrt-conll09-mend |
    ./vrt-drop --dots --name feat
