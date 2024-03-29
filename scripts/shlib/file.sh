# -*- coding: utf-8 -*-

# shlib/file.sh
#
# Generic library functions for Bourne shell scripts: file processing
#
# NOTE: Some functions require Bash. Some functions use "local", which
# is not POSIX but supported by dash, ash.


# Load shlib components for the functions used
shlib_required_libs="msgs"
. $_shlibdir/loadlibs.sh


find_existing_dir () {
    _test=$1
    _file=$2
    shift 2
    for dir in "$@"; do
	if [ $_test $dir/$_file ]; then
	    echo $dir
	    break
	fi
    done
}

# find_dir_with_file file dir [dir ...]
#
# Find a directory under one of dir containing file. The printed
# directory is the first one found by find. Follows symbolic links.
find_dir_with_file () {
    local file path
    file=$1
    shift
    path=$(find -L "$@" -name "$file" 2> /dev/null | head -1)
    if [ "$path" != "" ]; then
        echo "${path%/*}"
    fi
}

find_filegroup () {
    filegroup=
    for grp in $@; do
	if groups 2> /dev/null | grep -qw $grp; then
	    filegroup=$grp
	    break
	fi
    done
    if [ "x$filegroup" = x ]; then
	filegroup=`groups 2> /dev/null | cut -d' ' -f1`
    fi
}

find_prog () {
    # If --no-path is specified, do not try to find the program on
    # $PATH but only in argument directories. Otherwise, try to find
    # the program on $PATH at the position marked with "@" in the
    # argument directory list, or if the arguments do not contain a
    # "@", after any argument directories.
    if [ "x$1" = "x--no-path" ]; then
	shift
    else
	set -- "$@" @
    fi
    _prog=$1
    shift
    for _dir in "$@"; do
	if [ "$_dir" = @ ]; then
	    _path=`which "$_prog" 2> /dev/null`
	    if [ "x$_path" != "x" ]; then
		echo "$_path"
		return 0
	    fi
	elif [ -x "$_dir/$_prog" ]; then
	    echo "$_dir/$_prog"
	    return 0
	fi
    done
    return 1
}

test_file () {
    _test=$1
    _file=$2
    _not_found_cmd=$3
    shift 3
    if [ $_test "$_file" ]; then
	return 0
    else
	$_not_found_cmd "$@"
	return 1
    fi
}


ensure_perms () {
    chgrp -R $filegroup "$@" 2> /dev/null
    chmod -R $fileperms "$@" 2> /dev/null
    return 0
}

# mkdir_perms dir [dir ...]
#
# Create the directories dir and ensure that they have the desired
# permissions ($filegroup and $fileperms).
mkdir_perms () {
    if mkdir -p "$@"; then
	ensure_perms "$@"
    else
	return $?;
    fi
}


comprcat () {
    if [ "x$1" = "x--tar-args" ]; then
	_comprcat_tar_args=$2
	shift 2
    fi
    if [ "x$1" = "x--files" ]; then
	_comprcat_tar_args="$_comprcat_tar_args --wildcards $2"
	_comprcat_unzip_args="$2"
	shift 2
    fi
    if [ "x$1" = x ]; then
	cat
    else
	for fname in "$@"; do
	    if [ ! -r "$fname" ]; then
		error "Unable to read input file: $fname"
	    fi
	    case "$fname" in
		*.bz2 )
		    bzcat "$fname"
		    ;;
		*.gz )
		    zcat "$fname"
		    ;;
		*.xz )
		    xzcat "$fname"
		    ;;
		*.tar | *.tar.[bgx]z | *.tar.bz2 | *.t[bgx]z | *.tbz2 )
		    tar -xaOf "$fname" $_comprcat_tar_args
		    ;;
		*.zip )
		    unzip -p "$fname" $_comprcat_unzip_args
		    ;;
		* )
		    cat "$fname"
		    ;;
	    esac
	done
    fi
}


# test_compr_file [-test] file_basename
#
# Return the result of [ -test file ] for the file_basename, or if
# that is false, try file_basename suffixed with .gz, .bz2 and .xz. If
# they all return false, return false. The default test is -e.
test_compr_file () {
    local test basename compr_exts ext
    compr_exts='.gz .bz2 .xz'
    test=-e
    if [ "x$2" != x ]; then
	test=$1
	shift
    fi
    basename=$1
    [ $test "$basename" ] && return 0
    for ext in $compr_exts; do
	[ $test "$basename$ext" ] && return 0
    done
    return 1
}


calc_gib () {
    awk 'BEGIN { printf "%0.3f", '$1' / 1024 / 1024 / 1024 }'
}

get_filesize () {
    ls -l "$1" | awk '{print $5}'
}

# replace_file [--backup backup_file] old_file new_file
#
# Safely replace old_file with new_file. If --backup is specified,
# rename old_file as backup_file.
#
# TODO: Allow numbered backups
replace_file () {
    local oldfile newfile bakfile backup
    backup=
    if [ "x$1" = "x--backup" ]; then
	backup=1
	bakfile=$2
	shift 2
    fi
    oldfile=$1
    newfile=$2
    if [ "x$bakfile" = x ]; then
	bakfile=$oldfile.old
    fi
    if [ ! -r "$oldfile" ]; then
	error "Cannot read file: $oldfile"
    fi
    {
	mv -f "$oldfile" "$bakfile" &&
	mv -f "$newfile" "$oldfile"
    }
    if [ "$?" = 0 ]; then
	if [ "x$backup" = x ]; then
	    rm "$bakfile"
	fi
    else
	# If the old file was removed, replace it with the backup file
	if [ ! -e "$oldfile" ] && [ -e "$bakfile" ]; then
	    mv -f "$bakfile" "$oldfile"
	fi
	error "Could not replace file $oldfile with $newfile"
    fi
}


# file_newer file1 file2 [...]
#
# Return true (0) if file1 is newer than file2 or any other of the
# files specified as arguments, or if the other files do not exist.
# (If file1 does not exist, return 1.) Return 2 if fewer than 2
# arguments were given.
file_newer () {
    local file1 file
    file1=$1
    shift
    if [ "$1" = "" ]; then
        return 2
    fi
    for file in "$@"; do
        if [ ! "$file1" -nt "$file" ]; then
            return 1
        fi
    done
    return 0
}


# Initialize variables

# File permissions used by ensure_perms
fileperms=ug+rwX,o+rX

find_filegroup $default_filegroups
