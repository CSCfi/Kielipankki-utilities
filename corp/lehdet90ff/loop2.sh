rm Hot*.txt &&
sed -i '1 s/^\xef\xbb\xbf//' *.txt && 
for file in *.txt
do
    echo "$file"    
    python3 raw_to_vrt.py "$file" > "$file.VRT"
done
cat *.VRT > all.vrt &&
    rm *.VRT &&
    echo "running sent-fix"
    python3 ~asahala/scripts/vrt_fix_sents.py < all.vrt > all.VRT &&
    echo "running fix-attrs"
    python /v/korp/scripts/vrt-fix-attrs.py --encode-special-chars=all < all.VRT > all.fix


