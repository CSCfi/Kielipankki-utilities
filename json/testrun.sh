#! /bin/bash

# ./vrt-to-json has interacting complications:
# - optional input and output files
# - optional splitting of output to many files
# - named or positional output of data lines
# - optional output of values as natural numbers
#
# This script exercises some of the possibilites.
# - script and input file can have paths
# - test output is left in work directory
# - test input best not be huge (or even big)
# - tested with ten Suomi24 text elements.

set -eu -o pipefail

badarg () {
    2>&1 echo "usage: $0 INFILE"
    2>&1 echo "where INFILE in *.vrt"
    2>&1 echo "(and best not too big)"
    exit 1
}

case $# in
    1) ;;
    *) badarg
esac

case "$1" in
    *.vrt) ;;
    *) badarg
esac

case "$0" in
    testrun.sh) DIR="." ;;
    ?*/testrun.sh) DIR="${0%/*}" ;;
    *) 2>&1 echo "testrun.sh does not recognize itself in '$0'"
       exit 1
esac

PROG="$DIR/vrt-to-json"

echo "In $PWD"
echo "exercising $PROG"
echo "with $1"
echo "creating ./roska.json"
echo "creating ./roska/."

echo help option
"$PROG" --help > /dev/null

echo file to stdout
"$PROG" "$1" > /dev/null

echo stdin to stdout
"$PROG" < "$1" > /dev/null

echo file to roska.json
"$PROG" -o roska.json "$1"
python3 -c "import json; json.load(open('roska.json'))"
echo "succesfully load roska.json"

echo file to roska/def.json
"$PROG" -o roska/def.json "$1"
python3 -c "import json; json.load(open('roska/def.json'))"
echo "succesfully load roska/def.json"

echo file to roska/pos.json
"$PROG" -p -o roska/pos.json "$1"
python3 -c "import json; json.load(open('roska/pos.json'))"
echo "succesfully load roska/pos.json"

echo file to roska/#/def.json
"$PROG" --limit=100 -o roska/#/def.json "$1"
for f in roska/?/def.json
do
    python3 -c "import json; json.load(open('$f'))"
    echo "succesfully load $f"
done

echo file to roska/#/pos.json
"$PROG" -p --limit=100 -o roska/#/pos.json "$1"
for f in roska/?/pos.json
do
    python3 -c "import json; json.load(open('$f'))"
    echo "succesfully load $f"
done

echo file to roska/many/def.json
"$PROG" --limit=100 -o roska/many/def.json "$1"
echo "not even attempting to load roska/many/def.json"

echo file to roska/many/pos.json
"$PROG" -p --limit=100 -o roska/many/pos.json "$1"
echo "not even attempting to load roska/many/pos.json"

echo file to roska/nats/def.json
"$PROG" --nat ref,pos --nat text:title,sent:id -o roska/nats/def.json "$1"
python3 -c "import json; json.load(open('roska/nats/def.json'))"
echo "succesfully load roska/nats/def.json"

echo file to roska/nats/pos.json
"$PROG" -p --nat ref,pos --nat text:title,sent:id -o roska/nats/pos.json "$1"
python3 -c "import json; json.load(open('roska/nats/pos.json'))"
echo "succesfully load roska/nats/pos.json"

echo "done exercising $PROG."
