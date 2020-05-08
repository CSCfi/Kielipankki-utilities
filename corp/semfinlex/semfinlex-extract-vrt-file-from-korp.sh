# On korp server, extract the vrt file from cwb data:

/v/korp/scripts/cwbdata2vrt-simple.sh --all --force --omit-log-comment --omit-attribute-comment --output-file /var/tmp/semfinlex_asd_fi_2018.VRT semfinlex_asd_fi_2018

# Then remove link elements as this is a one-language corpus:

cat semfinlex_asd_fi_2018.VRT | perl -pe 's/^<link .*\n//; s/^<\/link>\n//;' > semfinlex_asd_fi_2018.VRT.nolinks

# Fix element order in the vrt file, i.e. cases such as
# 
# <paragraph id="46" type="heading">
# <sentence id="54" n="54">
# <link id="1">
# <section id="1" title="1 §">
# 1
# §
# </section>
# </link>
# </sentence>
# </paragraph>

cat semfinlex_asd_fi_2018.VRT.nolinks | \
perl -pe 's/\n/¤/g;' | \
perl -pe 's/>¤</></g;' | \
perl -pe 's/¤/\n/g;' | \
perl -pe 's/(<paragraph[^>]*>)(<sentence[^>]*>)(<section[^>]*>)/\3\1\2/;' | \
perl -pe 's/<\/section><\/sentence><\/paragraph>/<\/sentence><\/paragraph><\/section>/;' | \
perl -pe 's/></>\n</g;' > semfinlex_asd_fi_2018.VRT.nolinks.fixed

# Fix double spaces in section titles:

cat semfinlex_asd_fi_2018.VRT.nolinks.fixed | perl -pe 's/  / /g;' > semfinlex_asd_fi_2018.VRT.nolinks.fixed.fixed

