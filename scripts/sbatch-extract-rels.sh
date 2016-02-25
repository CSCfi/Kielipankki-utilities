#! /bin/bash

progname=$(basename $0)
progdir=$(dirname $0)

shortopts="hnc:f:r:i:o:l:t:v"
longopts="help,dry-run,corpus-name:,input-fields:,relation-map:,input:,output-dir:,log-dir:,token-count:,timelimit:,memory:,timelimit-factor:,memory-factor:,verbose"

corpus_name=
input_fields=
relation_map=
input=
output_dir=.
log_dir=.
action=sbatch
verbose=
token_count=
timelimit=
memory=
timelimit_factor=100
memory_factor=100
default_token_count=10M

. $progdir/korp-lib.sh


usage () {
    cat <<EOF
Usage: $progname [options]

Subtmit a SLURM batch job to extract dependency relations for the Korp
word picture.

Options:
  -h, --help
  -n, --dry-run
  -c, --corpus-name CORPUS
  -f, --input-fields FIELDLIST
  -r, --relation-map FILE
  -i, --input FILESPEC
  -o, --output-dir DIR
  -l, --log-dir DIR
  -t, --token-count NUM
  --timelimit MINS
  --memory MB
  --timelimit-factor PERCENTAGE
  --memory-factor PERCENTAGE
  -v, --verbose
EOF
    exit 0
}

# Process options
while [ "x$1" != "x" ] ; do
    case "$1" in
	-h | --help )
	    usage
	    ;;
	-n | --dry-run )
	    action=cat
	    ;;
	-c | --corpus-name )
	    corpus_name=$2
	    shift
	    ;;
	-f | --input-fields )
	    input_fields=$2
	    shift
	    ;;
	-r | --relation-map )
	    relation_map=$2
	    shift
	    ;;
	-i | --input )
	    input=$2
	    shift
	    ;;
	-o | --output-dir )
	    output_dir=$2
	    shift
	    ;;
	-l | --log-dir )
	    log_dir=$2
	    shift
	    ;;
	-t | --token-count )
	    token_count=$2
	    shift
	    ;;
	--timelimit )
	    timelimit=$2
	    shift
	    ;;
	--memory )
	    memory=$2
	    shift
	    ;;
	--timelimit-factor )
	    timelimit_factor=$2
	    shift
	    ;;
	--memory-factor )
	    memory_factor=$2
	    shift
	    ;;
	-v | --verbose )
	    verbose=1
	    ;;
	-- )
	    shift
	    break
	    ;;
	--* )
	    warn "Unrecognized option: $1"
	    ;;
	* )
	    break
	    ;;
    esac
    shift
done


if [ $action = sbatch ] && ! find_prog sbatch > /dev/null; then
    error "Please run in a system with SLURM installed."
fi

if [ "x$corpus_name" = x ]; then
    error "Please specify corpus name with --corpus-name"
fi
if [ "x$input_fields" = x ]; then
    error "Please specify input field names with --input-fields"
fi
if [ "x$relation_map" = x ]; then
    error "Please specify relation map file with --relation-map"
fi

if [ -e "$output_dir/${corpus_name}_rels.tar" ]; then
    error "Output file $output_dir/${corpus_name}_rels.tar already exists"
fi

if [ "x$timelimit" = x ] || [ "x$memory" = x ]; then
    if [ "x$token_count" = x ]; then
	if [ "x$input" != x ]; then
	    if [ -d "$input" ]; then
		for ext in vrt vrt.gz vrt.bz2 vrt.xz; do
		    files=$(ls $input/*.$ext 2> /dev/null)
		    if [ "x$files" != x ]; then
			input="$files"
			break
		    fi
		done
	    fi
	    token_count=$(
		comprcat --tar-args "--wildcards *.vrt" $input |
		grep -cv '^<'
	    )
	else
	    token_count=$default_token_count
	fi
    fi
    case $token_count in
	*[kK] )
	    multiplier=1000
	    ;;
	*[mM] )
	    multiplier=1000000
	    ;;
	*[gG] )
	    multiplier=1000000000
	    ;;
	* )
	    multiplier=1
	    ;;
    esac
    if [ $multiplier != 1 ]; then
	token_count_base=${token_count%[kKmMgG]}
	token_count=$(($token_count_base * $multiplier))
    fi
    if [ "x$timelimit" = x ]; then
	timelimit=$((($token_count / 500000 + 1) * $timelimit_factor / 100))
    fi
    test $timelimit -lt 1 && timelimit=1
    if [ "x$memory" = x ]; then
	memory=$((($token_count / 1000) * $memory_factor / 100))
    fi
    test $memory -lt 32 && memory=32
    test $memory -gt 128000 && memory=128000
fi

if [ "x$verbose" != x ]; then
    cat <<EOF
Submitting job "extrels_$corpus_name" to partition "serial"
Tokens: $token_count
Max run time: $timelimit mins
RAM per CPU: $memory MiB
EOF
fi

$action <<EOF
#! /bin/bash -l
#SBATCH -J extrels_$corpus_name
#SBATCH -o $log_dir/extrels_log-${corpus_name}-%j.out
#SBATCH -e $log_dir/extrels_log-${corpus_name}-%j.err
#SBATCH -t $timelimit
#SBATCH --mem-per-cpu $memory
#SBATCH -n 1
#SBATCH -p serial

. $progdir/korp-lib.sh

echo Job: \$SLURM_JOB_ID \$SLURM_JOB_NAME
echo Input: $input
comprcat $input |
$progdir/run-extract-rels.sh --corpus-name $corpus_name \
    --input-fields "$input_fields" --relation-map "$relation_map" \
    --output-dir "$output_dir" --optimize-memory --verbose
EOF
