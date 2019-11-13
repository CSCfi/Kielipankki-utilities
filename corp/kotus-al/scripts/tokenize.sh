#!/bin/bash
#use the combined converted xml as input
    
echo "remove line-breaking hyphens and page numbers"
../../../../../tokenizer/vrt-dehype ../results/all_result_clean.xml > ../vrt/all_result_dehyped.vrt

echo "tokenize"
../../../../../tokenizer/vrt-tokenize ../vrt/all_result_dehyped.vrt > ../vrt/all_result_tokenized.vrt

echo "validate"
../../../../../tokenizer/vrt-validate ../vrt/all_result_tokenized.vrt &&

echo "remove temporary files"
rm ../vrt/all_result_dehyped.vrt

rm ../results/all_result_clean.xml

