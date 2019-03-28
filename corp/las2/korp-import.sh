

for CNAME in las2_esseet_s2 las2_esseet_v las2_tentit_s2 las2_tentit_v ; do
    echo $CNAME
    cat las2/$CNAME/*.vrt | /proj/clarin/korp/scripts/korp-make --input-fields "lemma pos msd fun com" $CNAME
done