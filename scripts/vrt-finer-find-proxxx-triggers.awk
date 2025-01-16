#! /usr/bin/awk -f

# vrt-finer-find-proxxx-triggers.awk
#
# Usage: vrt-finer-find-proxxx-triggers.awk token [input.vrt ...]
#
# Try to find in VRT input such expressions that appear to make the
# following occurrences of the specified token be recognized as
# product names (tagged as EnamexProXxx-F by vrt-finnish-nertag). The
# triggering expression is assumed to contain the token (possibly with
# a suffix) within ExnamexProXxx.
#
# The first argument is the token to be checked (with possible Awk
# regular expression metacharacters protected) and the rest are the
# input VRT files. If no input files are specified, read from stdin.
#
# The first four positional attributes in the VRT input should be word
# form, maximal NER tag, set of NER tags, NER BIO tag. The input VRT
# also must contain <ne> structures added with vrt-augment-name-attrs.
#
# The output is of the form:
#
# ------------------------------------------------------------
#   211635 non-name: 68 ... 6244357
#
# 6244409 ,       EnamexProXxx-B  |EnamexProXxx-B-0|      B-PRO
# 6244410 -laivalla       EnamexProXxx-E  |EnamexProXxx-E-0|      I-PRO
#
#   6293 EnamexProXxx-F: 6244433 ... 6445306
#   30638 non-name: 6445327 ... 7296483
#
# ...
#
# Total 1648002:
#    1626525 non-name
#      21399 EnamexProXxx-F
#         78 other
# ------------------------------------------------------------
#
# The indented lines "N TYPE: A ... B" indicate that the input had N
# occurrences of token of TYPE between input lines A and B, where TYPE
# is either "non-name" (not tagged as a name) or "EnamexProXxx-F"
# (tagged as a single-word product name).
#
# The non-indented lines are input lines containing an assumed
# triggering expression (EnamexProXxx including token), prefixed with
# input line numbers (followed by tabs). If no triggering expression
# was detected, "No triggering expression found" is output instead. If
# an expected triggering expression did not trigger EnamexProXxx-F,
# these lines are preceded by line "Non-triggering expression:".
#
# The end of input contains the total number of the given tokens, and
# the number of them that are non-name, EnamexProXxx-F and others
# (occurring within a multi-word name or tagged as some other type of
# name than EnamexProXxx).


BEGIN {
    # The first argument is the token to be tested
    token = ARGV[1]
    ARGV[1] = ""
    # Any line with token as the word form
    any_re = "^" token "\t"
    # token as a single-word product name
    proxxx_re = "^" token "\tEnamexProXxx-F"
    # token outside names
    noname_re = "^" token "\t_\t\\|\tO"
    # Triggering construct is assumed to start with token, possibly
    # followed by a suffix
    trigger_re = "^" token ".*\t"
    # Lines of the current NE expression
    ne = ""
    # Saved possible triggering construct (NE)
    saved_ne = ""
    # Whether to save the current NE expression
    save_ne = 0
    # Whether currently within a NE expression
    within_ne = 0
    # Look for EnamexProXxx-F token
    PROXXX = 1
    # Look for non-name token
    NONAME = 2
    # Whether to look for a EnamexProXxx-F or non-name token
    look_for = PROXXX
    # Number of the current kind (EnamexProXxx-F or non-name) of
    # tokens
    count = 0
    # The first token of the current kind
    first = 0
    # The last token of the current kind
    last = 0
    # Total number of tokens
    total = 0
    # Total number of tokens marked as EnamexProXxx-F
    total_proxxx = 0
    # Total number of non-name tokens
    total_noname = 0
}

# Print count information from the current token span. Argument type
# is either "non-name" or "EnamexProXxx-F".
function print_count (type) {
    if (count) {
        print "  " count " " type ": " first " ... " last
    }
}

# Any type of token
$0 ~ any_re {
    total++
}

# Beginning of a product NE when looking for EnamexProXxx-F
! within_ne && look_for == PROXXX && /^<ne .* fulltype="EnamexProXxx"/ {
    within_ne = 1
    ne = ""
    save_ne = 0
    next
}

# Nested NE expression
within_ne && /^<ne / {
    within_ne++
}

# Closing a NE expression
within_ne && /^<\/ne/ {
    within_ne--
    if (within_ne == 0 && save_ne) {
        saved_ne = ne
    }
}

# Within a NE expression
within_ne {
    ne = (ne ? ne "\n" : "") NR "\t" $0
    # If matches a triggering construct, mark to be saved
    if ($0 ~ trigger_re && $0 !~ proxxx_re) {
        save_ne = 1
    }
}

# EnamexProXxx-F token
$0 ~ proxxx_re {
    if (look_for == PROXXX) {
        # If looking for this, print and reset counts, print the
        # possible triggering construct and begin looking for non-name
        # tokens
        print_count("non-name")
        if (count) {
            print ""
        }
        print (saved_ne ? saved_ne : "No triggering expression found")
        # print "--\n" NR "\t" $0 "\n"
        print ""
        look_for = NONAME
        saved_ne = ""
        count = 1
        first = last = NR
    } else {
        # Otherwise, increment the number of EnamexProXxx-F tokens
        count++
        last = NR
    }
    total_proxxx++
}

# Non-name token
$0 ~ noname_re {
    if (look_for == NONAME) {
        # If looking for this, print and reset counts and begin
        # looking for EnamexProXxx-F tokens
        print_count("EnamexProXxx-F")
        look_for = PROXXX
        count = 1
        first = last = NR
    } else {
        # Otherwise, increment the number of non-name tokens
        if (count == 0) {
            first = NR
        }
        count++
        last = NR
        if (saved_ne) {
            # The previous saved NE did not trigger EnamexProXxx-F
            print "Non-triggering expression:"
            print saved_ne
            saved_ne = ""
        }
    }
    total_noname++
}

END {
    # Print current counts and totals
    type = (look_for == PROXXX ? "non-name" : "EnamexProXxx-F")
    print_count(type)
    print "\nTotal " total ":"
    printf "  %8d non-name\n", total_noname
    printf "  %8d EnamexProXxx-F\n", total_proxxx
    printf "  %8d other\n", total - total_noname - total_proxxx
}
