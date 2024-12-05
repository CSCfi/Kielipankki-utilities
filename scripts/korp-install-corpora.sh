#! /bin/bash
# -*- coding: utf-8 -*-

# Install Korp corpora of the latest corpora package

# TODO:
# - Multiple or timestamped backups
# - Backup to a different backup directory
# - Verbosity control


progname=`basename $0`
progdir=`dirname $0`


usage_header="Usage: $progname [options] corpus|package ...

Install or update the specified corpora from corpus packages to Corpus
Workbench and Korp database.

The arguments may be either corpus package file names, possibly with a full
path name, or corpus names, in which case packages for the corpus are searched
for in the package directory. A full path name may be preceded by a remote
host name and a colon, in which case the package is retrieved from the remote
host without a need to make a local copy of the package file."

optspecs='
c|corpus-root=DIR "$corpus_root"
    use DIR as the root directory of corpus files (CORPUS_ROOT)
p|package-dir=DIR "CORPUS_ROOT/$pkgsubdir" pkgdir
    DIR is the default directory in which to search for corpus
    packages to be installed; may be a remote directory specified as
    HOST:DIR
no-backups !backups
    do not make backup copies of existing corpus files
backup-suffix=SUFFIX ".bak"
    use SUFFIX as the backup file suffix
f|force
    force installing a corpus package that is older than or as old as
    the currently installed package
database-import=MODE db_import
    when to import database data (other than authorization data)
    included in the corpus packages to be installed: MODE is one of
    the following: "delay" (after extracting all corpus packages),
    "immediate" (immediately after extracting each corpus), "later"
    (on a later run of '"$progname"'), or "no" (do not import at all
    nor extract database files from corpus packages); note that
    authorization data is always imported immediately (default:
    "delay")
immediate-database-import immediate_import
    DEPRECATED: use --database-import=immediate instead
load-limit=LIMIT "$num_cpus"
    install corpus data only if the CPU load is below LIMIT (a
    positive integer); otherwise wait for the load to decrease;
    checked before each corpus package and database table file
n|dry-run
    only report corpus packages that would be installed, but do not
    actually install them
times
    show timestamps and the time used for installing individual corpus
    packages and database files and the whole process
'

usage_footer="Note: The backup copy of a corpus is overwritten by subsequent updates of the
corpus."


pkgsubdir=pkgs


. $progdir/korp-lib.sh


# The number of CPUs (cores) for the --load-limit default to be shown
# in the usage message, even if it does not seem to be set the default
num_cpus=$(get_num_cpus)

# Process options
eval "$optinfo_opt_handler"

# Validate and set --database-import option value
case "$db_import" in
    delay | immediate | later | no )
        if [ "x$immediate_import" != x ]; then
            error "--immediate-database-import is deprecated and conflicts with --database-import=$db_import"
        fi
        ;;
    "" )
        # Default value
        if [ "x$immediate_import" != x ]; then
            warn "--immediate-database-import is deprecated: use --database-import=immediate instead"
            db_import=immediate
        else
            db_import=delay
        fi
        ;;
    * )
        error '--database-import argument value must be one of "delay", "immediate", "later" or "no"'
        ;;
esac

# By default, extract all database files from corpus package
extract_dbfiles="*"
# With --database-import=no, extract only authorization files
if [ "$db_import" = no ]; then
    # "CORPUS" will be replaced with the actual corpus id
    extract_dbfiles="*/CORPUS_auth_*"
fi

# Set the default for --load-limit if empty
if [ "x$load_limit" = x ]; then
    load_limit=$num_cpus
fi

# This is only for compatibility with older corpus packages
pkg_prefix=korpdata_

# $filelistfile needs to be an absolute path as it is also accessed
# from the corpus root when ensuring the permissions of the extracted
# files (listed in $filelistfile)
filelistfile=$(realpath $tmp_prefix.files)
pkglistfile=$tmp_prefix.pkgs

timestamp_format="+%Y-%m-%dT%H:%M:%S"

