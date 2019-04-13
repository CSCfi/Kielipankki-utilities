# bash this in vrt-tools

set -o errtrace pipefail

(
    ./vrt-name --number 3 --position 2=the-word |
	./vrt-rename --map v3=v8 |
	./vrt-rename --map v1=id --map v8=next_word_id |
	./vrt-rename --map the-word=word |
	./vrt-keep --name word --rest |
	./vrt-rename --map next_word_id=next.word.id |
	./vrt-drop --name id |
	./vrt-drop --dots
) <<EOF
<text>
<paragraph>
<sentence>
1	x	2
2	y	3
3	z	0
</sentence>
</paragraph>
</text>
EOF
