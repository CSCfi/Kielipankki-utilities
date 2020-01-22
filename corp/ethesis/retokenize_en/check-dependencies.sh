#!/bin/sh

# - newer gradut package contains dir matemaattis with 577 files
# - newer gradut package contains 1203 more files
# - older gradut package contains one file that is not in newer package: teologinen/tuhoa.zip
# - both packages contain "Hot Folder Log.txt", category.txt and logfile.txt files
# - gradutiivistelmat is not in IDA in txt format? 2016 files in package

# "You do not have the credentials to access the restricted item hdl:10138/165906. The selected item is withdrawn and is no longer available."

if !(ls venv-parser-neural/bin/activate > /dev/null 2> /dev/null); then
    echo "venv-parser-neural/bin/activate not found in the current directory";
    exit 1;
fi

if !(ls lang_recognizer.py > /dev/null 2> /dev/null); then
    echo "lang_recognizer.py not found in the current directory";
    exit 1;
fi

for packagedir in E-thesis_gradut_TXT_2016-11-22 E-thesis_vaitokset_TXT_2016-10-17 E-thesis_other_langs_VRT_2016-11-22;
do
    if !(ls $packagedir > /dev/null 2> /dev/null); then
	echo "Package directory "$packagedir" not found in the current directory";
	exit 1;
    fi
done

for script in renumber-sentences.pl add-missing-tags.pl split-conllu-files.pl; # msd-bar-to-space.pl;
do
    if !(ls $script > /dev/null 2> /dev/null); then
	echo "Script "$script" not found in the current directory";
	exit 1;
    fi
done

vrttooldir=""
for arg in $@;
do
    if [ "$arg" = "--vrt-tool-dir" ]; then
	vrttooldir="<next>";
    else
	if [ "$vrttooldir" = "<next>" ]; then
	    vrttooldir=$arg"/";
	fi
    fi
done

for tool in vrt-keep vrt-rename;
do
    if !(which $vrttooldir$tool > /dev/null 2> /dev/null); then
	echo "Tool "$vrttooldir$tool" not found (path can be given with --vrt-tool-dir PATH)";
	exit 1;
    fi
done
