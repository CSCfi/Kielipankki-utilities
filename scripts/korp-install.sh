#! /bin/sh
# -*- coding: utf-8 -*-

# korp-install.sh
# 
# Install or update Korp components from Kielipankki's Korp Git repositories
# 
# Usage: korp-install.sh [options] component[:refspec] [target]
#
# For more information, run korp-install.sh --help
#
# TODO:
# - Modify backend files as appropriate (Python path, config values)
# - Produce (maybe optionally, or maybe when installing to the
#   production frontend) a compressed dist version of Korp frontend
#   and install it; requires Node.js (npm)
# - Check that Korp is not currently being run; possibly put a
#   temporary index.html displaying "Korp is being updated"
# - Multiple backups, maybe timestamped
# - Specify source Git remote other than origin
# - Use an existing (test) installation as a source
# - Support other "Korp components": annlab, corpimport, news
# - Support other than CSC's servers
#
# FIXME:
# - If the name of a (non-top) target is not in the excludes list for the
#   component, it is deleted from the backup the following time when the
#   upper-level component is installed


progname=$(basename $0)
progdir=$(dirname $0)

remote_git_repo_pattern=git@github.com:CSCfi/korp-%s.git
local_git_root=/v/korp/git
local_git_prefix=$local_git_root/korp-
backup_root=/v/korp/backup
log_file=/v/korp/log/korp-install.log

# FIXME: "test" might not make sense for other repositories than frontend
default_target=test
default_refspec=master

root_frontend=/var/www/html
root_backend=/v/korp/cgi-bin

rsync_opts="-uacR --omit-dir-times"

excludes_frontend='/*test*/ /*beta*/ /*download*/ /tmp*/ /old*/ /secure/ /fulltext/ /dma/'
excludes_backend='/korp-*/ /annlab/ /log/'


usage_header="Usage: $progname [options] component[:refspec] [target]

Install or update Korp components from Kielipankki's Korp Git repositories

Arguments:
  component       the Korp component to install: either \"frontend\" or
                  \"backend\"
  refspec         the refspec in Git repository to install; typically a
                  branch or tag name, but may also be relative to one, e.g.,
                  \"master~2\" for the commit two commits before \"master\"
                  (default: \"$default_refspec\")
  target          the target (subdirectory) of the component to which to
                  install the new version: if \"/\", install to the top
                  directory (main production version) (default: \"$default_target\")"

optspecs='
revert
  restore the backup copy of the component in target saved when the
  script was run last time
'

usage_footer="The script makes a backup copy of the current installation of component in
target. It can be restored later with the option --revert. Each target has
a backup copy of its own, but subsequent runs of the script overwrite the
backup copy.

Note: The script does not delete existing files in the target directory
even if they do not exist in the new version, to avoid deleting files added
bypassing the version control. If the new version omits some files in the
previous version, they will nevertheless be present in the installation
unless manually removed, which may cause problems in some cases."


. $progdir/korp-lib.sh


if [ ! -e $log_file ]; then
    touch $log_file
    ensure_perms $log_file
fi

log () {
    type=$1
    shift
    echo [$progname $$ $(whoami) $type @ $(date '+%Y-%m-%d %H:%M:%S')] "$@" \
	>> $log_file
}

# Log warnings and errors
warn_hook='log WARN "$msg"'
error_hook='log ERROR "$msg"'


log INFO Run: $0 "$@"

if [ $(get_host_env) != "korp" ]; then
    error "This script currently only works on korp.csc.fi and korp-test.csc.fi"
fi


# Process options
eval "$optinfo_opt_handler"


compspec=$1
target=$2

if [ "x$compspec" = x ]; then
    error "Please specify the Korp component to install.
For more information, run '$0 --help'."
fi

case $compspec in
    *:* )
	comp=$(echo "$compspec" | sed -e 's/:.*//')
	refspec=$(echo "$compspec" | sed -e 's/[^:]*://')
	;;
    * )
	comp=$compspec
	refspec=$default_refspec
	;;
esac

case $comp in
    frontend | backend )
	:
	;;
    * )
	error "Unknown Korp component: $comp"
	;;
esac

case $refspec in
    *^ | *~* )
	branch=$(echo $refspec | sed -e 's/\(\^\|~\).*//')
	;;
    * )
	branch=$refspec
	;;
esac

if [ "x$target" = x ]; then
    target=$default_target
fi
orig_target=$target
case $target in
    / )
	target=.
	;;
esac

case $comp in
    frontend )
	targetdir=$root_frontend
	;;
    backend )
	error "Installing Korp backend does not yet work"
	targetdir=$root_backend
	;;
esac
if [ "$target" != . ]; then
    targetdir=$targetdir/$target
fi


