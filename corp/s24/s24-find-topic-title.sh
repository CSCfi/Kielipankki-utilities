#! /bin/sh

# s24-find-topic-title.sh
#
# Find the title (name) for a topic number: find a thread with that
# topic number in its topic (hierarhcy) list in the VRT (attribute
# text_topics), retrieve the HTML for that thread from Suomi24 and
# extract the topic title from it.
#
# Usage: s24-find-topic-title.sh topic_num [input_vrt ...]
#
# Output: topic_num <tab> topic_title
#
# If input_vrt is not specified, read from stdin.


if [ "x$1" = x ]; then
    echo "Usage: s24-find-topic-title.sh topic_num [input_vrt ...]" \
	 > /dev/stderr
    exit 1
fi

topic_num=$1
shift

topic_title=DUMMY
try_threads=10

round=1

topic_title=
while [ $round -le $try_threads ] && [ "x$topic_title" = x ]; do

    thread_topic_level=$(
	perl -ne '
	    if (/^<text.*topics="((?:[0-9]+,)*'$topic_num'(?:,[0-9]+)*)"/) {
	        $count++;
		if ($count < '$round') {
		    next;
		}
		@topics = split (",", $1);
		for ($level = 0; $level <= $#topics; $level++) {
		    last if ($topics[$level] == '$topic_num');
		}
		# The topic numbers are listed from bottom up, but return
		# level number so that the topmost level is 1.
		$level = $#topics - $level + 1;
		($thread) = /thread="(.*?)"/;
		print "$thread $level\n";
		exit;
	    }
	' "$@"
    )

    if [ "x$thread_topic_level" = x ]; then
	echo "Threads with topic $topic_num not found" > /dev/stderr
	exit 1
    fi

    thread=${thread_topic_level% *}
    topic_level=${thread_topic_level#* }

    logfile=$TMPDIR/$$.wget.log

    topic_title=$(
	wget -O - -o $logfile 'https://keskustelu.suomi24.fi/t/'$thread'/' |
	    grep '<a property="item" typeof="WebPage"' |
	    grep -v '>Keskustelu24<' |
	    head -n$topic_level |
	    tail -1 |
	    sed -e 's/.*<span property="name">//; s/<\/span>.*//;'
    )
    # echo $round $thread $topic_level $topic_title
    round=$(($round + 1))
done

if [ "x$topic_title" = x ]; then
    echo "Error retrieving threads topic $topic_num (tried $try_threads threads):" \
	 > /dev/stderr
    echo "Wget log output for the last thread $thread:" > /dev/stderr
    cat $logfile > /dev/stderr
    exit 1
fi
rm -f $logfile

printf "$topic_num\t$topic_title\n"