# The order in which database tables should be imported
# Always installed immediately after extracting package
dbtable_install_order_immediate="auth_.*"
# Installed only after extracting all packages unless
# --immediate-database-import
dbtable_install_order="timedata(_date)? lemgrams .*"


if [ "x$1" = x ]; then
    error "Please specify the names of corpus packages or corpora to install.
For more information, run '$0 --help'."
fi

dry_run_msg=
if [ "x$dry_run" != x ]; then
    dry_run_msg=" (dry run)"
fi

if [ "x$pkgdir" = "xCORPUS_ROOT/$pkgsubdir" ]; then
    pkgdir=${CORPUS_PKGDIR:-$corpus_root/$pkgsubdir}
fi

localhost=LOCALHOST
default_pkghost=$localhost
case $pkgdir in
    *:* )
	default_pkghost=${pkgdir%%:*}
	pkgdir=${pkgdir#*:}
	;;
esac

installed_list=$corpus_root/korp_installed_corpora.list
install_state_dir=$corpus_root/korp-install-corpora

if [ ! -e "$installed_list" ]; then
    touch "$installed_list"
    ensure_perms "$installed_list"
fi

if [ ! -e "$install_state_dir" ]; then
    mkdir -p "$install_state_dir"
    ensure_perms "$install_state_dir"
fi

dbfile_list_prefix=$install_state_dir/dbfile_queue-

install_only_dbfiles_corpora=

# Non-empty if database files need to be installed at the end
install_dbfiles=

# If not --times, use empty TIMEFORMAT not to print times.
# This requires Bash; does not work on Dash.
if [ "x$times" != x ]; then
    TIMEFORMAT="[Elapsed %E, user %U, system %S]"
else
    TIMEFORMAT=
fi


timestamp () {
    if [ "x$times" != x ]; then
        date +'[%F %T]'
    fi
}

wait_for_low_load () {
    local load load_int wait_min
    # Dry run regardless of CPU load
    if [ "x$dry_run" != x ]; then
        return
    fi
    load=$(get_cpu_load)
    load_int=$(integer $load)
    while [ "$load_int" -ge "$load_limit" ] &&
              [ "$load" != "$load_limit.00" ];
    do
        # Heuristic for how long to wait based on the load and limit
        # TODO: Take into account whether the load is increasing or
        # decreasing
        wait_min=$(($load_int / $load_limit * 2))
        echo "CPU load $load exceeds the limit $load_limit; waiting $wait_min minutes for the load to decrease"
        sleep $(($wait_min * 60))
        load=$(get_cpu_load)
        load_int=$(integer $load)
    done
}

make_dbfile_list_filename () {
    local corp
    corp=$1
    echo "$dbfile_list_prefix$corp.list"
}

host_is_remote () {
    test "x$1" != x$localhost && test "x$1" != x
}

get_package_corpus_name () {
    local corpname
    corpname=${1##*/}
    corpname=${corpname%.t?z}
    corpname=${corpname%.tar.*}
    case "$1" in
	"$pkgprefix*" )
            corpname=${corpname##$pkgprefix}
            ;;
	* )
	    corpname=${corpname%_korp_20*}
	    ;;
    esac
    echo "$corpname"
}

run_command () {
    if host_is_remote "$1"; then
	# ssh may not read anything from stdin, so that higher-level
	# read works; see https://unix.stackexchange.com/a/107801
	ssh "$1" "$2" < /dev/null
    else
	eval "$2"
    fi
}

make_pkgname_cond () {
    # Output package name condition for find for the package base
    # names listed as arguments
    local name suff suffs result
    suffs="t\?z tar.\*"
    result=
    for name in "$@"; do
        for suff in $suffs; do
            if [ "x$result" != x ]; then
                result="$result -o"
            fi
            result="$result -name $name.$suff"
        done
    done
    safe_echo "$result"
}

find_corpus_packages () {
    local pkgspec pkghost use_find current_pkgdir pkgname_cond ls_cmd cmd \
	  mode links owner group size timestamp pkgname
    pkgspec=$1
    pkghost=$default_pkghost
    use_find=1
    current_pkgdir=$pkgdir
    case $pkgspec in
	*:* )
	    pkghost=${pkgspec%%:*}
	    pkgspec=${pkgspec#*:}
	    ;;
    esac
    # TODO: If $pkgspec is a directory, find packages in it and its
    # subdirectories
    case $pkgspec in
	*/*.* )
	    use_find=
	    ;;
	*/* )
	    current_pkgdir=$pkgspec
	    pkgname_cond=$(make_pkgname_cond "\*_korp_20\*" "$pkg_prefix\*")
	    ;;
	*.* )
	    pkgname_cond="-name $pkgspec"
	    ;;
	* )
	    pkgname_cond=$(
                make_pkgname_cond "${pkgspec}_korp_20\*" "$pkg_prefix$pkgspec")
	    ;;
    esac
    # Use -v "natural sort of (version) numbers" of GNU ls to use the
    # latest package by the timestamp in the package name, as the
    # timestamp of the file may have changed e.g. in copying.
    ls_cmd="ls -lvr --time-style=$timestamp_format --dereference"
    if [ "x$use_find" = x ]; then
	cmd="$ls_cmd $pkgdir/$pkgspec $pkgspec 2> /dev/null"
    else
	cmd="find $current_pkgdir $maxdepth_opt $pkgname_cond | xargs --no-run-if-empty $ls_cmd"
    fi
    run_command "$pkghost" "$cmd" |
    while read mode links owner group size timestamp pkgname; do
	printf "%s\t%s\t%s\t%s\t%s\n" $(get_package_corpus_name $pkgname) \
	     $pkghost "$pkgname" $timestamp $size
    done
}

