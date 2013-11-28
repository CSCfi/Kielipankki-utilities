#! /bin/sh
# -*- coding: utf-8 -*-


progname=`basename $0`

begin_string=
end_string=


usage () {
    cat <<EOF
Usage: $progname [options] [--] file ...
Concatenate argument files, each surrounded by a leading and trailing string

Options:
  --help        show this help
  --begin STRING, --file-begin STRING
                add STRING at the beginning of each file
  --end STRING, --file-end STRING
		add STRING at the end of each file

The option argument STRING may contain C-style character escapes (\n, \t, ...).
A newline is added at the end of STRING.
The following references in STRING are expanded:
  {filename}   the name of the file as given as argument
  {basename}   the name of the file without directory part
  {dirname}    the directory part of the file name
EOF
    exit 0
}

# Test if GNU getopt
getopt -T > /dev/null
if [ $? -eq 4 ] ; then
    # This requires GNU getopt
    args=`getopt -o "h" -l "help,file-begin:,begin:,file-end:,end:" -- "$@"`
    if [ $? -ne 0 ] ; then
	exit 1
    fi
    eval set -- "$args"
fi
# If not GNU getopt, arguments of long options must be separated from
# the option string by a space; getopt allows an equals sign.

# Process options
while [ "x$1" != "x" ] ; do
    case "$1" in
	-h | --help )
	    usage
	    ;;
	--begin | --file-begin )
	    shift
	    begin_string="$1\n"
	    ;;
	--end | --file-end )
	    shift
	    end_string="$1\n"
	    ;;
	-- )
	    shift
	    break
	    ;;
	--* )
	    echo "$0: Unrecognized option: $1" > /dev/stderr
	    ;;
	* )
	    break
	    ;;
    esac
    shift
done

expand_and_print () {
    printf "$@" |
    sed -e "s@{filename}@$filename@g; s@{basename}@$basename@g; s@{dirname}@$dirname@g;"
}

for filename in "$@"; do
    basename=`basename "$filename"`
    dirname=`dirname "$filename"`
    expand_and_print "$begin_string"
    cat $filename
    expand_and_print "$end_string"
done
