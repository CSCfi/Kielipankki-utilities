
# Post-processing the Oracc 2024 VRT data

This document describes the post-processing of the Oracc 2024 VRT data
for importing into Korp.

The data was post-processed by Jyrki Niemi on Puhti between 2025-06-09
and 2025-09-12.


## Input VRT

The input VRT files had been produced by Aleksi Sahala from Oracc JSON
data as of 2024-11. Each VRT file corresponded to one Oracc project
and one Korp subcorpus. These VRT files were then processed further by
Heidi Jauhiainen as follows:

- Replaced the value `_` with the empty string `text` attribute
  `primarypub`.

- Removed trailing spaces from the values of the `text` attributes
  `primarypub` and `excavation` (25 occurrences in total).

- Replaced an occurrence of a double space with a `+` surrounded by
  spaces in the `text` attribute `accessionno` of subcorpus RIBo.

- Removed duplicate texts in subcorpus EPSD2. Duplicates were
  identified by the `text` attribute `cdlinumber`.

- Removed from subcorpus SAAo texts also occurring in subcorpus EPSD2.


## Post-processing VRT


### Environment

- Post-processing was done under directory
  `/scratch/clarin/tmp/oracc-2024` on Puhti.

- The subdirectory `00-input` contained the intermediate VRT files
  that had been processed as described above.

- The output of each step was stored in a separate subdirectory whose
  name began was of the form _nn_`-`_name_, where _nn_ is a two-digit
  step number and _name_ a short descriptive name of the step.


### Notes

- The post-processing steps described below are represented by Bash
  command lines on Puhti.

- The steps have been documented afterwards, based on Bash
  command-line history, so they may contain errors.

- In many cases, a step required several iterations to get it work
  correctly. The command lines below should represent the final,
  working ones.

- The order of the steps is probably not the most logical. Some steps
  could also have been avoided if some previous one had been done more
  properly.

- Some of the Bash command lines have been slightly edited. In
  particular, many of them have been divided into multiple lines.

- The variable `tab` represents a tab character, set as follows:
  ```bash
  tab="$(printf "\t")"
  ```

