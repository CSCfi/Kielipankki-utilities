# -*- coding: utf-8 -*-

# shlib/sys.sh
#
# Generic library functions for Bourne shell scripts: system
# information


# Load shlib components for the definitions used
shlib_required_libs="str"
. $_shlibdir/loadlibs.sh


# Functions


# get_num_cpus
#
# Output the number of CPUs (cores)
get_num_cpus () {
    nth_arg 2 $(lscpu | grep '^CPU(s):')
}

# get_cpu_load
#
# Output system CPU load average for the past minute
get_cpu_load () {
    local ut
    ut=$(LC_ALL=C uptime)
    ut=${ut#*average:}
    echo ${ut%%,*}
}
