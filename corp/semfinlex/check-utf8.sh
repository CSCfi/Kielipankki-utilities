for dir in "asd/fi" "asd/sv" "kko/fi" "kko/sv" "kho/fi" "kho/sv"
do
    echo "Checking that files in directory "$dir" are UTF-8, printing files that are not:"
    file $dir/*/*.xml | grep -v 'XML 1.0 document, UTF-8 Unicode text'
done
