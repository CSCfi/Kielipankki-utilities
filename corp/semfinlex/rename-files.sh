#!/bin/sh

# Rename some files in asd/ and kko/ so that they will be left out
# by scripts that compile the packages.

# empty files
mv asd/fi/1994/asd19940635.xml asd/fi/1994/asd19940635.xml.empty
mv asd/fi/2010/asd20000001.xml asd/fi/2010/asd20000001.xml.empty

# duplicates (e.g. asd/fi/1734/asd17340001000.xml is equivalent to asd/fi/1734/asd17340001.xml)
# (also asd/fi/1906/asd19070006001.xml is equivalent to asd/fi/1907/asd19070006.xml)
for file in \
    asd/fi/1734/asd17340001000.xml \
    asd/fi/1734/asd17340003000.xml \
    asd/fi/1734/asd17340004000.xml \
    asd/fi/1868/asd18680031000.xml \
    asd/fi/1889/asd18890039001.xml \
    asd/fi/1895/asd18950037001.xml \
    asd/fi/1896/asd18960037000.xml \
    asd/fi/1898/asd18980034001.xml \
    asd/fi/1901/asd19010015001.xml \
    asd/fi/1901/asd19010034001.xml \
    asd/fi/1906/asd19060026001.xml \
    asd/fi/1906/asd19070006001.xml \
    asd/fi/1919/asd19190001001.xml \
    asd/fi/1919/asd19190094001.xml \
    asd/fi/1919/asd19190122001.xml;
do
    mv $file $file.duplicate
done

# Swedish text and only short summary in Finnish
for file in \
    kko/fi/1980/kko19800021t.xml \
    kko/fi/1980/kko19800032t.xml \
    kko/fi/1980/kko19800093t.xml \
    kko/fi/1981/kko19810017t.xml \
    kko/fi/1981/kko19810028t.xml \
    kko/fi/1981/kko19810053t.xml \
    kko/fi/1981/kko19810085t.xml \
    kko/fi/1982/kko19820056t.xml \
    kko/fi/1982/kko19820062t.xml \
    kko/fi/1982/kko19820095t.xml \
    kko/fi/1982/kko19820117t.xml \
    kko/fi/1982/kko19820183t.xml \
    kko/fi/1983/kko19830103t.xml \
    kko/fi/1983/kko19830111t.xml \
    kko/fi/1983/kko19830121t.xml \
    kko/fi/1983/kko19830148t.xml \
    kko/fi/1983/kko19830169t.xml \
    kko/fi/1983/kko19830186t.xml \
    kko/fi/1983/kko19830193t.xml \
    kko/fi/1984/kko19840010t.xml \
    kko/fi/1984/kko19840051t.xml \
    kko/fi/1984/kko19840117t.xml \
    kko/fi/1984/kko19840119t.xml \
    kko/fi/1984/kko19840144t.xml \
    kko/fi/1984/kko19840221t.xml \
    kko/fi/1985/kko19850063t.xml \
    kko/fi/1985/kko19850102t.xml \
    kko/fi/1985/kko19850161t.xml \
    kko/fi/1985/kko19850174t.xml \
    kko/fi/1986/kko19860002t.xml \
    kko/fi/1986/kko19860013t.xml \
    kko/fi/1986/kko19860051t.xml \
    kko/fi/1986/kko19860129t.xml \
    kko/fi/1987/kko19870008.xml \
    kko/fi/1987/kko19870032.xml \
    kko/fi/1987/kko19870034.xml \
    kko/fi/1987/kko19870039.xml \
    kko/fi/1987/kko19870040.xml \
    kko/fi/1987/kko19870061.xml;
do
    mv $file $file.swedish
done

# files that do not pass the scripts (todo: fix the scripts)
# asd/fi/1992/asd19920123.xml # many xml tags on one line
# asd/sv/1992/asd19921607.xml # many xml tags on one line
# asd/fi/1996/asd19960460.xml # many xml tags on one line
# asd/fi/1996/asd19960477.xml # many xml tags on one line
# kho/fi/2018/kho201801629.xml # missing <p>
for file in \
    asd/fi/1992/asd19920123.xml \
    asd/sv/1992/asd19921607.xml \
    asd/fi/1996/asd19960460.xml \
    asd/fi/1996/asd19960477.xml \
    kho/fi/2018/kho201801629.xml;
do
    mv $file $file.error
done

# <saa:Osa> inside <saa:Pykala>, rename to *.error or
# fix manually
#
# asd/fi/1968/asd19680360.xml
# asd/fi/1974/asd19741043.xml
# asd/fi/1988/asd19881240.xml
# asd/fi/1992/asd19921535.xml
# asd/fi/2006/asd20060624.xml
# asd/fi/2007/asd20070503.xml
# asd/fi/2011/asd20110621.xml
# asd/fi/2013/asd20130421.xml
# asd/fi/2015/asd20150487.xml
#
# asd/sv/1974/asd19741043.xml
# asd/sv/1988/asd19881240.xml
# asd/sv/2006/asd20060624.xml
# asd/sv/2007/asd20070503.xml
# asd/sv/2011/asd20110621.xml
# asd/sv/2013/asd20130421.xml
# asd/sv/2015/asd20150487.xml

# contain "&#9;"s, fix manually
#
# asd/fi/1999/asd19991341.xml
#
# asd/sv/1991/asd19911444.xml
# asd/sv/1999/asd19991063.xml
# asd/sv/1999/asd19991070.xml