- Many steps use the [GNU
  Parallel](https://www.gnu.org/software/parallel/) tool for starting
  multiple processes to process input files in parallel. The actual
  processing command is specified as a single string argument, which
  may make argument quoting within the command line somewhat more
  complicated.

- Many of the steps follow a similar pattern, which could perhaps be
  made a wrapper script.

- Some VRT tools used in the steps were (and some still are)
  development versions with features not yet in the `master` branch of
  Kielipankki-utilities (this repository). In particular, the version
  of the tool `vrt-add-struct-attrs` was that in branch
  `dev-vrt-update-attrs` is referred to as `$vt/vrt-add-struct-attrs`
  in the commands below. The tool was later renamed to
  `vrt-update-attrs`.


### Post-processing steps

1. Try to find `_geo_provenience` attributes with incorrect coordinates.

    - Latitude greater than or equal to 40 and the difference between
      latitude and longitude greater than or equal to 4:

        ```bash
        grep -o '_geo_provenience="[^"]*"' 00-input/*.vrt |
            grep ';' |
            grep -v '0;0' |
            cut -d= -f2 |
            tr -d '|"' |
            sort -u |
            awk -F';' '$3 >= 41 && $3 - $4 >= 3'
        ```

    - More tightly constrained (see the comments in the Awk code):

        ```bash
        grep -o '_geo_provenience="[^"]*"' 00-input/*.vrt |
            grep ';' |
            grep -v '0;0' |
            cut -d= -f2 |
            tr -d '"' |
            sort -u |
            awk -F';' '
            {
                if ($1 == prevname) {
                    if (int($3) == prevlng && int($4) == prevlat) {
                        # Same place name with longitude and latitude
                        # swapped -> very likely one is incorrect
                        printf "><"
                    } else if (int($3) == prevlat && int($4) == prevlng) {
                        # Same place name with a small difference in
                        # coordinates
                        printf "~"
                    } else {
                        # Completely different coordinates
                        printf "??"
                    }
                    print "\t" prev;
                    print "\t" $0;
                }
                prev = $0;
                prevname = $1;
                prevlat = int($3);
                prevlng = int($4)
            }'
        ```

2. Replace some provenience names.

   Replacements were originally in file
   `korvaukset-oracc-korp-2024.txt` provided by Aleksi Sahala, with
   the original and replacement values separated by a semicolon.

   Convert the file to TSV:

    ```bash
    tr ';' '\t' < korvaukset-oracc-korp-2024.txt > korvaukset-oracc-korp-2024.tsv
    ```

    Actually replace the values in `text` attributes `provenience` and
    `_geo_provenience`:

    ```bash
    parallel -j8 "
        $vt/vrt-add-struct-attrs --data korvaukset-oracc-korp-2024.tsv --attr provenience,provenience2 --key provenience --compute provenience='attr[\"provenience2\"] or val' --compute _geo_provenience='if val and attr[\"provenience2\"]: val = attr[\"provenience2\"] + \";\" + val.partition(\";\")[2]' {} 2> 01-repl-provenience/{/.}.err |
        vrt-drop-attrs --structure text --drop provenience2 > 01-repl-provenience/{/}" \
        ::: 00-src/*.vrt
    ```

3. Replace some coordinates (`text` attribute `_geo_provenience`)
   based on the replacements file `koordinaatit-oracc-korp-2024.txt`
   provided by Aleksi Sahala.

    Convert the file to TSV, with the place name as the first field:

    ```bash
    awk -F';' '{print $1 "\t" $0}' koordinaatit-oracc-korp-2024.txt > koordinaatit-oracc-korp-2024.tsv
    ```

    Replace the `_geo_provenience` values:

    ```bash
    parallel -j8 "
        $vt/vrt-add-struct-attrs --data koordinaatit-oracc-korp-2024.tsv --attr provenience,_geo_provenience --key provenience --overwrite _geo_provenience {} 2> 02-repl-geo_provenience/{/.}.err > 02-repl-geo_provenience/{/}" \
        ::: 01-repl-provenience/*.vrt
    ```

4. Replace `text` attribute `_geo_provenience` values having
   coordinates (0, 0) with an empty string:

    ```bash
    parallel -j8 "
        $vt/vrt-add-struct-attrs --compute _geo_provenience='if val.endswith(\";0;0\"): val = \"\"' {} > 03-empty-geo-0-0/{/}" \
        ::: 02-repl-geo_provenience/*.vrt
    ```

5. Make `text` attribute `_geo_provenience` values feature sets
   (enclose in `|`, empty value as a single `|`):

    ```bash
    parallel -j12 "
        $vt/vrt-add-struct-attrs --compute _geo_provenience='f\"|{val}|\" if val else \"|\"' {} > 04-geo-set/{/}" \
        ::: 03-empty-geo-0-0/*.vrt
    ```

6. Add `positional-attributes` comments:

    First, extract attribute names from the file `notes.txt` and
    create a file containing the comment line:

    ```bash
    grep -v '^#' 00-src/notes.txt |
        tr -d '\r' |
        tr '\n' ' ' |
        perl -ne 'print "<!-- #vrt positional-attributes: $_-->\n"' > oracc2024-posattrs.txt
    ```

    Then, add the comment line to VRT files:

    ```bash
    for f in 01-geo-set/*.vrt; do
        {
            cat oracc2024-posattrs.txt
            cat $f
        } > 05-add-pos-attr-comment/$(basename $f)
    done
    ```

7. Fix some `text` attribute `_geo_provenience` values.

   - Replace _Tel Billa_ with _Tell Billa_ in subcorpus ATAE:

       ```bash
       perl -pe 'if (/^<text/) { s/Tel Billa/Tell Billa/g }' \
           05-add-pos-attr-comment/oracc2024_atae.vrt > 06-fix-geo-2/oracc2024_atae.vrt
       ```

   -  Fix some `text` attribute `provenience` and `_geo_provenience`
      values in subcorpora RINAP, DCCLT and eCUT. (The files
      `korvaukset-oracc-korp-2024.tsv` and
      `koordinaatit-oracc-korp-2024.tsv` were amended to fix a couple of
      additional values.)

       ```bash
       parallel -j8 "
           $vt/vrt-add-struct-attrs --data korvaukset-oracc-korp-2024.tsv --attr provenience,provenience2 --key provenience --compute provenience='attr[\"provenience2\"] or val' --compute _geo_provenience='if val and attr[\"provenience2\"]: val = \"|\" + attr[\"provenience2\"] + \";\" + val.strip(\"|\").partition(\";\")[2] + \"|\"' {} 2> 06-fix-geo-2/{/.}.err1 |
           vrt-drop-attrs --structure text --drop provenience2 |
           $vt/vrt-add-struct-attrs --data koordinaatit-oracc-korp-2024.tsv --attr provenience,_geo_provenience --key provenience --overwrite _geo_provenience --compute _geo_provenience='if len(val) > 1 and val[0] != \"|\": val = f\"|{val}|\"' 2> 06-fix-geo-2/{/.}.err2 > 06-fix-geo-2/{/}" \
           ::: 05-add-pos-attr-comment/oracc2024_{rinap,dcclt,ecut}.vrt
       ```

8. Another fix to provenience attribute values in subcorpus DCCLT:

    ```bash
    parallel -j8 "
        $vt/vrt-add-struct-attrs --data korvaukset-oracc-korp-2024.tsv --attr provenience,provenience2 --key provenience --compute provenience='attr[\"provenience2\"] or val' --compute _geo_provenience='if val and attr[\"provenience2\"]: val = \"|\" + attr[\"provenience2\"] + \";\" + val.strip(\"|\").partition(\";\")[2] + \"|\"' {} 2> 07-fix-geo-3/{/.}.err1 |
        vrt-drop-attrs --structure text --drop provenience2 |
        $vt/vrt-add-struct-attrs --data koordinaatit-oracc-korp-2024.tsv --attr provenience,_geo_provenience --key provenience --overwrite _geo_provenience --compute _geo_provenience='if len(val) > 1 and val[0] != \"|\": val = f\"|{val}|\"' 2> 07-fix-geo-3/{/.}.err2 > 07-fix-geo-3/{/}" \
        ::: 06-fix-geo-2/oracc2024_dcclt.vrt
    ```

9. Two further fixes to `_geo_provenience` coordinates in subcorpus
    RINAP.

    Create a coordinate fix file with the `_geo_provenience` value as
    a feature set value:

    ```bash
    awk -F“$tab” '{print $1 "\t|" $2 "|"}' koordinaatit-oracc-korp-2024.tsv > koordinaatit-oracc-korp-2024-set.tsv
    ```

    Actually apply the fixes:

    ```bash
    parallel -j8 "
        $vt/vrt-add-struct-attrs --data koordinaatit-oracc-korp-2024-set.tsv --attr provenience,_geo_provenience --key provenience --overwrite _geo_provenience {} 2> 07-fix-geo-3/{/.}.err > 07-fix-geo-3/{/}" \
        ::: 06-fix-geo-2/oracc2024_rinap.vrt
    ```

10. Fix the values of `pos` and `oraccpos` in subcorpus EPSD2 to be
   consistent both within the subcorpus and with other subcorpora.

    In `pos`, replace tags of type _XX_ with a fully written part of
    speech, and in `oraccpos`, replace tags of type _XX XX_ with _XX
    explanation_. The replacement mappings were in TSV files
    `oracc2024_epsd2-fix-pos-map.tsv` and
    `oracc2024_epsd2-fix-oraccpos-map.tsv`, respectively.

    ```bash
    $vt/vrt-update-attrs --positional --data oracc2024_epsd2-fix-pos-map.tsv --attr "pos,pos2" --key pos --rename pos2:pos 05-add-pos-attr-comment/oracc2024_epsd2.vrt |
        $vt/vrt-update-attrs --positional --data oracc2024_epsd2-fix-oraccpos-map.tsv --attr oraccpos,oraccpos2 --key oraccpos --rename oraccpos2:oraccpos > 08-fix-pos-epsd2/oracc2024_epsd2.vrt
    ```

11. Fix `&` to be encoded correctly as `&amp;`, not as `&amp;amp;` in
   several subpcorpora:

    ```bash
    grep -lE '^[^<].*&amp;(lt|gt|quot|amp|apos);' 08-fix-pos-epsd2/*.vrt |
        parallel -j4 "
            $vt/vrt-update-attrs --positional --compute autolemma='s/&amp;amp;/&amp;/g' --compute autopos='s/&amp;amp;/&amp;/g' {} > 09-fix-autolemma-autopos-amps/{/}"
    ```

    This assumes that the directory `08-fix-pos-epsd2` contains the
    latest (fixed) VRT files for all subcorpora (or symlinks to them).


# Create Korp corpus packages with `korp-make`

The following assumes that the directory
`09-fix-autolemma-autopos-amps` contains the final VRT files of each
subcorpus (or symlinks to them).

```bash
parallel -v 'game --job korp-make-{/.} --GiB 4 --min 20 -C1 --scratch 40 korp-make --times --force --config-file oracc2024_korp-make.conf {/.} {}' ::: 09-fix-autolemma-autopos-amps/*.vrt
```

The content of `oracc2024_korp-make.conf` was as follows:

```
add-lemgrams-without-diacritics = 1
add-lowercase-lemgrams = 1
no-lemmas-without-boundaries = 1
lemgram-posmap = oracc2024_lemgram_posmap.tsv
```

This uses the [`game`](../../vrt-tools/game) tool for starting a SLURM
batch job. The time and memory requirements specified with `game`
options should be large enough for the largest subcorpus.
