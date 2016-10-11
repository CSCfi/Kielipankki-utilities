for file in *.txt.utf
do
 # do something on "$file"
 echo "$file"
 python3 iclfi_fix.py "$file" >> loki.txt
done
