for file in *.txt
do
 # do something on "$file"
 echo "$file"
 iconv -f iso-8859-1 -t UTF-8 "$file" > "$file.utf"
done
