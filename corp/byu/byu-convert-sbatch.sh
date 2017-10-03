#! /bin/bash

progname=$(basename $0)
progdir=$(dirname $0)

scriptdir=$progdir/../../scripts

usage_header="Usage: $progname [options] wlp_input.txt ...

Submit a SLURM batch job to convert BYU corpora from WLP to VRT."

action=sbatch

optspecs='
n|dry-run { action=cat }
l|log-dir=DIR "."
timelimit=MINS "10"
memory=MB "1000"
output-dir=DIR
metadata-file=FILE
v|verbose
'

. $scriptdir/korp-lib.sh

# Process options
eval "$optinfo_opt_handler"


if [ $action = sbatch ] && ! find_prog sbatch > /dev/null; then
    error "Please run in a system with SLURM installed."
fi


for file in "$@"; do
    jobname_base="$(basename $file .txt)"
    jobname="byu_$jobname_base"
    if [ -e "$file.vrt" ]; then
	echo "Skipping $file: $file.vrt already exists"
	continue
    fi
    if [ "x$output_dir" != x ]; then
	outfile=$output_dir/$jobname_base.txt.vrt
    else
	outfile=$file.vrt
    fi

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
#SBATCH -o $log_dir/byu_log-$jobname_base-%j.out
#SBATCH -e $log_dir/byu_log-$jobname_base-%j.err
#SBATCH -t $timelimit
#SBATCH --mem-per-cpu $memory
#SBATCH -n 1
#SBATCH -p serial

. $scriptdir/korp-lib.sh

echo Job: \$SLURM_JOB_ID \$SLURM_JOB_NAME
echo Input: "$file"
$progdir/byu-convert.sh --metadata-file "$metadata_file" --verbose \
    "$file" > "$outfile"
EOF

done
