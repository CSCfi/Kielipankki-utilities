#!/bin/sh
touch lang && for dir in *; do echo $dir && grep 'lang="' $dir/*/*/*mets.xml >> lang; done
perl -pe 's/^.*xml\:lang="([^"]*)".*$/\1/;'
sort langs | uniq -c | sort -nr
