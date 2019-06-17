#!/bin/sh

perl -pe 'use open qw(:std :utf8); s/(.)/\1\n/g;' | sort | uniq -c | sort -nr
