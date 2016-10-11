for file in *.txt.utf
do
 # do something on "$file"
 echo "$file"
 python3 icl_vrt.py "$file" t
done
