#!/bin/sh

for file in asd/*/*/*.xml kko/*/*/*.xml kho/*/*/*.xml
do
    echo $file
    sed "s/\xc2\x82/é/g; s/Ã\xc2\x96/Ö/g; s/Â\xc2\x96/-/g; s/\xc2\x96/-/g; s/\xc2\x92/'/g; s/\xc2\x8fÅ/Å/g; s/\xc2\x8f/Å/g; s/\xc2\x94//g; s/\xc2\x91/'/g; s/\xc2\x8e/Ä/g; s/Â\xc2\x97/-/g; s/\xc2\x85/à/g;" $file > tmp;
    mv tmp $file
done

sed -i 's/Ã¤/ä/g;' asd/sv/1992/asd19920149.xml
