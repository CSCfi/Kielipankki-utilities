#! /bin/sh


special_chars=" /<>|"
encoded_special_char_offset=0x7F
encoded_special_char_prefix=


decode_special_chars () {
    perl -C -e '
	$sp_chars = "'"$special_chars"'";
	%sp_char_map = map {("'$encoded_special_char_prefix'"
	                     . chr ('$encoded_special_char_offset' + $_))
			    => substr ($sp_chars, $_, 1)}
			   (0 .. length ($sp_chars));
	while (<>)
	{
	    for $c (keys (%sp_char_map))
	    {
		s/$c/$sp_char_map{$c}/g;
	    }
	    print;
	}'
}

make_lemgrams_tsv () {
    corpname=$1
    corpname_u=`echo $corpname | sed 's/.*/\U&\E/'`
    shift
    if [ "$#" != "0" ]; then
	cat "$@"
    else
	cat
    fi |
    grep -Ev '^<' |
    awk -F'	' '{print $NF}' |
    tr '|' '\n' |
    grep -Ev '^$' |
    decode_special_chars |
    sort |
    uniq -c |
    perl -pe 's/^\s*(\d+)\s*(.*)/$2\t$1\t0\t0\t'$corpname_u'/'
}

make_lemgrams_tsv "$@"