run_rsync () {
    src=$1
    dst=$2
    shift 2
    mkdir -p "$dst"
    (
	cd "$src" &> /dev/null &&
	{
	    fifo=/tmp/$progname.$$.rsync.fifo
	    mkfifo $fifo
	    grep -v 'failed to set times on' < $fifo >&2 &
	    rsync $rsync_opts "$@" . "$dst/" 2> $fifo
	    rm $fifo
	}
	ensure_perms "$dst"
    )
}

make_rsync_filter () {
    filter_type=$1
    shift
    for patt in "$@"; do
	echo --filter "${filter_type}_$patt"
    done
}

git_get () {
    _comp=$1
    _branch=$2
    _refspec=$3
    if [ "x$_refspec" = x ]; then
	_refspec=$_branch
    fi

    remote_git_repo=$(printf "$remote_git_repo_pattern" $_comp)
    local_git_repo="$local_git_prefix$_comp"

    # Ensure file permissions in the local working copy even when an
    # error occurs
    add_cleanup_funcs ensure_perms_cwd

    if [ ! -d $local_git_repo ]; then
	cd $local_git_root
	echo "Cloning Git repository for Korp $comp"
	git clone $remote_git_repo || error "Could not clone $remote_git_repo"
    fi

    echo "Updating the Korp $_comp repository working copy"
    cd $local_git_repo
    git remote update ||
    error "Could not update the repository from $remote_git_repo"
    git checkout $_branch || error "Could not checkout $_branch"
    git pull --force origin $_branch || {
	# If the pull failed because the local branch had diverged
	# from the remote, reset and force-fetch the remote to the
	# local. This apparently cannot be done with git pull alone.
	warn "Local branch $_branch was outdated; updating from the repository"
	git reset --hard HEAD &&
	    # You cannot fetch to the current branch, so change to
	    # another branch.
	    # FIXME: Do not assume any other branch is available.
	    git checkout $(git branch | grep -v '^\*' | head -1) &&
	    git fetch --force origin $_branch:$_branch &&
	    git checkout $_branch ||
		error "Could not pull origin/$_branch"
    }
    if [ "x$_refspec" != "x$_branch" ]; then
	git checkout $_refspec || error "Could not checkout $_refspec"
    fi
    rm_cleanup_funcs ensure_perms_cwd
    ensure_perms .
}

ensure_perms_cwd () {
    ensure_perms .
}

install_news () {
    git_get frontend news/master
    commit_sha1_full_news=$(git rev-parse HEAD)
    mkdir -p $root_frontend/$target/news/json
    run_rsync ${local_git_prefix}frontend/json/ \
	$root_frontend/$target/news/json/ \
	--filter 'protect /*' \
	--exclude '.git*'
    log INFO "Installed: news to $targetdir/news from frontend:news/master ($commit_sha1_full_news)"
}

install_frontend () {
    # TODO: Optionally minify and copy the dist version
    run_rsync $local_git_repo/app $root_frontend/$target \
	--filter 'protect /*' \
	--exclude '.git*'
    install_news
}

install_backend () {
    run_rsync $local_git_repo $root_backend/$target \
	$(make_rsync_filter protect $excludes_backend) \
	--exclude '.git*'
    # TODO: Modify Python path, config vars: first rsync to a
    # temporary dir, modify there, then rsync the modified files
    # to the destination
}

backup_frontend () {
    run_rsync $root_frontend/$target $backup_root/frontend/$target \
	--delete \
	$(make_rsync_filter exclude $excludes_frontend)
}

backup_backend () {
    run_rsync $root_backend/$target $backup_root/backend/$target \
	--delete \
	$(make_rsync_filter exclude $excludes_backend)
}

revert_frontend () {
    run_rsync $backup_root/frontend/$target $root_frontend/$target \
	$(make_rsync_filter exclude $excludes_frontend)
}

revert_backend () {
    run_rsync $backup_root/backend/$target $root_backend/$target \
	$(make_rsync_filter exclude $excludes_backend)
}

install () {
    git_get $comp $branch $refspec
    commit_sha1=$(git rev-parse --short HEAD)
    commit_sha1_full=$(git rev-parse HEAD)

    echo "Making a backup copy of the current Korp $comp in $targetdir"
    backup_$comp
    echo "Installing Korp $comp"
    install_$comp
    echo "
Installed Korp $comp to $targetdir from Git repository ref $refspec
(commit $commit_sha1).
The backup copy can be restored by running
$0 --revert $comp $orig_target"
    log INFO "Installed: $comp to $targetdir from $refspec ($commit_sha1_full)"
}

revert () {
    echo "Reverting Korp $comp in $targetdir to the previously saved version"
    revert_$comp
    echo "
Reverted Korp $comp in $targetdir"
}


if [ "x$revert" != x ]; then
    revert
else
    install
fi
