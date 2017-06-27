#! /bin/bash


# TODO:
# - Estimate the required time based on the size of the input. The
#   options specified in the configuration file also affect the run
#   time; could they also be taken into account?


progname=$(basename $0)
progdir=$(dirname $0)


usage_header="Usage: $progname [options] corpus input.vrt ...

Submit a SLURM batch job to run korp-make to make a Korp corpus package from
VRT input.

The options to korp-make need to be specified via --config-file."

action=sbatch

optspecs='
config-file=FILE
  read korp-make options from confinguration file FILE
n|dry-run { action=cat }
l|log-dir=DIR "."
timelimit=MINS "30"
memory=MB "2500"
v|verbose
'

. $progdir/korp-lib.sh

# Process options
eval "$optinfo_opt_handler"


if [ $action = sbatch ] && ! find_prog sbatch > /dev/null; then
    error "Please run in a system with SLURM installed."
fi

corpus=$1
shift

if [ "x$corpus" = x ]; then
    error "Please specify corpus id as the first argument"
fi

jobname_base="$corpus"
jobname="korp_make_$jobname_base"

if [ "x$verbose" != x ]; then
    cat <<EOF
Submitting job "$jobname" to partition "serial"
Max run time: $timelimit mins
RAM per CPU: $memory MiB
EOF
fi

$action <<EOF
#! /bin/bash -l
#SBATCH -J $jobname
#SBATCH -o $log_dir/$jobname-%j.out
#SBATCH -e $log_dir/$jobname-%j.err
#SBATCH -t $timelimit
#SBATCH --mem-per-cpu $memory
#SBATCH -n 1
#SBATCH -p serial

. $progdir/korp-lib.sh

echo Job: \$SLURM_JOB_ID \$SLURM_JOB_NAME
echo Input: $@
echo Start: \$(date '+%F %T%:z')
$progdir/korp-make --config-file "$config_file" --verbose --times $corpus $@
echo End: \$(date '+%F %T%:z')
EOF
