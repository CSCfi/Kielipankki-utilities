# bash this in vrt-tools

# In addition to vrt-simple-tear | ... | vrt-conll09-mend
# exercise vrt-report-tree-shape-issues; successful output
# is only a TSV header line and nothing more.

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
    ./vrt-tdp-alpha-lookup |
    ./vrt-tdp-alpha-marmot |
    ./vrt-tdp-alpha-fillup |
    ./vrt-tdp-alpha-parse --quiet |
    ./vrt-conll09-mend |
    ./vrt-report-tree-shape-issues --multi