find_package_candidates () {
    local listfile
    listfile=$1
    shift
    touch $listfile
    for pkgspec in "$@"; do
	find_corpus_packages "$pkgspec" > $listfile.tmp
	if [ -s $listfile.tmp ]; then
	    grep -Fvx -f$listfile < $listfile.tmp >> $listfile
	else
	    warn "No matching corpus packages found: $pkgspec"
	fi
    done
}

format_package_name_host () {
    if host_is_remote "$2"; then
	printf $2:
    fi
    printf "%s\n" $1
}

# Output the numeric suffix of the file name given as the argument:
# the suffix is preceded by a hyphen and may consist of 1 to 4 digits,
# possibly with leading zeros. If the file name has no suffix, output
# "0".
get_suffix () {
    local suffix
    # Separate suffix from base file name
    suffix=${1##*-}
    if [ "$suffix" = "$1" ]; then
        # If no suffix, default to 0
        suffix=0
    else
        # Remove up to three possible leading zeros from suffix to
        # avoid printf error "invalid octal number"
        suffix=${suffix#0}
        suffix=${suffix#0}
        suffix=${suffix#0}
        # A suffix containing only zeros may have been emptied
        # completely, so restore it to 0 (although printf "%d" ""
        # would also print "0")
        if [ "x$suffix" = x ]; then
            suffix=0
        fi
    fi
    echo "$suffix"
}

# Get package date with the possible running number suffix of up to
# 9999.
get_package_name_date () {
    local date suffix
    date=$1
    # Remove everything up to and including "_korp_"
    date=${date##*_korp_}
    # Remove extension(s)
    date=${date%%.*}
    # Extract suffix
    suffix=$(get_suffix "$date")
    # Remove suffix from date
    date=${date%-*}
    # Remove possible "after" date (update package)
    date=${date%%_a_*}
    if [ "${date%%_*}" = "$date" ]; then
        # If date contains no time (after an underscore), assume
        # 00:00:00
        date=${date}000000
    else
        # Remove underscore to allow numerical comparison
        date=${date/_/}
    fi
    printf "%s%04d" "$date" "$suffix"
}

# Output the "after" date of the update package file name given as the
# argument.
get_update_package_after_date () {
    # Make update package name look like full package name by removing
    # the first date and time (between "_korp_" and "_a_") and use
    # get_package_name_date to get the "after" date.
    get_package_name_date "${1/_korp_*_*_a_/_korp_}"
}

package_is_not_newer () {
    [ "$(get_package_name_date $1)" -le "$(get_package_name_date $2)" ]
}

# Return true if the package name given as the argument is an update
# package, recognized from the occurrence of "_korp_20*_a_20" in the
# file name.
is_update_package () {
    [ "${1%_korp_20*_a_20*}" != "$1" ]
}

# Sort input with package names expected to be in the third
# tab-separated field on each line, with optional preceding sorting
# options specified in the first argument. Transform package names to
# get the desired order: descending dates (sort -Vr), full packages
# before update packages with the same date and time (convert "_" to
# "!" in "_a_"), packages with an -xx suffix before those without one
# (corresponding to -00; convert "." to "*"), and (older) packages
# with only date after packages with the same date and explicit time
# (corresponding to time 000000; "-" and "*" precede "_" in reversed
# order).
sort_packages () {
    local presort
    presort=$1
    sed -e 's/_\(a_........_......\.\)/!\1/' |
        tr '.' '*' |
        sort -t"$tab" -s $presort -k3,3Vr |
        tr '!*' '_.'
}

# Given the following input (and installed) package dates, function
# filter_corpora should output the names of the packages 4, 3 and 1,
# in this order. Older packages are installed first, so that possible
# changes in newer ones override.
#
#   0 installed: 20241029_151515
#   1 update: 20241031_121010_a_20241030_202020
#   2 update: 20241031_101010_a_20241030_202020
#   3 update: 20241030_202020_a_20241030_101010
#   4 full: 20241030_101010
#   5 update: 20241030_101010_a_20241029_151515
#
# 5 is not output, since a full package (4) should always contain the
# files in an update package with the same base date. 2 is not output
# as it has the same "after" date as 1 but is older than 1.

filter_corpora () {
    local listfile corpname_prev corp_pkgfile corp_pkgs pkg_info \
	  corpname pkghost pkgfile timestamp pkgsize installed_pkg \
	  formatted_pkgname not_newer_msg after_date after_date2
    listfile=$1
    corpname_prev=
    corp_pkgfile=
    # Info lines for packages to install for the current corpus
    corp_pkgs=
    # global corpora_to_install
    corpora_to_install=
    # Sort packages first by corpus name (is it needed?), then by
    # package name
    sort_packages -k1,1 < $listfile > $listfile.srt
    # We cannot read from a pipeline because the values of the
    # variables would not be retained.
    while read corpname pkghost pkgfile timestamp pkgsize; do
        pkg_info="$corpname$tab$pkghost$tab$pkgfile$tab$timestamp$tab$pkgsize"
	if [ "$corpname" != "$corpname_prev" ]; then
            # Different corpus than for the previously checked package
            # (or the first package): the most recent package for this
            # corpus
            # The "after" date of an update package, empty for full
            # packages; if non-empty, check further packages for this
            # corpus
            after_date=
            # Output possible packages for the previous corpus
            if [ "x$corp_pkgs" != x ]; then
                safe_echo "$corp_pkgs"
            fi
            corp_pkgs=
            # sort_packages works here, too, as the package name is
            # the third field in the list of installed corpora
	    installed_pkg=$(
                grep -E "^[^$tab]+$tab$corpname$tab" $installed_list |
                    sort_packages |
		    head -1 |
		    cut -d"$tab" -f3)
	    corpname_prev=$corpname
	    if package_is_not_newer "$pkgfile" "$installed_pkg"; then
		formatted_pkgname="$(format_package_name_host $pkgfile $pkghost)"
		not_newer_msg="not newer than the installed package ($installed_pkg)"
		if [ "x$force" != x ]; then
		    echo "  $corpname: installing $formatted_pkgname because of --force, even though $not_newer_msg" >> /dev/stderr
		else
                    if [ -s $(make_dbfile_list_filename $corpname) ]; then
                        if [ "$db_import" = "delay" ] ||
                               [ "$db_import" = "immediate" ];
                        then
                            echo "  $corpname: $formatted_pkgname already installed but importing the database files not yet imported" >> /dev/stderr
                            install_only_dbfiles_corpora="$install_only_dbfiles_corpora $corpname"
                        else
                            echo "  $corpname: $formatted_pkgname already installed but has database files not yet imported; not importing them because of --database-import=$db_import" >> /dev/stderr
                        fi
                    else
		        echo "  $corpname: skipping $formatted_pkgname as $not_newer_msg" >> /dev/stderr
                    fi
		    continue
		fi
	    fi
	    corp_pkgs="$pkg_info"
	    corpora_to_install="$corpora_to_install $corpname"
	    corp_pkgfile=$pkgfile
            if is_update_package "$pkgfile"; then
                after_date=$(get_update_package_after_date "$pkgfile")
            fi
	elif [ "x$after_date" != x ]; then
            # The previous candidate checked for this corpus was an
            # update package
            if package_is_not_newer "$pkgfile" "$installed_pkg"; then
                # If the installed package is newer than this, no need
                # to check the rest of the packages for this corpus
                after_date=
            else
                if is_update_package "$pkgfile"; then
                    # If this is an update package with an "after"
                    # date same as (or later than, but that should not
                    # be possible) the previous one, skip this
                    after_date2=$(get_update_package_after_date "$pkgfile")
                    if [ "$after_date2" -ge "$after_date" ]; then
                        continue
                    fi
                    after_date=$after_date2
                else
                    # No need to check older full packages for this
                    # corpus
                    after_date=
                fi
                # Prepend package info to $corp_pkgs to install older
                # packages first (before updates)
                corp_pkgs="$pkg_info$nl$corp_pkgs"
            fi
        else
            :
            # TODO: Show this only with --verbose
            # echo "  $corpname: skipping $pkgfile as older than $corp_pkgfile" >> /dev/stderr
        fi
    done < $listfile.srt
    if [ "x$corp_pkgs" != x ]; then
        safe_echo "$corp_pkgs"
    fi
}

get_tar_compress_opt () {
    case "$1" in
	*.gz | *.tgz )
	    echo --gzip
	    ;;
	*.tbz | *.bz | *.bz2 )
	    echo --bzip2
	    ;;
	*.xz | *.txz )
	    echo --xz
	    ;;
    esac
}

backup_corpus () {
    local pkgname pkghost tar_cmd backup_msg_shown
    pkgname=$1
    pkghost=$2
    echo "  Checking for existing corpus files"
    tar_cmd="tar tf $pkgname $(get_tar_compress_opt $pkgname) \
            --wildcards --wildcards-match-slash \
	    --transform 's,.*/\(data\|registry\|sql\)/,\1/,' \
	    --show-transformed-names '*/data' '*/registry' '*/sql' 2> /dev/null"
    backup_msg_shown=
    run_command "$pkghost" "$tar_cmd" |
    cut -d/ -f1,2 |
    sort -u |
    while read fname; do
	if [ -e $corpus_root/$fname ]; then
	    if [ "x$backup_msg_shown" = x ]; then
		echo "  Backing up existing corpus files"
		backup_msg_shown=1
	    fi
	    cp -dpr $corpus_root/$fname $corpus_root/$fname$backup_suffix
	    ensure_perms $corpus_root/$fname$backup_suffix
	fi
    done
}

human_readable_size () {
    local kb
    kb=$(($1 / 1024))
    if [ "$kb" -lt 10240 ]; then
	echo "$kb KiB"
    else
	echo "$(($kb / 1024)) MiB"
    fi
}

# Return the size of a file in a human-readable format
filesize () {
    human_readable_size $(du -bs $1 | cut -f1)
}

adjust_registry () {
    local filelistfile regfile corpus_id datadir
    # This assumes that the target datadir is
    # $corpus_root/data/$corpus_id
    filelistfile=$1
    grep registry/ $filelistfile |
    while read regfile_base; do
	regfile=$corpus_root/$regfile_base
	corpus_id=${regfile_base##*/}
	datadir=$(echo "$regfile" | sed -e 's,/registry/,/data/,')
	if ! grep -E -ql $corpus_root $regfile 2> /dev/null; then
	    mv $regfile $regfile.orig
	    sed -e "s,^HOME .*,HOME $datadir," \
                -e "s,^INFO .*/\.info,INFO $datadir/.info," \
		$regfile.orig > $regfile
	    touch --reference=$regfile.orig $regfile
	    ensure_perms $regfile
	    rm $regfile.orig
	fi
    done
}

install_file_sql () {
    local sqlfile db
    sqlfile=$1
    db=$korpdb
    case $sqlfile in
	*_auth_* )
	    db=$korpdb_auth
	    ;;
    esac
    comprcat $sqlfile \
	| mysql $mysql_opts $db
    return $?
}

install_file_tsv () {
    local tsvfile
    tsvfile=$1
    $progdir/korp-mysql-import.sh --prepare-tables $tsvfile
    return $?
}

install_dbfiles () {
    local type msg corp tables_re listfile files file retval
    type=$1
    msg=$2
    corp=$3
    tables_re=$4
    if [ "x$tables_re" = x ]; then
        tables_re=".*"
    fi
    listfile=$(make_dbfile_list_filename $corp)
    if [ ! -e $listfile ]; then
        return
    fi
    files=$(grep -E '_'"$tables_re"'\.'$type'(\.(bz2|gz|xz))?$' $listfile)
    if [ "x$files" != "x" ]; then
	echo "  $msg data into MySQL database$dry_run_msg"
	for file in $files; do
            timestamp
	    echo "    $file (size `filesize $corpus_root/$file`)"
            if [ "x$dry_run" = x ]; then
                wait_for_low_load
	        time install_file_$type "$corpus_root/$file" \
                     > $tmp_prefix.install.out 2>&1
                retval=$?
                indent_input 6 < $tmp_prefix.install.out
	        if [ $retval -ne 0 ]; then
		    error "Errors in loading $file"
                else
                    grep -Fv "$file" $listfile > $listfile.new
                    replace_file $listfile $listfile.new
                    ensure_perms $listfile
	        fi
            fi
	done
    fi
    if [ ! -s $listfile ]; then
        rm $listfile
    fi
}

install_db () {
    local corp tables_re
    corp=$1
    tables_re=$2
    install_dbfiles sql Loading $corp "$tables_re"
    install_dbfiles tsv Importing $corp "$tables_re"
}

install_corpora_dbtables () {
    local install_fn corpora dbtable_order tables_re
    install_fn=$1
    corpora=$2
    dbtable_order=$3
    # The * and ? in $dbtable_order should not be expanded
    set -o noglob
    for tables_re in $dbtable_order; do
	$install_fn "$corpora" "$tables_re"
    done
    set +o noglob
}

install_corpus () {
    local corp corpus_pkg pkgtime pkgsize pkghost install_base_msg tables_re \
          update dbfile_list_file extract_dbfiles_expanded
    corp=$1
    corpus_pkg=$2
    pkgtime=$3
    pkgsize=$4
    pkghost=$5
    update=
    if is_update_package $corpus_pkg; then
        update=" (update)"
    fi
    install_base_msg="$corp$update from $(format_package_name_host $corpus_pkg $pkghost) (compressed size $(human_readable_size $pkgsize))"
    echo
    if [ "x$dry_run" != x ]; then
	echo "Would install $install_base_msg (dry run)"
	return
    fi
    timestamp
    echo "Installing $install_base_msg"
    wait_for_low_load
    if [ "x$backups" != x ]; then
	backup_corpus $corpus_pkg $pkghost
    fi
    # Replace "CORPUS" with the actual corpus id
    extract_dbfiles_expanded=${extract_dbfiles/CORPUS/$corp}
    echo "  Copying CWB files"
    time run_command "$pkghost" "cat '$corpus_pkg'" |
    tar xvp -C $corpus_root -f- $(get_tar_compress_opt $corpus_pkg) \
	--wildcards --wildcards-match-slash \
	--transform 's,.*/\(data\|registry\|sql\)/,\1/,' \
	--show-transformed-names \
        '*/data' '*/registry' "*/sql/$extract_dbfiles_expanded" 2>&1 \
	| tee $filelistfile \
	| sed -e 's/^/    /'
    # Allow missing directories
    if grep '^tar:' $filelistfile > $tmp_prefix.tar_errors; then
	if grep -E -q -v \
	    '(Not found|Cannot (utime|change mode)|Exiting with failure)' \
	    $tmp_prefix.tar_errors;
	then
	    error "Errors in extracting $corpus_pkg"
	else
	    warn "Ignoring non-fatal extraction errors"
	fi
    fi
    (
	cd $corpus_root
	ensure_perms $(cat $filelistfile)
    )
    adjust_registry $filelistfile
    dbfile_list_file=$(make_dbfile_list_filename $corp)
    grep -E '\.(sql|tsv)(\.(bz2|gz|xz))?$' $filelistfile > "$dbfile_list_file"
    install_corpora_dbtables install_db $corp "$dbtable_install_order_immediate"
    # Log to the list of installed corpora: current time, corpus name,
    # package file name, package file modification time, installing
    # user
    printf "%s\t%s\t%s\t%s\t%s\n" \
	$(date "$timestamp_format") $corp $(basename "$corpus_pkg") \
	$pkgtime $(whoami) >> $installed_list
    if [ "$db_import" = "no" ]; then
        echo "  (Not installing database files because of --database-import=no)"
    elif [ -s "$dbfile_list_file" ]; then
        if [ "$db_import" = "delay" ]; then
            echo "  (Installing (the rest of) the database files after extracting all packages)"
            install_dbfiles=1
        elif [ "$db_import" = "later" ]; then
            echo "  (Marking (the rest of) the database files to be installed on a later run)"
        else
            install_corpora_dbtables install_db $corp "$dbtable_install_order"
        fi
    fi
}

install_corpora_db () {
    local corpora tables_re
    corpora=$1
    tables_re=$2
    if [ "x$install_only_dbfiles_corpora" != x ]; then
        install_corpora_db_aux "$install_only_dbfiles_corpora" "$tables_re"
    fi
    if [ "x$install_dbfiles" != x ]; then
        install_corpora_db_aux "$corpora" "$tables_re"
    fi
}

install_corpora_db_aux () {
    local corpora tables_re corpname
    corpora=$1
    tables_re=$2
    for corpname in $corpora; do
        install_db $corpname "$tables_re"
    done
}

install_corpora () {
    local pkglistfile corpname pkghost pkgfile pkgtime pkgsize corpora \
          tables_re order
    if [ "x$corpora_to_install" != x ]; then
        pkglistfile=$1
        echo
        echo "Installing Korp corpora$dry_run_msg:"
        for corpname in $corpora_to_install; do
            echo "  $corpname"
        done
        corpora=
        while read corpname pkghost pkgfile pkgtime pkgsize; do
            install_corpus $corpname "$pkgfile" $pkgtime $pkgsize $pkghost
            corpora="$corpora $corpname"
        done < $pkglistfile
    fi
    if [ "x$install_only_dbfiles_corpora" != x ] ||
           [ "x$install_dbfiles" != x ];
    then
	echo
	echo "Installing database files$dry_run_msg"
        if [ "x$dry_run" != x ]; then
            # If dry run, showing tables ".*" last would also show
            # those matching the other table patterns in
            # $dbtable_install_order, as they are not actually
            # installed, so show all tables at once, even though the
            # order is different than the actual installation order
            order=".*"
        else
            order=$dbtable_install_order
        fi
        install_corpora_dbtables install_corpora_db "$corpora" "$order"
    fi
    echo
    echo "Installation complete$dry_run_msg"
}

main () {
    timestamp
    echo Searching for corpus packages to install
    find_package_candidates $pkglistfile.base "$@"
    if [ ! -s $pkglistfile.base ]; then
        error "No matching corpus packages found"
    fi
    # The following two cannot be in a pipeline, because the former
    # constructs the value of the variable corpora_to_install that the
    # latter uses
    filter_corpora $pkglistfile.base > $pkglistfile
    if [ "x$corpora_to_install" = x ] &&
           [ "x$install_only_dbfiles_corpora" = x ];
    then
        error "No corpora to install"
    fi
    install_corpora $pkglistfile
    timestamp
}


time main "$@"
