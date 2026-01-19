
# Processing BALT 2025-02 data for Korp

## Resource information

- *Resource name*: BALT: Babylonian Administrative and Legal Texts –
  Kielipankki version 2025-02
- *Resource short name*: balt-2025-02-korp
- *Persistent identifier*: https://urn.fi/urn:nbn:fi:lb-2025022201

## Initial VRT format

The BALT 2025-02 corpus data had been converted to an initial VRT
format, one file per subcorpus, by Aleksi Sahala. This original VRT
data is [in IDA](https://ida.fairdata.fi/f/89120883).

The VRT data was then post-processed in several steps on Puhti in
February–March 2025 by Jyrki Niemi, with feedback from Tero Alstola.

## Post-processing VRT

The following post-processing steps are Bash command lines on Puhti.

Note that the steps have been documented afterwards, based on Bash
command-line history.

1. Add a positional-attributes comment:
   ```bash
   for f in *.vrt; do vrt-name -b.bak01 --map "$(echo "word lemma translation sense transcription pos oraccpos normname lang msd autolemma autopos url" | tr ' ' '\n' | awk '{print "v" NR "=" $0}' | tr '\n' ' ')" $f; done
   ```

2. Remove `text` attribute `url` (value always `_`):
   ```bash
   for f in *.vrt; do vrt-drop --backup .bak02 -f url $f; done
   ```

3. Convert text `_geo_provenience` attributes values to feature sets:
   ```bash
   perl -i.bak03 -pe 'if (/^<text/) { s/(_geo_provenience=")(.*?)"/$1|$2|"/; s/\|_\|/|/ }' *.vrt
   ```

4. Remove leading and trailing spaces from `text` attributes
   `museumno` and `subgenre`:
   ```bash
   perl -i.bak04 -pe 'if (/^<text/) { s/(museumno|subgenre)="\s*(.*?)\s*"/$1="$2"/g; }' *.vrt
   ```

5. Remove sentence translation attribute:
   ```bash
   time for f in *.vrt; do vrt-drop-attrs --backup .bak05 --structure sentence --drop translation $f; done
   ```

6. Convert CR+LF newlines to LF:
   ```bash
   for f in *.vrt; do mv $f{,.bak06}; tr -d '\r' < $f.bak06 > $f; done
   ```

7. Convert missing text `cdlilink` attribute values from underscore to
   empty string:
   ```bash
   perl -i.bak07 -pe 'if (/^<text.*/) { s/( cdlilink=")_"/$1"/ }' *.vrt
   ```

8. Convert `_geo_provenience` values `|undefined;XX;0;0|` to `|`:
   ```bash
   perl -i.bak08 -pe 'if (/^<text.*/) { s/( _geo_provenience="\|)undefined;XX;0;0\|"/$1"/ }' *.vrt
   ```

9. Convert all the rest of text attribute values with a single
   underscore to empty string:
   ```bash
   perl -i.bak09 -pe 'if (/^<text/) { s/="_"/=""/g }' *.vrt
   ```

10. Remove the first text with `cdlinumber` value `P371439` from
    subcorpus Everling.
    ```bash
    perl -i.bak10 -ne 'if ((! $dropped) && /^<text cdlinumber="P371439"/) { $dropping = 1; next } elsif ($dropping) { if (/^<\/text>/) { $dropping = 0; $dropped = 1 } } else { print }' balt_everling.vrt
    ```
11. Change the `primarypub` attribute value of the first text with
    `cdlinumber` value `P527436` in subcorpus Hack, Jursa & Schmidl:
    ```bash
    perl -i.bak11 -pe 'if ((! $changed) && /^<text cdlinumber="P527436"/) { s/( primarypub=").*?"/$1Hackl, Jursa &amp; Schmidl, AOAT 414\/1, 166"/; $changed = 1 }' balt_hackl_jursa_privatbriefe.vrt
    ```

12. Copy the attributes of text `P551157` to texts `X101528` and
    `X101529`, adding a suffix to `primarypub` value in subcorpus
    Everling:
    ```bash
    perl -i.bak12 -pe 'if (/^<text/) { if (/ cdlinumber="P551157"/) { $saveline = $_ } elsif (/ cdlinumber="X10152([89])"/) { if ($1 eq "8") { $suff = "ii" } else { $suff = "iii" } $_ = $saveline; s/( primarypub=").*?"/$1Nbk 452_$suff"/ } }' balt_everling.vrt
    ```

13. Correct the positional attributes of the word form _min_ in
    subcorpus Everling:
    ```bash
    perl -i.bak13 -pe 'if (/^min\t/) { $_ = "min\t_\t_\t_\t_\tmiscunknown\tu unknown\t_\tAkkadian\t_\t_\tu\n" }' balt_everling.vrt
    ```

14. Rename the subcorpus VRT files to correspond to the subcorpus ids
    decided:
    ```bash
    mv balt_hackl_{jankovic_jursa,briefdossier}.vrt
    mv balt_hackl{_jursa,}_privatbriefe.vrt
    ```

## Creating CWB corpus

The CWB corpora were created with the
[`korp-make`](../../scripts/korp-make) script as follows:
```bash
for f in *.vrt; do korp-make --force --add-lemgrams-without-diacritics --add-lowercase-lemgrams --no-lemmas-without-boundaries --lemgram-posmap ../balt_lemgram_posmap.tsv $(basename $f .vrt) $f; done
```
