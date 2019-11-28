#!/bin/sh

element=""
prefix=""

if [ "$1" = "--paragraph" ]; then
    element="paragraph";
fi
if [ "$1" = "--sentence" ]; then
    element="sentence";
fi
if [ "$1" = "--link" ]; then
    element="link";
fi

prefix=$2;

num=`cat - | egrep '^<'${element}'' | wc -l`;
perl -e 'use List::Util qw(shuffle); @array = (1..'$num'); @array = shuffle(@array); for my $el (@array) { print "'$prefix'".$el."\n"; }';
