#! /bin/sh

# Calculate the absolute and relative frequencies of the values of a
# single positional attribute in a corpus or a group of corpora.


progname=`basename $0`
progdir=`dirname $0`

usage_header="Usage: $progname [options] corpus_id ... > output.tsv

Calculate the absolute and relative frequencies of the values of a single
positional attribute in a corpus or a group of corpora, based on the data
stored in CWB.

The output is in three-column tab-separated format: attribute value, absolute
frequency, relative frequency per million tokens.

The corpus ids specified may contain shell wildcards that are expanded."

optspecs='
attribute=ATTR "word" attr
    calculate the frequencies of the positional attribute ATTR
v|verbose
    output progress information to stderr
'

. $progdir/korp-lib.sh

# Process options
eval "$optinfo_opt_handler"


if [ "x$1" = x ]; then
    error "Please specify corpora"
fi

corpora=$(list_corpora "$@")

tokencnt=0

for corp in $corpora; do
    corpus_tokencnt=$(get_corpus_token_count $corp)
    echo_verb "Processing corpus $corp ($corpus_tokencnt tokens)" >> /dev/stderr
    $cwb_bindir/cwb-lexdecode -P $attr -f -s -b $corp > $tmp_prefix.$corp.tsv
    if [ "$?" = 0 ]; then
	tokencnt=$((tokencnt + $corpus_tokencnt))
    fi
done
echo_verb "In total $tokencnt tokens" >> /dev/stderr

echo_verb "Combining results and sorting" >> /dev/stderr

for corp in $corpora; do
    cat $tmp_prefix.$corp.tsv
done |
LC_ALL=C sort -k2,2 |
awk 'function print_line (token, freq) {
         printf "%s\t%d\t%.2f\n", token, freq, freq / tokencnt * 1e6
     }
     BEGIN { tokencnt = '"$tokencnt"' }
     {
         if (prev && $2 != prev) {
             print_line(prev, freq)
             freq = 0
         }
         prev = $2
         freq += $1
     }
     END { print_line(prev, freq) }' |
decode_special_chars |
sort -k2,2nr -s
